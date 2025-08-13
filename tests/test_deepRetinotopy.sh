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

list_of_maps="polarAngle,eccentricity,pRFsize"
IFS=',' read -ra maps <<< "$list_of_maps"
echo "Maps: "${maps[@]}""

echo "[DEBUG]: copying models' weights from cvmfs to repo directory:"
sudo mkdir -p /storage/deep_retinotopy/"$tmp_dir"/deepRetinotopy_TheToolbox/models/
sudo chmod 777 /storage/deep_retinotopy/"$tmp_dir"/deepRetinotopy_TheToolbox/

echo "[DEBUG]: testing deepRetinotopy:"
cd /storage/deep_retinotopy/"$tmp_dir"/deepRetinotopy_TheToolbox/
var=`cat ./README.md | grep date_tag=`
echo $var
export $var

#find path of deepRetinotopy executable
deepRetinotopy_executable=$(which deepRetinotopy)
echo $deepRetinotopy_executable

echo $DEPLOY_BINS
export PATH=/storage/deep_retinotopy/"$tmp_dir"/deepRetinotopy_TheToolbox/:/storage/deep_retinotopy/"$tmp_dir"/deepRetinotopy_TheToolbox/main/:/storage/deep_retinotopy/"$tmp_dir"/deepRetinotopy_TheToolbox/utils/:$PATH
export DEPLOY_BINS=wb_view:wb_command:wb_shortcuts:python:deepRetinotopy:signMaps:1_native2fsaverage.sh:2_inference.py:3_fsaverage2native.sh:4_signmaps.py:transform_polarangle_lh.py:midthickness_surf.py
echo $DEPLOY_BINS

#remove executable name from $deepRetinotopy_path
deepRetinotopy_path=${deepRetinotopy_executable%/*}
echo $deepRetinotopy_path

#extract the last directory of $deepRetinotopy_path
deepRetinotopy_last_dir=${deepRetinotopy_path##*/}
echo $deepRetinotopy_last_dir

for map in "${maps[@]}";
do
    # Only copy if the model files don't already exist in the destination
    if ! ls /storage/deep_retinotopy/"$tmp_dir"/deepRetinotopy_TheToolbox/models/deepRetinotopy_"$map"_* 1> /dev/null 2>&1; then
        echo "No deepRetinotopy_${map} model files found in destination, copying..."
        sudo cp -r $deepRetinotopy_path/$deepRetinotopy_last_dir.simg/opt/deepRetinotopy_TheToolbox/models/deepRetinotopy_"$map"_* /storage/deep_retinotopy/"$tmp_dir"/deepRetinotopy_TheToolbox/models/
    else
        echo "deepRetinotopy_${map} model files already exist in destination, skipping copy"
    fi

    for i in $(ls "$dirSubs"); do
        sudo chmod 777 $dirSubs/$i
        sudo mkdir -p  $dirSubs/$i/deepRetinotopy/
        sudo chmod 777  $dirSubs/$i/deepRetinotopy/
    done
    
    deepRetinotopy -s $dirSubs -t $dirHCP -d $datasetName -m $map
    sudo rm -r /storage/deep_retinotopy/"$tmp_dir"/deepRetinotopy_TheToolbox/models/*
done
sudo rm -rf /storage/deep_retinotopy/$tmp_dir