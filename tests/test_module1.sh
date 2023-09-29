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

# pip install osfclient
#TODO: repo with data


$dirSubs="./data/"
echo "Path to freesurfer data: "$dirSubs""

$dirHCP ="./templates/"
echo "Path to template surfaces: "$dirHCP ""

$hemisphere="LH"
echo "Dataset name: "$hemisphere""

echo "[DEBUG]: Module 1: Generating mid-thickness surface and curvature data..."
clone_command=`cat /tmp/deepRetinotopy_TheToolbox/deepRetinotopy.sh | grep 1_native2fsaverage.sh`
echo $clone_command
$clone_command
