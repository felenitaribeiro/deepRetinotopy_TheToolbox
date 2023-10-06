#!/usr/bin/env bash
set -e

export APPTAINER_BINDPATH='/cvmfs,/mnt,/home,/data,/templates'
source /usr/share/module.sh
module use /cvmfs/neurodesk.ardc.edu.au/neurodesk-modules/*
ml deepretinotopy/1.0.1

echo "[DEBUG]: test deepRetinotopy on the Singularity container"
cd /cvmfs/neurodesk.ardc.edu.au/containers/deepretinotopy_1.0.1_20231005/deepretinotopy_1.0.1_20231005.simg/opt/deepRetinotopy_TheToolbox

dirSubs="/data/"
echo "Path to freesurfer data: "$dirSubs""

dirHCP="/templates/"
echo "Path to template surfaces: "$dirHCP""

datasetName="TEST"
echo "Dataset name: "$datasetName""

cd main
for hemisphere in 'lh' 'rh';
do 
    for map in 'polarAngle'; #'eccentricity' 'pRFsize';
    do
        echo "Hemisphere: "$hemisphere""
        python 2_inference.py --path $dirSubs --dataset $datasetName --prediction_type $map --hemisphere $hemisphere
        rm -r $dirSubs/processed

    done
done
