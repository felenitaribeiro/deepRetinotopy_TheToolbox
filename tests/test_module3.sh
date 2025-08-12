#!/usr/bin/env bash
set -e

echo "[DEBUG]: test deepRetinotopy on the Singularity container"
export APPTAINER_BINDPATH='/cvmfs,/mnt,/home,/data,/templates,/storage'
# Remove all the if/then module sourcing attempts and replace with:
export LMOD_CMD=/usr/share/lmod/lmod/libexec/lmod

# Create the module/ml function directly
module() { eval $($LMOD_CMD bash "$@") 2>/dev/null; }
export -f module

ml() { module load "$@"; }
export -f ml

# add neurodesk modules
module use /cvmfs/neurodesk.ardc.edu.au/neurodesk-modules/*
ml deepretinotopy

echo "[DEBUG]: test if deepRetinotopy repo is cloned"
if find .-name "deepRetinotopy" -size +0 | grep -q '.'; then
    echo "deepRetinotopy repo is cloned"
else
    echo "deepRetinotopy repo is not cloned"
fi
cp -r . /storage/deep_retinotopy/deepRetinotopy_TheToolbox/

echo "[DEBUG]: general settings:"
dirSubs="/storage/deep_retinotopy/data/"
echo "Path to freesurfer data: "$dirSubs""

dirHCP="/storage/deep_retinotopy/templates/"
echo "Path to template surfaces: "$dirHCP""

model=model
echo "Model: "$model""

echo "[DEBUG]: data download for resampling:"
mkdir /storage/deep_retinotopy/data/1/deepRetinotopy/
cd /storage/deep_retinotopy/resampling/
unzip resampling.zip
sudo chmod 777 -R /storage/deep_retinotopy/resampling/
sudo chmod 777 -R /storage/deep_retinotopy/data
mv /storage/deep_retinotopy/resampling/resampling/* /storage/deep_retinotopy/data/1/deepRetinotopy/

cd /storage/deep_retinotopy/deepRetinotopy_TheToolbox/main
export PATH=$PATH:/storage/deep_retinotopy/deepRetinotopy_TheToolbox/:/storage/deep_retinotopy/deepRetinotopy_TheToolbox/main/:/storage/deep_retinotopy/deepRetinotopy_TheToolbox/utils/
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

        if find /storage/deep_retinotopy/data -name "*.predicted_"$map"_"$model"."$hemisphere".native.func.gii" -size +0 | grep -q '.'; then
            echo "retinotopic map in native surface space generated"
        else
            echo "retinotopic map in native surface space was not generated"
            ls -R /storage/deep_retinotopy/data
        fi

    done
done
