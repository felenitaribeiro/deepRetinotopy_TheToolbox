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
sudo mkdir -p /storage/deep_retinotopy/deepRetinotopy_TheToolbox/
cp -r . /storage/deep_retinotopy/deepRetinotopy_TheToolbox/

echo "[DEBUG]: general settings:"
dirSubs="/storage/deep_retinotopy/data/"
echo "Path to freesurfer data: "$dirSubs""

dirHCP="/storage/deep_retinotopy/templates/"
echo "Path to template surfaces: "$dirHCP""

datasetName="TEST"
echo "Dataset name: "$datasetName""

list_of_maps="polarAngle,eccentricity,pRFsize"
IFS=',' read -ra maps <<< "$list_of_maps"
echo "Maps: "${maps[@]}""

echo "[DEBUG]: copying models' weights from cvmfs to repo directory:"
sudo mkdir -p /storage/deep_retinotopy/deepRetinotopy_TheToolbox/models/
sudo chmod 777 /storage/deep_retinotopy/deepRetinotopy_TheToolbox/

echo "[DEBUG]: testing deepRetinotopy:"
cd /storage/deep_retinotopy/deepRetinotopy_TheToolbox/
var=`cat ./README.md | grep date_tag=`
echo $var
export $var

echo $DEPLOY_BINS
export PATH=/storage/deep_retinotopy/deepRetinotopy_TheToolbox/:/storage/deep_retinotopy/deepRetinotopy_TheToolbox/main/:/storage/deep_retinotopy/deepRetinotopy_TheToolbox/utils/:$PATH
export DEPLOY_BINS=wb_view:wb_command:wb_shortcuts:python:deepRetinotopy:signMaps:1_native2fsaverage.sh:2_inference.py:3_fsaverage2native.sh:4_signmaps.py:transform_polarangle_lh.py:midthickness_surf.py
echo $DEPLOY_BINS
which deepRetinotopy

#find path of deepRetinotopy executable
deepRetinotopy_executable=$(which deepRetinotopy)
echo $deepRetinotopy_executable

#remove executable name from $deepRetinotopy_path
deepRetinotopy_path=${deepRetinotopy_executable%/*}
echo $deepRetinotopy_path

#extract the last directory of $deepRetinotopy_path
deepRetinotopy_last_dir=${deepRetinotopy_path##*/}
echo $deepRetinotopy_last_dir

for map in "${maps[@]}";
do
    sudo cp -r $deepRetinotopy_path/$deepRetinotopy_last_dir.simg/opt/deepRetinotopy_TheToolbox/models/deepRetinotopy_"$map"_* /storage/deep_retinotopy/deepRetinotopy_TheToolbox/models/
    for i in $(ls "$dirSubs"); do
        sudo chmod 777 $dirSubs/$i
        sudo mkdir -p  $dirSubs/$i/deepRetinotopy/
        sudo chmod 777  $dirSubs/$i/deepRetinotopy/
    done
    
    deepRetinotopy -s $dirSubs -t $dirHCP -d $datasetName -m $map
    sudo rm -r /storage/deep_retinotopy/deepRetinotopy_TheToolbox/models/*
done
