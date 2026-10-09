import scipy.io as sio, re, os
v = sio.loadmat('/scratch/project_mnt/S0210/deepRetinotopy_TheToolbox/HCP/raw/converted/cifti_polarAngle_all.mat')['cifti_polarAngle']
subs = sorted(re.match(r'x(\d+)_fit1', n).group(1) for n in v.dtype.names if '_fit1_' in n)
print(len(subs), 'subjects')
open('/scratch/project_mnt/S0210/deepRetinotopy_TheToolbox/sandbox/spherereg_targets/subjects.txt','w').write('\n'.join(subs)+'\n')
fsdirs = set(os.listdir('/scratch/project_mnt/S0210/deepRetinotopy_TheToolbox/HCP/freesurfer'))
print('missing fs dirs:', [s for s in subs if s not in fsdirs])
