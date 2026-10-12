#!/bin/bash
# Step 1: subject list, per-subject HCP S1200 surfaces + native myelin from S3,
# and the canonical template spheres.
#
# Usage: 1_download_hcp.sh                 # full cohort: list + pilot extras + all 181 + templates
#        1_download_hcp.sh <sub> [pilot]   # one subject (helper mode; "pilot" adds the
#                                          # 32k sphere + 32k MSMAll myelin used by checks)
set -euo pipefail
WORK=/scratch/project_mnt/S0210/deepRetinotopy_TheToolbox/sandbox/spherereg_targets
TOOLBOX=/scratch/project_mnt/S0210/deepRetinotopy_TheToolbox
HERE=$(cd "$(dirname "$0")" && pwd)
PILOT="100610 102311 102816 104416 105923"

download_one() {
    local sub=$1 pilot=${2:-}
    local dest=$WORK/hcp/$sub
    local S3=s3://hcp-openaccess/HCP_1200/$sub/MNINonLinear
    mkdir -p "$dest"
    get() { [ -s "$dest/$(basename "$1")" ] || aws s3 cp "$1" "$dest/" --only-show-errors; }
    for H in L R; do
        get $S3/Native/$sub.$H.sphere.MSMAll.native.surf.gii
        get $S3/Native/$sub.$H.midthickness.native.surf.gii
        get $S3/fsaverage_LR32k/$sub.$H.midthickness_MSMAll.32k_fs_LR.surf.gii
    done
    get $S3/Native/$sub.MyelinMap_BC.native.dscalar.nii
    if [ "$pilot" == "pilot" ]; then
        for H in L R; do get $S3/fsaverage_LR32k/$sub.$H.sphere.32k_fs_LR.surf.gii; done
        get $S3/fsaverage_LR32k/$sub.MyelinMap_BC_MSMAll.32k_fs_LR.dscalar.nii
    fi
    echo "done $sub"
}

# helper mode: one subject
if [ $# -ge 1 ]; then
    download_one "$@"
    exit 0
fi

mkdir -p $WORK/{hcp,gii,mat,checks,templates}

# subject list from the .mat field names (181 subjects)
conda run -n deepretinotopy_2 python - <<PYEOF
import scipy.io as sio, re, os
v = sio.loadmat('$TOOLBOX/HCP/raw/converted/cifti_polarAngle_all.mat')['cifti_polarAngle']
subs = sorted(re.match(r'x(\d+)_fit1', n).group(1) for n in v.dtype.names if '_fit1_' in n)
open('$WORK/subjects.txt', 'w').write('\n'.join(subs) + '\n')
print(len(subs), 'subjects')
PYEOF

for s in $PILOT; do download_one "$s" pilot; done
cat $WORK/subjects.txt | xargs -P 8 -I{} "$HERE/1_download_hcp.sh" {}

# canonical template spheres: the (subject-invariant) fs_LR 32k sphere and the 2016
# fs_LR-deformed_to-fsaverage spheres from the toolbox templates/ (checksums in report.md)
conda run -n deepretinotopy_2 python - <<PYEOF
import shutil
for H in 'LR':
    shutil.copy2(f'$WORK/hcp/100610/100610.{H}.sphere.32k_fs_LR.surf.gii',
                 f'$WORK/templates/S1200.{H}.sphere.32k_fs_LR.surf.gii')
    shutil.copy2(f'$TOOLBOX/templates/fs_LR-deformed_to-fsaverage.{H}.sphere.32k_fs_LR.surf.gii',
                 f'$WORK/templates/fs_LR-deformed_to-fsaverage.{H}.sphere.32k_fs_LR.surf.gii')
print('templates staged')
PYEOF
echo "download stage complete"
