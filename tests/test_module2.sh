#!/usr/bin/env bash
set -e

echo "[DEBUG]: General configuration for testing deepRetinotopy "
# Get the directory where the current script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Source the file from that directory
source "$SCRIPT_DIR/test_cvmfs.sh"
ml deepretinotopy

echo "[DEBUG]: data paths:"
#find path of deepRetinotopy executable
deepRetinotopy_executable=$(which deepRetinotopy)
echo $deepRetinotopy_executable

#remove executable name from $deepRetinotopy_path
deepRetinotopy_path=${deepRetinotopy_executable%/*}
echo $deepRetinotopy_path

#extract the last directory of $deepRetinotopy_path
deepRetinotopy_last_dir=${deepRetinotopy_path##*/}
echo $deepRetinotopy_last_dir

cd $deepRetinotopy_path/$deepRetinotopy_last_dir.simg/opt/deepRetinotopy_TheToolbox
sudo mkdir /storage/deep_retinotopy/$tmp_dir/deepRetinotopy_TheToolbox/models/
sudo chmod 777 /storage/deep_retinotopy/$tmp_dir/deepRetinotopy_TheToolbox/
sudo cp -r models/deepRetinotopy_polarAngle_LH_* /storage/deep_retinotopy/$tmp_dir/deepRetinotopy_TheToolbox/models/

dirSubs="/storage/deep_retinotopy/$tmp_dir/data"
echo "Path to freesurfer data: "$dirSubs""
sudo mkdir -p $dirSubs
sudo chmod 777 $dirSubs
cp -r /storage/deep_retinotopy/data/* $dirSubs

dirHCP="/storage/deep_retinotopy/templates/"
echo "Path to template surfaces: "$dirHCP""

datasetName="TEST"
echo "Dataset name: "$datasetName""


echo "[DEBUG]: deepRetinotopy inference:"
export PATH=$PATH:/storage/deep_retinotopy/"$tmp_dir"/deepRetinotopy_TheToolbox/:/storage/deep_retinotopy/"$tmp_dir"/deepRetinotopy_TheToolbox/main/
cd /storage/deep_retinotopy/$tmp_dir/deepRetinotopy_TheToolbox/main
for hemisphere in 'lh'; # 'rh';
do 
    for map in 'polarAngle'; #'eccentricity' 'pRFsize';
    do
        echo "Hemisphere: "$hemisphere""
        for i in $(ls "$dirSubs"); do
            sudo chmod 777 $dirSubs/$i
            sudo mkdir -p  $dirSubs/$i/deepRetinotopy/
            sudo chmod 777  $dirSubs/$i/deepRetinotopy/
            ls $dirSubs/$i/surf/
        done
        python ./2_inference.py --path $dirSubs --dataset $datasetName --prediction_type $map --hemisphere $hemisphere
        sudo rm -r $dirSubs/processed
    done
done
sudo rm -rf /storage/deep_retinotopy/$tmp_dir