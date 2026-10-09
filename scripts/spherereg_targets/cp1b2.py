import scipy.io as sio, nibabel as nib, numpy as np
C='/scratch/project_mnt/S0210/deepRetinotopy_TheToolbox/HCP/raw/converted'
FS='/scratch/project_mnt/S0210/deepRetinotopy_TheToolbox/HCP/freesurfer'
curv=sio.loadmat(f'{C}/cifti_curv_all.mat')['cifti_curv']
N=32492
for sub in ['100610','102311','102816','104416','105923']:
    for h,sl in [('lh',slice(0,N)),('rh',slice(N,2*N))]:
        a=curv[f'x{sub}_curvature'][0,0][:,0][sl]
        b=nib.load(f'{FS}/{sub}/surf/{sub}.curvature-midthickness.{h}.32k_fs_LR.func.gii').darrays[0].data
        m=np.isfinite(a)&np.isfinite(b)
        print(f'{sub} {h}: corr={np.corrcoef(a[m],b[m])[0,1]:.3f} (n={m.sum()})')
