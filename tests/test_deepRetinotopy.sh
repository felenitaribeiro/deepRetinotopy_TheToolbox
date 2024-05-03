#!/usr/bin/env bash
set -e

echo "[DEBUG]: test deepRetinotopy on the Singularity container"
export APPTAINER_BINDPATH='/cvmfs,/mnt,/home,/data,/templates'
source /usr/share/module.sh
module use /cvmfs/neurodesk.ardc.edu.au/neurodesk-modules/*
ml deepretinotopy/1.0.2

echo "[DEBUG]: test if deepRetinotopy repo is cloned"
if find .-name "deepRetinotopy" -size +0 | grep -q '.'; then
    echo "deepRetinotopy repo is cloned"
else
    echo "deepRetinotopy repo is not cloned"
fi
cp -r . ~/deepRetinotopy_TheToolbox/

echo "[DEBUG]: general settings:"
dirSubs="/data/"
echo "Path to freesurfer data: "$dirSubs""

dirHCP="/templates/"
echo "Path to template surfaces: "$dirHCP""

datasetName="TEST"
echo "Dataset name: "$datasetName""

list_of_maps="polarAngle,eccentricity,pRFsize"
IFS=',' read -ra maps <<< "$list_of_maps"
echo "Maps: "${maps[@]}""

echo "[DEBUG]: copying models' weights from cvmfs to repo directory:"
sudo mkdir ~/deepRetinotopy_TheToolbox/models/
sudo chmod 777 ~/deepRetinotopy_TheToolbox/

echo "[DEBUG]: testing deepRetinotopy:"
cd ~/deepRetinotopy_TheToolbox/
var=`cat ./README.md | grep date_tag=`
echo $var
export $var

for map in "${maps[@]}";
do
    sudo cp -r /cvmfs/neurodesk.ardc.edu.au/containers/deepretinotopy_1.0.2_"$date_tag"/deepretinotopy_1.0.2_"$date_tag".simg/opt/deepRetinotopy_TheToolbox/models/deepRetinotopy_"$map"_* ~/deepRetinotopy_TheToolbox/models/
    for i in $(ls "$dirSubs"); do
        sudo chmod 777 $dirSubs/$i
        sudo mkdir -p  $dirSubs/$i/deepRetinotopy/
        sudo chmod 777  $dirSubs/$i/deepRetinotopy/
    done
    export PATH=$PATH:~/deepRetinotopy_TheToolbox/main/
    deepRetinotopy -s $dirSubs -t $dirHCP -d $datasetName -m $map
    sudo rm -r ~/deepRetinotopy_TheToolbox/models/*
done
