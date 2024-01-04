#!/usr/bin/env bash
set -e

export APPTAINER_BINDPATH='/cvmfs,/mnt,/home,/data,/templates'
source /usr/share/module.sh
module use /cvmfs/neurodesk.ardc.edu.au/neurodesk-modules/*
ml deepretinotopy/1.0.2

echo "[DEBUG]: test if deepRetinotopy repo is cloned"
if find .-name "deepRetinotopy.sh" -size +0 | grep -q '.'; then
    echo "deepRetinotopy repo is cloned"
else
    echo "deepRetinotopy repo is not cloned"
fi
cp -r . ~/deepRetinotopy_TheToolbox/

cd ~/deepRetinotopy_TheToolbox

dirSubs="/data/"
echo "Path to freesurfer data: "$dirSubs""
rm /data/*/surf/*curvature-midthickness*
rm /data/*/surf/*graymid

dirHCP="/templates/"
echo "Path to template surfaces: "$dirHCP""

cd main
for hemisphere in lh rh; do
    echo "Hemisphere: "$hemisphere""
    echo "[DEBUG]: Module 1: Generating mid-thickness surface and curvature data..."
    clone_command=`cat ../deepRetinotopy.sh | grep 1_native2fsaverage.sh`
    echo $clone_command
    eval $clone_command

    if find /data -name "*${hemisphere}.midthickness.32k_fs_LR.surf.gii" -size +0 | grep -q '.'; then
        echo "midthickness surface generated"
    else
        echo "midthickness surface not generated"
    fi

    if find /data -name "*curvature-midthickness.${hemisphere}.32k_fs_LR.func.gii" -size +0 | grep -q '.'; then
        echo "curvature data generated"
    else
        echo "curvature data not generated"
    fi
done
