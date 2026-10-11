#!/usr/bin/env python
"""Checkpoint 4.5: read_HCP loads the new *_spherereg.mat files and returns tensors
with the same shapes and comparable mask sizes as with the originals."""
import os, sys
import numpy as np
import scipy.io as sio

TOOLBOX = '/scratch/project_mnt/S0210/deepRetinotopy_TheToolbox'
WORK = f'{TOOLBOX}/sandbox/spherereg_targets'
sys.path.insert(0, TOOLBOX)
from utils.read_data import read_HCP
from utils.rois import get_roi
from utils.labels import labels

# Stage a converted-dir lookalike for the new files
base = f'{WORK}/loader_test/HCP_new'
conv = f'{base}/raw/converted'
os.makedirs(conv, exist_ok=True)
links = {
    'cifti_polarAngle_all.mat': f'{WORK}/mat/cifti_polarAngle_all_spherereg.mat',
    'cifti_eccentricity_all.mat': f'{WORK}/mat/cifti_eccentricity_all_spherereg.mat',
    'cifti_pRFsize_all.mat': f'{WORK}/mat/cifti_pRFsize_all_spherereg.mat',
    'cifti_R2_all.mat': f'{WORK}/mat/cifti_R2_all_spherereg.mat',
    'cifti_myelin_all.mat': f'{WORK}/mat/cifti_myelin_all_spherereg.mat',
    'mid_pos_L.mat': f'{TOOLBOX}/HCP/raw/converted/mid_pos_L.mat',
    'mid_pos_R.mat': f'{TOOLBOX}/HCP/raw/converted/mid_pos_R.mat',
}
for name, target in links.items():
    p = f'{conv}/{name}'
    if not os.path.islink(p) and not os.path.exists(p):
        os.symlink(target, p)
if not os.path.islink(f'{base}/freesurfer'):
    os.symlink(f'{TOOLBOX}/HCP/freesurfer', f'{base}/freesurfer')

mask_L, mask_R, idx_L, idx_R = get_roi('wholebrain')
faces_R = labels(sio.loadmat(f'{TOOLBOX}/utils/templates/tri_faces_R.mat')['tri_faces_R'] - 1, idx_R)
faces_L = labels(sio.loadmat(f'{TOOLBOX}/utils/templates/tri_faces_L.mat')['tri_faces_L'] - 1, idx_L)

orig_path = f'{TOOLBOX}/HCP/raw/converted'
new_path = conv
subs = ['100610', '102311', '102816']
ok = True
for sub in subs:
    for hemi in ['Left', 'Right']:
        for pred in ['polarAngle', 'eccentricity', 'pRFsize', 'visualCoord']:
            for myel in [False, True]:
                kw = dict(hemisphere=hemi, sub_id=sub, visual_mask_L=mask_L,
                          visual_mask_R=mask_R, faces_L=faces_L, faces_R=faces_R,
                          myelination=myel, prediction=pred)
                dO = read_HCP(orig_path, **kw)
                dN = read_HCP(new_path, **kw)
                shapes_ok = (dO.x.shape == dN.x.shape and dO.y.shape == dN.y.shape
                             and dO.pos.shape == dN.pos.shape and dO.face.shape == dN.face.shape)
                mO, mN = int(dO.mask.sum()), int(dN.mask.sum())
                rel = abs(mN - mO) / max(mO, 1)
                line_ok = shapes_ok and rel <= 0.05
                ok &= line_ok
                print(f'{sub} {hemi[:1]} {pred:12s} myel={int(myel)}: '
                      f'x{tuple(dN.x.shape)} y{tuple(dN.y.shape)} mask {mO}->{mN} '
                      f'({rel*100:.1f}%) {"OK" if line_ok else "FAIL"}')
print('PASS' if ok else 'FAIL')
