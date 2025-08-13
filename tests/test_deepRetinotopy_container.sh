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

echo "[DEBUG]: testing deepRetinotopy:"
for map in "${maps[@]}";
do
    for i in $(ls "$dirSubs"); do
        sudo chmod 777 $dirSubs/$i
        sudo mkdir -p  $dirSubs/$i/deepRetinotopy/
        sudo chmod 777  $dirSubs/$i/deepRetinotopy/
    done
    
    deepRetinotopy -s $dirSubs -t $dirHCP -d $datasetName -m $map
done
