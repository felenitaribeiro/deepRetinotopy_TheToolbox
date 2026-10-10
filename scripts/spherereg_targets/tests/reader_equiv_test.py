"""read_HCP_gifti (per-subject GIFTIs) vs read_HCP (new _spherereg.mat via symlinks):
same x, y, pos, R2, mask up to float32 rounding."""
import os, sys
import numpy as np
import scipy.io as sio
TOOLBOX='/scratch/project_mnt/S0210/deepRetinotopy_TheToolbox'
WORK=f'{TOOLBOX}/sandbox/spherereg_targets'
sys.path.insert(0, TOOLBOX)
from utils.read_data import read_HCP, read_HCP_gifti
from utils.rois import get_roi
from utils.labels import labels

mask_L, mask_R, idx_L, idx_R = get_roi('wholebrain')
faces_R = labels(sio.loadmat(f'{TOOLBOX}/utils/templates/tri_faces_R.mat')['tri_faces_R']-1, idx_R)
faces_L = labels(sio.loadmat(f'{TOOLBOX}/utils/templates/tri_faces_L.mat')['tri_faces_L']-1, idx_L)
new_mat_path=f'{WORK}/loader_test/HCP_new/raw/converted'
fs_path=f'{TOOLBOX}/HCP/freesurfer'
ok=True
for sub in ['100610','102311','169444']:
    for hemi in ['Left','Right']:
        for pred in ['polarAngle','eccentricity','pRFsize','visualCoord']:
            for myel in [False,True]:
                kw=dict(hemisphere=hemi, sub_id=sub, visual_mask_L=mask_L, visual_mask_R=mask_R,
                        faces_L=faces_L, faces_R=faces_R, myelination=myel, prediction=pred)
                a=read_HCP(new_mat_path, **kw)
                b=read_HCP_gifti(fs_path, **kw)
                dx=(a.x-b.x).abs().max().item()
                dy=(a.y-b.y).abs().max().item()
                dr=(a.R2-b.R2).abs().max().item()
                dm=int((a.mask!=b.mask).sum())
                dp=(a.pos-b.pos).abs().max().item()
                line_ok = dx<1e-4 and dy<2e-3 and dr<1e-3 and dm<=2 and dp==0
                ok &= line_ok
                if not line_ok or (pred=='polarAngle' and not myel):
                    print(f'{sub} {hemi[:1]} {pred:12s} myel={int(myel)}: dx={dx:.2e} dy={dy:.2e} dR2={dr:.2e} mask_mismatch={dm} {"OK" if line_ok else "FAIL"}')
print('PASS' if ok else 'FAIL')
