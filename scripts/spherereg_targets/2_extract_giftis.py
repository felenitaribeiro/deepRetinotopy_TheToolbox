#!/usr/bin/env python
"""Extract per-subject, per-hemisphere GIFTI metric files from the training .mat files.

Targets file (targets.<h>.32k.func.gii), one column set per fit present on disk:
  cos<f>, sin<f> : cos/sin of polar angle (deg) -- never interpolate angle directly
  ecc<f>, prf<f>, r2<f> : eccentricity, pRF size, R2 (r2 only for fit1)
  valid<f> : 1 where polar angle AND eccentricity are finite, else 0
Invalid vertices are zero-filled in every column so NaN does not spread.

Myelin file (myelin_mat.<h>.32k.func.gii): myelin (zero-filled) + validm column.
"""
import argparse, os, sys
import numpy as np
import scipy.io as sio
import nibabel as nib

WORK = '/scratch/project_mnt/S0210/deepRetinotopy_TheToolbox/sandbox/spherereg_targets'
CONV = '/scratch/project_mnt/S0210/deepRetinotopy_TheToolbox/HCP/raw/converted'
NHEMI = 32492

STRUCT = {'lh': 'CortexLeft', 'rh': 'CortexRight'}


def write_metric(path, cols, names, hemi):
    darrays = []
    for name, col in zip(names, cols):
        d = nib.gifti.GiftiDataArray(np.asarray(col, dtype=np.float32),
                                     intent='NIFTI_INTENT_NONE',
                                     datatype='NIFTI_TYPE_FLOAT32')
        d.meta = nib.gifti.GiftiMetaData({'Name': name,
                                          'AnatomicalStructurePrimary': STRUCT[hemi]})
        darrays.append(d)
    img = nib.gifti.GiftiImage(darrays=darrays)
    img.meta = nib.gifti.GiftiMetaData({'AnatomicalStructurePrimary': STRUCT[hemi]})
    nib.save(img, path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--subjects', nargs='+', required=True)
    ap.add_argument('--fits', nargs='+', default=['fit1'])
    args = ap.parse_args()

    mats = {}
    for fit in args.fits:
        for short, var, field in [('polarAngle', 'cifti_polarAngle', 'polarangle'),
                                  ('eccentricity', 'cifti_eccentricity', 'eccentricity'),
                                  ('pRFsize', 'cifti_pRFsize', 'receptivefieldsize')]:
            fname = f'cifti_{short}_all.mat' if fit == 'fit1' else f'cifti_{short}_{fit}_all.mat'
            key = (fit, field)
            if key not in mats:
                path = os.path.join(CONV, fname)
                if not os.path.exists(path):
                    sys.exit(f'missing {path}')
                mats[key] = sio.loadmat(path)[var]
    r2mat = sio.loadmat(os.path.join(CONV, 'cifti_R2_all.mat'))['cifti_R2']
    mymat = sio.loadmat(os.path.join(CONV, 'cifti_myelin_all.mat'))['cifti_myelin']

    for sub in args.subjects:
        outdir = os.path.join(WORK, 'gii', sub)
        os.makedirs(outdir, exist_ok=True)
        for hemi, sl in [('lh', slice(0, NHEMI)), ('rh', slice(NHEMI, 2 * NHEMI))]:
            cols, names = [], []
            for fit in args.fits:
                pa = mats[(fit, 'polarangle')][f'x{sub}_{fit}_polarangle_msmall'][0, 0][sl, 0]
                ecc = mats[(fit, 'eccentricity')][f'x{sub}_{fit}_eccentricity_msmall'][0, 0][sl, 0]
                prf = mats[(fit, 'receptivefieldsize')][f'x{sub}_{fit}_receptivefieldsize_msmall'][0, 0][sl, 0]
                valid = np.isfinite(pa) & np.isfinite(ecc)
                rad = np.deg2rad(np.where(valid, pa, 0.0))
                def z(v):
                    return np.where(valid & np.isfinite(v), v, 0.0)
                cols += [np.where(valid, np.cos(rad), 0.0), np.where(valid, np.sin(rad), 0.0),
                         z(ecc), z(prf)]
                names += [f'cos_{fit}', f'sin_{fit}', f'ecc_{fit}', f'prf_{fit}']
                if fit == 'fit1':
                    r2 = r2mat[f'x{sub}_fit1_r2_msmall'][0, 0][sl, 0]
                    cols.append(z(r2)); names.append('r2_fit1')
                cols.append(valid.astype(np.float32)); names.append(f'valid_{fit}')
            write_metric(os.path.join(outdir, f'targets.{hemi}.32k.func.gii'), cols, names, hemi)

            my = mymat[f'x{sub}_myelinmap'][0, 0][sl, 0]
            vm = np.isfinite(my)
            write_metric(os.path.join(outdir, f'myelin_mat.{hemi}.32k.func.gii'),
                         [np.where(vm, my, 0.0), vm.astype(np.float32)],
                         ['myelin', 'validm'], hemi)
        print('extracted', sub, flush=True)


if __name__ == '__main__':
    main()
