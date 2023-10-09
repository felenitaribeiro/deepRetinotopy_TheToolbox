#!/usr/bin/env bash
set -e

echo "[DEBUG]: test deepRetinotopy on the Singularity container"
export APPTAINER_BINDPATH='/cvmfs,/mnt,/home,/data,/templates'
source /usr/share/module.sh
module use /cvmfs/neurodesk.ardc.edu.au/neurodesk-modules/*
ml deepretinotopy/1.0.1

echo "[DEBUG]: test if deepRetinotopy repo is cloned"
ls
cp -r . /tmp/deepRetinotopy_TheToolbox
cd ~

# test readme
echo "[DEBUG]: testing the clone command from the README:"
clone_command=`cat /tmp/deepRetinotopy_TheToolbox/README.md | grep https://github.com/felenitaribeiro/deepRetinotopy_TheToolbox.git`
echo $clone_command
$clone_command

echo "[DEBUG]: copying models' weights from cvmfs to repo directory:"
cd /cvmfs/neurodesk.ardc.edu.au/containers/deepretinotopy_1.0.1_20231006/deepretinotopy_1.0.1_20231006.simg/opt/deepRetinotopy_TheToolbox
sudo mkdir ~/deepRetinotopy_TheToolbox/models/
sudo chmod 777 ~/deepRetinotopy_TheToolbox/
sudo cp -r models/deepRetinotopy_polarAngle_LH_* ~/deepRetinotopy_TheToolbox/models/

dirSubs="/data/"
echo "Path to freesurfer data: "$dirSubs""

dirHCP="/templates/"
echo "Path to template surfaces: "$dirHCP""

datasetName="TEST"
echo "Dataset name: "$datasetName""

echo "[DEBUG]: deepRetinotopy inference:"
cd ~/deepRetinotopy_TheToolbox/main
for hemisphere in 'lh'; # 'rh';
do 
    for map in 'polarAngle'; #'eccentricity' 'pRFsize';
    do
        echo "Hemisphere: "$hemisphere""
        for i in $(ls "$dirSubs"); do
            sudo chmod 777 $dirSubs/$i
            sudo mkdir -p  $dirSubs/$i/deepRetinotopy/
            sudo chmod 777  $dirSubs/$i/deepRetinotopy/
        done
        python 2_inference.py --path $dirSubs --dataset $datasetName --prediction_type $map --hemisphere $hemisphere
        rm -r $dirSubs/processed
    done
done
