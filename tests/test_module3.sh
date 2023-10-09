#!/usr/bin/env bash
set -e

export APPTAINER_BINDPATH='/cvmfs,/mnt,/home,/data,/templates'
source /usr/share/module.sh
module use /cvmfs/neurodesk.ardc.edu.au/neurodesk-modules/*
ml deepretinotopy/1.0.1

echo "[DEBUG]: test if deepRetinotopy repo is cloned"
ls
cp -r . /tmp/deepRetinotopy_TheToolbox

# test readme
echo "[DEBUG]: testing the clone command from the README:"
clone_command=`cat /tmp/deepRetinotopy_TheToolbox/README.md | grep https://github.com/felenitaribeiro/deepRetinotopy_TheToolbox.git`
echo $clone_command
$clone_command

cd deepRetinotopy_TheToolbox

dirSubs="/data/"
echo "Path to freesurfer data: "$dirSubs""

dirHCP="/templates/"
echo "Path to template surfaces: "$dirHCP""

model=average
echo "Model: "$model""

cd main
for hemisphere in lh; # rh; 
do
    for map in 'polarAngle'; #'eccentricity' 'pRFsize';
    do
        echo "Hemisphere: "$hemisphere""
        echo "[DEBUG]: Module 3: Resampling data back to native space..."
        clone_command=`cat ../deepRetinotopy.sh | grep 3_fsaverage2native.sh`
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
    do
done