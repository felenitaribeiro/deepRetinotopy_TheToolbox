#!/usr/bin/env python
"""Checkpoints 0 and 1 (inputs): file census, native vertex-count identity,
curvature provenance over all subjects, and the cifti_curv_all.mat
disconfirmation (checkpoint 1b.2, pilot subjects).
Exits nonzero listing offenders if anything is missing or mismatched."""
import os, sys
import numpy as np
import nibabel as nib
import scipy.io as sio

WORK = '/scratch/project_mnt/S0210/deepRetinotopy_TheToolbox/sandbox/spherereg_targets'
FS = '/scratch/project_mnt/S0210/deepRetinotopy_TheToolbox/HCP/freesurfer'
CONV = '/scratch/project_mnt/S0210/deepRetinotopy_TheToolbox/HCP/raw/converted'
PILOT = ['100610', '102311', '102816', '104416', '105923']
NHEMI = 32492
subs = [s.strip() for s in open(f'{WORK}/subjects.txt') if s.strip()]

print('=== checkpoint 0: file census + native vertex-count identity ===')
missing, mismatch = [], []
for sub in subs:
    files = []
    for H, h in [('L', 'lh'), ('R', 'rh')]:
        files += [
            f'{WORK}/hcp/{sub}/{sub}.{H}.sphere.MSMAll.native.surf.gii',
            f'{WORK}/hcp/{sub}/{sub}.{H}.midthickness.native.surf.gii',
            f'{WORK}/hcp/{sub}/{sub}.{H}.midthickness_MSMAll.32k_fs_LR.surf.gii',
            f'{FS}/{sub}/surf/{h}.sphere.reg.surf.gii',
            f'{FS}/{sub}/surf/{h}.midthickness.surf.gii',
            f'{FS}/{sub}/surf/{sub}.{h}.midthickness.32k_fs_LR.surf.gii',
            f'{FS}/{sub}/surf/{h}.graymid.H.gii',
            f'{FS}/{sub}/surf/{sub}.curvature-midthickness.{h}.32k_fs_LR.func.gii',
        ]
    files.append(f'{WORK}/hcp/{sub}/{sub}.MyelinMap_BC.native.dscalar.nii')
    miss = [f for f in files if not os.path.exists(f)]
    if miss:
        missing.append((sub, miss))
        continue
    for H, h in [('L', 'lh'), ('R', 'rh')]:
        n_hcp = nib.load(f'{WORK}/hcp/{sub}/{sub}.{H}.sphere.MSMAll.native.surf.gii').darrays[0].dims[0]
        n_reg = nib.load(f'{FS}/{sub}/surf/{h}.sphere.reg.surf.gii').darrays[0].dims[0]
        n_mid = nib.load(f'{FS}/{sub}/surf/{h}.midthickness.surf.gii').darrays[0].dims[0]
        if not (n_hcp == n_reg == n_mid):
            mismatch.append((sub, H, n_hcp, n_reg, n_mid))
print(f'{len(subs)} subjects checked; missing files: {len(missing)}; '
      f'vertex-count mismatches: {len(mismatch)}')
for s, m in missing[:20]:
    print('  missing:', s, m[:3], '...' if len(m) > 3 else '')
for row in mismatch[:20]:
    print('  mismatch:', row)

print('=== checkpoint 1.1: training-curvature provenance census ===')
bad = []
for sub in subs:
    for h, H in [('lh', 'L'), ('rh', 'R')]:
        img = nib.load(f'{FS}/{sub}/surf/{sub}.curvature-midthickness.{h}.32k_fs_LR.func.gii')
        prov = dict(img.meta).get('Provenance', '')
        ok = (f'{h}.graymid.H.gii' in prov and f'{h}.sphere.reg.surf.gii' in prov
              and f'fs_LR-deformed_to-fsaverage.{H}.sphere.32k_fs_LR.surf.gii' in prov
              and 'ADAP_BARY_AREA' in prov and f'{h}.midthickness.surf.gii' in prov
              and f'{sub}.{h}.midthickness.32k_fs_LR.surf.gii' in prov)
        if not ok:
            bad.append((sub, h, prov[:200]))
print(f'{len(subs)*2} curvature files checked; non-conforming: {len(bad)}')
for b in bad[:10]:
    print('  ', b)

print('=== checkpoint 1b.2: cifti_curv_all.mat is NOT the training curvature (pilot) ===')
curv = sio.loadmat(f'{CONV}/cifti_curv_all.mat')['cifti_curv']
for sub in PILOT:
    for h, sl in [('lh', slice(0, NHEMI)), ('rh', slice(NHEMI, 2 * NHEMI))]:
        a = curv[f'x{sub}_curvature'][0, 0][:, 0][sl]
        b = nib.load(f'{FS}/{sub}/surf/{sub}.curvature-midthickness.{h}.32k_fs_LR.func.gii').darrays[0].data
        m = np.isfinite(a) & np.isfinite(b)
        print(f'{sub} {h}: corr={np.corrcoef(a[m], b[m])[0, 1]:.3f} (expect ~-0.34)')

sys.exit(1 if (missing or mismatch or bad) else 0)
