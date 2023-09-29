#!/usr/bin/env bash
set -e

cp -r . /tmp/deepRetinotopy_TheToolbox

# test readme
echo "[DEBUG]: testing the clone command from the README:"
clone_command=`cat /tmp/deepRetinotopy_TheToolbox/README.md | grep https://github.com/felenitaribeiro/deepRetinotopy_TheToolbox.git`
echo $clone_command
$clone_command

cd deepRetinotopy_TheToolbox

# settings for data download
mkdir ./data/
mkdir ./models/

pip install osfclient
for i in {1..5};
do
    osf -p ermbz fetch /osfstorage/models/deepRetinotopy_polarAngle_LH_model"$i".pt ./model/deepRetinotopy_polarAngle_LH_model"$i".pt
done

osf -p ermbz fetch /osfstorage/models/deepRetinotopy_polarAngle_LH_* ./models/*
#TODO: repo with data

path_freesurfer_dir="./data/"
echo "Path to freesurfer data: "$path_freesurfer_dir""

path_hcp_templates_surfaces="./templates/"
echo "Path to template surfaces: "$path_hcp_templates_surfaces""

dataset_name="HCP"
echo "Dataset name: "$dataset_name""

