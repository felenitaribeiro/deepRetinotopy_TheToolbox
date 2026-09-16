"""Export per-subject myelin maps as GIFTIs for benchmark inference.

Training (read_HCP with myelination=True) takes myelin from
HCP/raw/converted/cifti_myelin_all.mat (key 'x<sub>_myelinmap'; LH = rows
0:32492, RH = rows 32492:64984). Inference on the freesurfer-style directory
goes through read_gifti, which expects per-subject files
  <sub>/surf/<sub>.myelinmap-midthickness.<lh|rh>.32k_fs_LR.func.gii
next to the curvature files. This script writes those files from the .mat,
using each subject's curvature GIFTI as a template, so the inference features
match training exactly. Existing myelin GIFTIs are overwritten (idempotent).
"""
import os
import os.path as osp
import numpy as np
import nibabel as nib
import scipy.io

REPO = osp.dirname(osp.dirname(osp.realpath(__file__)))
FS_DIR = osp.join(REPO, 'HCP', 'freesurfer')
MAT = osp.join(REPO, 'HCP', 'raw', 'converted', 'cifti_myelin_all.mat')

N_HEMI = 32492

myelin = scipy.io.loadmat(MAT)['cifti_myelin']
subjects = sorted(
    s for s in os.listdir(FS_DIR)
    if osp.isdir(osp.join(FS_DIR, s, 'surf')) and not s.startswith('processed_')
    and s != 'fsaverage')

written, skipped = 0, []
for sub in subjects:
    key = 'x' + sub + '_myelinmap'
    if key not in myelin.dtype.names:
        skipped.append(sub)
        continue
    full = np.asarray(myelin[key][0][0]).reshape(-1)
    assert full.shape[0] == 2 * N_HEMI, (sub, full.shape)
    for hemi, sl in (('lh', slice(0, N_HEMI)), ('rh', slice(N_HEMI, 2 * N_HEMI))):
        curv_path = osp.join(FS_DIR, sub, 'surf',
                             f'{sub}.curvature-midthickness.{hemi}.32k_fs_LR.func.gii')
        out_path = osp.join(FS_DIR, sub, 'surf',
                            f'{sub}.myelinmap-midthickness.{hemi}.32k_fs_LR.func.gii')
        template = nib.load(curv_path)
        data = template.agg_data()
        assert data.shape[0] == N_HEMI, (sub, hemi, data.shape)
        data[:] = full[sl]
        nib.save(template, out_path)
        written += 1

print(f'Wrote {written} myelin GIFTIs for {len(subjects) - len(skipped)} subjects.')
if skipped:
    print(f'WARNING: no myelin data in .mat for {len(skipped)} subjects: {skipped}')
