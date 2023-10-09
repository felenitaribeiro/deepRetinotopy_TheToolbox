#!/usr/bin/env bash
set -e

echo "[DEBUG]: test deepRetinotopy on the Singularity container"
export APPTAINER_BINDPATH='/cvmfs,/mnt,/home,/data,/templates'
source /usr/share/module.sh
module use /cvmfs/neurodesk.ardc.edu.au/neurodesk-modules/*
ml deepretinotopy/1.0.1

# test readme
echo "[DEBUG]: testing the clone command from the README:"
clone_command=`cat /tmp/deepRetinotopy_TheToolbox/README.md | grep https://github.com/felenitaribeiro/deepRetinotopy_TheToolbox.git`
echo $clone_command
$clone_command

echo "[DEBUG]: copying models' weights from cvmfs to repo directory:"
cd /cvmfs/neurodesk.ardc.edu.au/containers/deepretinotopy_1.0.1_20231006/deepretinotopy_1.0.1_20231006.simg/opt/deepRetinotopy_TheToolbox
mkdir ~/deepRetinotopy_TheToolbox/models/
cp -r models/deepRetinotopy_polarAngle_LH_* ~/deepRetinotopy_TheToolbox/models

dirSubs="/data/"
echo "Path to freesurfer data: "$dirSubs""
sudo chmod u+w "$dirSubs"*

dirHCP="/templates/"
echo "Path to template surfaces: "$dirHCP""

datasetName="TEST"
echo "Dataset name: "$datasetName""


cd ~/deepRetinotopy_TheToolbox/main
for hemisphere in 'lh'; # 'rh';
do 
    for map in 'polarAngle'; #'eccentricity' 'pRFsize';
    do
        echo "Hemisphere: "$hemisphere""
        python 2_inference.py --path $dirSubs --dataset $datasetName --prediction_type $map --hemisphere $hemisphere
        rm -r $dirSubs/processed
    done
done
