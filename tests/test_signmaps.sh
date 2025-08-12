#!/usr/bin/env bash
set -e

echo "[DEBUG]: test deepRetinotopy on the Singularity container"
export APPTAINER_BINDPATH='/cvmfs,/mnt,/home,/data,/templates,/storage'
# source /usr/share/module.sh
module use /cvmfs/neurodesk.ardc.edu.au/neurodesk-modules/*
ml deepretinotopy

echo "[DEBUG]: test if deepRetinotopy repo is cloned"
if find .-name "deepRetinotopy" -size +0 | grep -q '.'; then
    echo "deepRetinotopy repo is cloned"
else
    echo "deepRetinotopy repo is not cloned"
fi
cp -r . /storage/deep_retinotopy/deepRetinotopy_TheToolbox/

dirSubs="/data/"
echo "Path to freesurfer data: "$dirSubs""

dirHCP="/templates/"
echo "Path to template surfaces: "$dirHCP""

datasetName="TEST"
echo "Dataset name: "$datasetName""

echo "[DEBUG]: Visual field sign maps generation"
export PATH=$PATH:/storage/deep_retinotopy/deepRetinotopy_TheToolbox/:/storage/deep_retinotopy/deepRetinotopy_TheToolbox/main/
cd /storage/deep_retinotopy/data/1/
unzip deepRetinotopy.zip
rm deepRetinotopy.zip
sudo chmod 777 -R /storage/deep_retinotopy/data/1/deepRetinotopy/

cd /storage/deep_retinotopy/deepRetinotopy_TheToolbox/main
signMaps -s $dirSubs -t $dirHCP -d $datasetName 

file_path=$dirSubs/1/deepRetinotopy/1.fs_predicted_fieldSignMap_lh_model.func.gii
if [ ! -f "$file_path" ]; then
    echo "Error: File does not exist."
    exit 1
fi

