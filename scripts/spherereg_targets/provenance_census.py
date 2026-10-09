import nibabel as nib, re, sys
WORK='/scratch/project_mnt/S0210/deepRetinotopy_TheToolbox/sandbox/spherereg_targets'
FS='/scratch/project_mnt/S0210/deepRetinotopy_TheToolbox/HCP/freesurfer'
subs=[s.strip() for s in open(f'{WORK}/subjects.txt') if s.strip()]
bad=[]
for sub in subs:
    for h,H in [('lh','L'),('rh','R')]:
        img=nib.load(f'{FS}/{sub}/surf/{sub}.curvature-midthickness.{h}.32k_fs_LR.func.gii')
        meta=dict(img.meta)
        prov=meta.get('Provenance','')
        ok=(f'{h}.graymid.H.gii' in prov and f'{h}.sphere.reg.surf.gii' in prov
            and f'fs_LR-deformed_to-fsaverage.{H}.sphere.32k_fs_LR.surf.gii' in prov
            and 'ADAP_BARY_AREA' in prov and f'{h}.midthickness.surf.gii' in prov
            and f'{sub}.{h}.midthickness.32k_fs_LR.surf.gii' in prov)
        if not ok: bad.append((sub,h,prov[:200]))
print(f'{len(subs)*2} files checked; non-conforming: {len(bad)}')
for b in bad[:10]: print(b)
sys.exit(1 if bad else 0)
