#!/usr/bin/env bash
set -e

echo "[DEBUG]: test deepRetinotopy on the Singularity container"
export APPTAINER_BINDPATH='/cvmfs,/mnt,/home,/data,/templates'
source /usr/share/module.sh
module use /cvmfs/neurodesk.ardc.edu.au/neurodesk-modules/*
ml deepretinotopy/1.0.5

echo "[DEBUG]: test if deepRetinotopy repo is cloned"
if find .-name "deepRetinotopy" -size +0 | grep -q '.'; then
    echo "deepRetinotopy repo is cloned"
else
    echo "deepRetinotopy repo is not cloned"
fi
cp -r . ~/deepRetinotopy_TheToolbox/

echo "[DEBUG]: copying models' weights from cvmfs to repo directory:"
var=`cat ./README.md | grep date_tag=`
echo $var
export $var

sudo mkdir ~/deepRetinotopy_TheToolbox/models/
sudo chmod 777 ~/deepRetinotopy_TheToolbox/
sudo cp -r /cvmfs/neurodesk.ardc.edu.au/containers/deepretinotopy_1.0.5_"$date_tag"/deepretinotopy_1.0.5_"$date_tag".simg/opt/deepRetinotopy_TheToolbox/models/deepRetinotopy_polarAngle_* ~/deepRetinotopy_TheToolbox/models/
sudo cp -r /cvmfs/neurodesk.ardc.edu.au/containers/deepretinotopy_1.0.5_"$date_tag"/deepretinotopy_1.0.5_"$date_tag".simg/opt/deepRetinotopy_TheToolbox/models/deepRetinotopy_eccentricity_* ~/deepRetinotopy_TheToolbox/models/

echo "[DEBUG]: general settings:"
dirSubs="/data/"
echo "Path to freesurfer data: "$dirSubs""

dirHCP="/templates/"
echo "Path to template surfaces: "$dirHCP""

datasetName="TEST"
echo "Dataset name: "$datasetName""

echo "[DEBUG]: deepRetinotopy inference:"
export PATH=~/deepRetinotopy_TheToolbox/:~/deepRetinotopy_TheToolbox/main/:$PATH
which deepRetinotopy

cd ~/deepRetinotopy_TheToolbox/main
for hemisphere in 'lh' 'rh';
do 
    for map in 'polarAngle' 'eccentricity'; # 'pRFsize';
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

echo "[DEBUG]: Visual field sign maps generation"
signMaps -s $dirSubs -t $dirHCP -d $datasetName 
ls -R test_data/100610/deepRetinotopy/*Sign*
