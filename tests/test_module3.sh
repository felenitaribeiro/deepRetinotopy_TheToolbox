#!/usr/bin/env bash
set -e

export APPTAINER_BINDPATH='/cvmfs,/mnt,/home,/data,/templates'
source /usr/share/module.sh
module use /cvmfs/neurodesk.ardc.edu.au/neurodesk-modules/*
ml deepretinotopy/1.0.1

echo "[DEBUG]: test if deepRetinotopy repo is cloned"
ls
cp -r . /tmp/deepRetinotopy_TheToolbox
cd ~

# test readme
echo "[DEBUG]: testing the clone command from the README:"
clone_command=`cat /tmp/deepRetinotopy_TheToolbox/README.md | grep https://github.com/felenitaribeiro/deepRetinotopy_TheToolbox.git`
echo $clone_command
$clone_command

dirSubs="/data/"
echo "Path to freesurfer data: "$dirSubs""

dirHCP="/templates/"
echo "Path to template surfaces: "$dirHCP""

model=average
echo "Model: "$model""

echo "[DEBUG]: data download for resampling:"
mkdir /data/1/deepRetinotopy/
cd /resampling/
unzip resampling.zip
sudo chmod 777 -R /resampling/
sudo chmod 777 -R /data
mv /resampling/resampling/* /data/1/deepRetinotopy/

cd ~/deepRetinotopy_TheToolbox/main
for hemisphere in lh; # rh; 
do
    for map in 'polarAngle'; #'eccentricity' 'pRFsize';
    do
        echo "Hemisphere: "$hemisphere""
        echo "[DEBUG]: Module 3: Resampling data back to native space..."
        clone_command=`cat ../deepRetinotopy.sh | grep 3_fsaverage2native.sh`
        echo $clone_command
        eval $clone_command

        if find /data -name "*.predicted_"$map"_"$model"."$hemisphere".native.func.gii " -size +0 | grep -q '.'; then
            echo "retinotopic map in native surface space generated"
        else
            echo "retinotopic map in native surface space not generated"
            ls -R /data
        fi

    done
done
