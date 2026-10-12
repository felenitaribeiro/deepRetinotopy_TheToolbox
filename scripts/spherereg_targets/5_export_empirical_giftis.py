#!/usr/bin/env python
"""Export the re-expressed empirical maps as per-subject GIFTIs into
HCP/freesurfer/<sub>/surf/.

32k files carry the frame token (sphere.reg frame); native files need none:
  <sub>.empirical_<map>_<fit>-spherereg.<h>.32k_fs_LR.func.gii
  <sub>.empirical_<map>_<fit>.<h>.native.func.gii
  <sub>.myelinmap-spherereg.<h>.32k_fs_LR.func.gii
Maps: polarAngle, eccentricity, pRFsize (fit1/fit2/fit3) and R2 (fit1 only).
Usage: export_empirical_giftis.py [subjects...]   (default: all)
"""
import os, sys
import numpy as np
import nibabel as nib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import WORK, load_metric, reconstruct, VALID_THR

FSBASE = '/scratch/project_mnt/S0210/deepRetinotopy_TheToolbox/HCP/freesurfer'
subs = sys.argv[1:] or [s.strip() for s in open(f'{WORK}/subjects.txt') if s.strip()]
MAPNAME = {'pa': 'polarAngle', 'ecc': 'eccentricity', 'prf': 'pRFsize', 'r2': 'R2'}
STRUCT = {'lh': 'CortexLeft', 'rh': 'CortexRight'}


def write_map(path, data, name, hemi):
    d = nib.gifti.GiftiDataArray(np.asarray(data, dtype=np.float32),
                                 intent='NIFTI_INTENT_NONE', datatype='NIFTI_TYPE_FLOAT32')
    d.meta = nib.gifti.GiftiMetaData({'Name': name,
                                      'AnatomicalStructurePrimary': STRUCT[hemi]})
    img = nib.gifti.GiftiImage(darrays=[d])
    img.meta = nib.gifti.GiftiMetaData({'AnatomicalStructurePrimary': STRUCT[hemi]})
    nib.save(img, path)


for i, sub in enumerate(subs):
    outdir = f'{FSBASE}/{sub}/surf'
    g = f'{WORK}/gii/{sub}'
    for hemi in ['lh', 'rh']:
        m32 = load_metric(f'{g}/targets.{hemi}.32k_spherereg.func.gii')
        mnat = load_metric(f'{g}/targets.{hemi}.native.func.gii')
        for fit in ['fit1', 'fit2', 'fit3']:
            r32 = reconstruct(m32, fit)
            rnat = reconstruct(mnat, fit)
            keys = ['pa', 'ecc', 'prf'] + (['r2'] if fit == 'fit1' else [])
            for k in keys:
                mp = MAPNAME[k]
                write_map(f'{outdir}/{sub}.empirical_{mp}_{fit}-spherereg.{hemi}.32k_fs_LR.func.gii',
                          r32[k], f'{mp}_{fit}_spherereg', hemi)
                write_map(f'{outdir}/{sub}.empirical_{mp}_{fit}.{hemi}.native.func.gii',
                          rnat[k], f'{mp}_{fit}_native', hemi)
        # myelin, mat route (32k MSMAll -> native -> 32k sphere.reg); range-bounded,
        # same smoothness class as the original training input
        mm = load_metric(f'{g}/myelin_mat.{hemi}.32k_spherereg.func.gii')
        roi = mm['validm']
        good = roi >= VALID_THR
        with np.errstate(divide='ignore', invalid='ignore'):
            my = np.where(good, mm['myelin'] / np.where(roi > 0, roi, np.nan), np.nan)
        write_map(f'{outdir}/{sub}.myelinmap-spherereg.{hemi}.32k_fs_LR.func.gii',
                  my, 'myelin_spherereg', hemi)
    if (i + 1) % 20 == 0:
        print(f'{i+1}/{len(subs)}', flush=True)
print('export done')
