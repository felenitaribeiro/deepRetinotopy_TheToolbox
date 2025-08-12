#!/usr/bin/env bash
set -e

echo "[DEBUG]: test deepRetinotopy on the Singularity container"
export APPTAINER_BINDPATH='/cvmfs,/mnt,/home,/data,/templates,/storage'
# Remove all the if/then module sourcing attempts and replace with:
export LMOD_CMD=/usr/share/lmod/lmod/libexec/lmod

# Create the module/ml function directly
module() { eval $($LMOD_CMD bash "$@") 2>/dev/null; }
export -f module

ml() { module load "$@"; }
export -f ml

# add neurodesk modules
module use /cvmfs/neurodesk.ardc.edu.au/neurodesk-modules/*
ml deepretinotopy

echo "[DEBUG]: test if deepRetinotopy repo is cloned"
if find .-name "deepRetinotopy" -size +0 | grep -q '.'; then
    echo "deepRetinotopy repo is cloned"
else
    echo "deepRetinotopy repo is not cloned"
fi
sudo mkdir -p /storage/deep_retinotopy/deepRetinotopy_TheToolbox/
sudo chmod 777 /storage/deep_retinotopy/deepRetinotopy_TheToolbox/
cp -r ./* /storage/deep_retinotopy/deepRetinotopy_TheToolbox/

cd /storage/deep_retinotopy/deepRetinotopy_TheToolbox

dirSubs="/storage/deep_retinotopy/data/"
echo "Path to freesurfer data: "$dirSubs""
rm /storage/deep_retinotopy/data/*/surf/*curvature-midthickness*
rm /storage/deep_retinotopy/data/*/surf/*graymid

dirHCP="/storage/deep_retinotopy/templates/"
echo "Path to template surfaces: "$dirHCP""

export PATH=/storage/deep_retinotopy/deepRetinotopy_TheToolbox/:/storage/deep_retinotopy/deepRetinotopy_TheToolbox/main/:/storage/deep_retinotopy/deepRetinotopy_TheToolbox/utils/:$PATH
export DEPLOY_BINS=midthickness_surf.py:$DEPLOY_BINS

cd main
for hemisphere in lh rh; do
    for fast in 'yes'; do
        echo "Hemisphere: "$hemisphere""
        echo "[DEBUG]: Module 1: Generating mid-thickness surface and curvature data..."
        # clone_comand=`cat ../deepRetinotopy | grep 1_native2fsaverage.sh`
        rm $dirSubs/*/surf/*graymid*
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
