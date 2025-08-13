#!/usr/bin/env bash
set -e

echo "[DEBUG]: General configuration for testing deepRetinotopy "
# Get the directory where the current script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Source the file from that directory
source "$SCRIPT_DIR/test_cvmfs.sh"
ml deepretinotopy

echo "[DEBUG]: data paths:"
dirSubs="/storage/deep_retinotopy/$tmp_dir/data"
echo "Path to freesurfer data: "$dirSubs""
sudo mkdir -p $dirSubs
sudo chmod 777 $dirSubs
cp -r /storage/deep_retinotopy/data/* $dirSubs

dirHCP="/storage/deep_retinotopy/templates/"
echo "Path to template surfaces: "$dirHCP""

datasetName="TEST"
echo "Dataset name: "$datasetName""

echo "[DEBUG]: Visual field sign maps generation"
export PATH=$PATH:/storage/deep_retinotopy/"$tmp_dir"/deepRetinotopy_TheToolbox/:/storage/deep_retinotopy/"$tmp_dir"/deepRetinotopy_TheToolbox/main/
cd $dirSubs/1/
if [ ! -d $dirSubs/1/deepRetinotopy/ ]; then
    unzip deepRetinotopy.zip
else
    echo "deepRetinotopy directory already exists, skipping unzipping"
fi
sudo chmod 777 -R $dirSubs/1/deepRetinotopy/

cd /storage/deep_retinotopy/"$tmp_dir"/deepRetinotopy_TheToolbox/main
signMaps -s $dirSubs -t $dirHCP -d $datasetName 

file_path=$dirSubs/1/deepRetinotopy/1.fs_predicted_fieldSignMap_lh_model.func.gii
if [ ! -f "$file_path" ]; then
    echo "Error: File does not exist."
    exit 1
fi

