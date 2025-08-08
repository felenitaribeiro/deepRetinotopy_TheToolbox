#!/usr/bin/env bash
set -e

export APPTAINER_BINDPATH='/cvmfs,/mnt,/home,/data,/templates'
source /usr/share/module.sh
module use /cvmfs/neurodesk.ardc.edu.au/neurodesk-modules/*
ml deepretinotopy/1.0.11

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

model=model
echo "Model: "$model""

echo "[DEBUG]: data download for resampling:"
mkdir /data/1/deepRetinotopy/
cd /resampling/
unzip resampling.zip
sudo chmod 777 -R /resampling/
sudo chmod 777 -R /data
mv /resampling/resampling/* /data/1/deepRetinotopy/

cd ~/deepRetinotopy_TheToolbox/main
export PATH=$PATH:~/deepRetinotopy_TheToolbox/:~/deepRetinotopy_TheToolbox/main/:~/deepRetinotopy_TheToolbox/utils/
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

        if find /data -name "*.predicted_"$map"_"$model"."$hemisphere".native.func.gii" -size +0 | grep -q '.'; then
            echo "retinotopic map in native surface space generated"
        else
            echo "retinotopic map in native surface space was not generated"
            ls -R /data
        fi

    done
done
