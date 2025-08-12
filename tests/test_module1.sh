#!/usr/bin/env bash
set -e


ml deepretinotopy
cd /storage/deep_retinotopy/deepRetinotopy_TheToolbox

dirSubs="/storage/deep_retinotopy/data"
echo "Path to freesurfer data: "$dirSubs""
# remove files to perform tests
rm $dirSubs/*/surf/*curvature-midthickness*
rm $dirSubs/*/surf/*graymid

dirHCP="/storage/deep_retinotopy/templates/"
echo "Path to template surfaces: "$dirHCP""

export PATH=/storage/deep_retinotopy/deepRetinotopy_TheToolbox/:/storage/deep_retinotopy/deepRetinotopy_TheToolbox/main/:/storage/deep_retinotopy/deepRetinotopy_TheToolbox/utils/:$PATH
export DEPLOY_BINS=midthickness_surf.py:$DEPLOY_BINS

cd main
for hemisphere in lh rh; do
    for fast in 'yes'; do
        echo "Hemisphere: "$hemisphere""
        echo "[DEBUG]: Module 1: Generating mid-thickness surface and curvature data..."
        clone_command="./1_native2fsaverage.sh -s $dirSubs -t $dirHCP -h $hemisphere -g $fast"
        echo $clone_command
        eval $clone_command

        if find $dirSubs -name "*${hemisphere}.midthickness.32k_fs_LR.surf.gii" -size +0 | grep -q '.'; then
            echo "midthickness surface generated"
        else
            echo "midthickness surface not generated"
        fi

        if find $dirSubs -name "*curvature-midthickness.${hemisphere}.32k_fs_LR.func.gii" -size +0 | grep -q '.'; then
            echo "curvature data generated"
        else
            echo "curvature data not generated"
        fi
    done
done
