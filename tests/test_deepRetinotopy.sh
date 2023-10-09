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

echo "[DEBUG]: general settings:"
dirSubs="/data/"
echo "Path to freesurfer data: "$dirSubs""

dirHCP="/templates/"
echo "Path to template surfaces: "$dirHCP""

datasetName="TEST"
echo "Dataset name: "$datasetName""

maps="polarAngle,eccentricity,pRFsize"
echo "Maps: "$maps""

echo "[DEBUG]: copying models' weights from cvmfs to repo directory:"
cd /cvmfs/neurodesk.ardc.edu.au/containers/deepretinotopy_1.0.1_20231006/deepretinotopy_1.0.1_20231006.simg/opt/deepRetinotopy_TheToolbox
sudo mkdir ~/deepRetinotopy_TheToolbox/models/
sudo chmod 777 ~/deepRetinotopy_TheToolbox/

echo "[DEBUG]: testing deepRetinotopy:.sh"
cd ~/deepRetinotopy_TheToolbox/
for map in $maps;
do
    sudo cp -r models/deepRetinotopy_"$map"_* ~/deepRetinotopy_TheToolbox/models/
    for i in $(ls "$dirSubs"); do
        sudo chmod 777 $dirSubs/$i
        sudo mkdir -p  $dirSubs/$i/deepRetinotopy/
        sudo chmod 777  $dirSubs/$i/deepRetinotopy/
    done
    bash deepRetinotopy.sh -s $dirSubs -t $dirHCP -d $datasetName -m $map
    rm -r models/
done
