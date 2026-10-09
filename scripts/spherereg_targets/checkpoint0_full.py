#!/usr/bin/env python
"""Checkpoint 0 over all subjects: file census + native vertex-count identity.
Exits nonzero listing offenders if anything is missing or mismatched."""
import os, sys
import nibabel as nib

WORK = '/scratch/project_mnt/S0210/deepRetinotopy_TheToolbox/sandbox/spherereg_targets'
FS = '/scratch/project_mnt/S0210/deepRetinotopy_TheToolbox/HCP/freesurfer'
subs = [s.strip() for s in open(f'{WORK}/subjects.txt') if s.strip()]

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

print(f'{len(subs)} subjects checked')
print(f'missing files: {len(missing)}')
for s, m in missing[:20]:
    print('  ', s, m[:3], '...' if len(m) > 3 else '')
print(f'vertex-count mismatches: {len(mismatch)}')
for row in mismatch[:20]:
    print('  ', row)
sys.exit(1 if (missing or mismatch) else 0)
