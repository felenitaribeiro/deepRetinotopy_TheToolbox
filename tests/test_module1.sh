#!/usr/bin/env bash
set -e

export APPTAINER_BINDPATH='/cvmfs,/mnt,/home,/data,/templates'
source /usr/share/module.sh
module use /cvmfs/neurodesk.ardc.edu.au/neurodesk-modules/*
ml deepretinotopy/1.0.11

echo "[DEBUG]: test if deepRetinotopy repo is cloned"
if find .-name "deepRetinotopy" -size +0 | grep -q '.'; then
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

export PATH=~/deepRetinotopy_TheToolbox/:~/deepRetinotopy_TheToolbox/main/:~/deepRetinotopy_TheToolbox/utils/:$PATH
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
