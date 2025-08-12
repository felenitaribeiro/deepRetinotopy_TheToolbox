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

cd /storage/deep_retinotopy/resampling/
if [ ! -d /storage/deep_retinotopy/resampling/resampling/ ]; then
    unzip resampling.zip
else
    echo "Resampling directory already exists, skipping unzipping"
fi
sudo chmod 777 -R /storage/deep_retinotopy/resampling/
cp /storage/deep_retinotopy/resampling/resampling/* /storage/deep_retinotopy/$tmp_dir/data/1/deepRetinotopy/

dirHCP="/storage/deep_retinotopy/templates/"
echo "Path to template surfaces: "$dirHCP""

model=model
echo "Model: "$model""


echo "[DEBUG]: export excutables:"
cd /storage/deep_retinotopy/$tmp_dir/deepRetinotopy_TheToolbox/main
export PATH=$PATH:/storage/deep_retinotopy/"$tmp_dir"/deepRetinotopy_TheToolbox/:/storage/deep_retinotopy/"$tmp_dir"/deepRetinotopy_TheToolbox/main/:/storage/deep_retinotopy/"$tmp_dir"/deepRetinotopy_TheToolbox/utils/
export DEPLOY_BINS=$DEPLOY_BINS:transform_polarangle_lh.py

for hemisphere in lh; # rh; 
do
    for map in 'polarAngle'; #'eccentricity' 'pRFsize';
    do
        echo "Hemisphere: "$hemisphere""
        echo "[DEBUG]: Module 3: Resampling data back to native space..."
        # clone_command=`cat ../deepRetinotopy | grep 3_fsaverage2native.sh`
        clone_command="./3_fsaverage2native.sh -s $dirSubs -t $dirHCP -h $hemisphere -r $map -m $model"
        echo $clone_command
        eval $clone_command

        if find $dirSubs -name "*.predicted_"$map"_"$model"."$hemisphere".native.func.gii" -size +0 | grep -q '.'; then
            echo "retinotopic map in native surface space generated"
        else
            echo "retinotopic map in native surface space was not generated"
            ls -R $dirSubs
        fi
    done
done
sudo rm -rf /storage/deep_retinotopy/$tmp_dir