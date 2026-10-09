#!/bin/bash
# Download HCP S1200 structural files needed for the spherereg re-expression task.
# Usage: download_subject.sh <sub> [pilot]   ("pilot" adds 32k sphere + 32k MSMAll myelin for checks)
set -e
sub=$1
pilot=$2
WORK=/scratch/project_mnt/S0210/deepRetinotopy_TheToolbox/sandbox/spherereg_targets
dest=$WORK/hcp/$sub
mkdir -p $dest
S3=s3://hcp-openaccess/HCP_1200/$sub/MNINonLinear
get() { [ -s "$dest/$(basename $1)" ] || aws s3 cp "$1" "$dest/" --only-show-errors; }
for H in L R; do
  get $S3/Native/$sub.$H.sphere.MSMAll.native.surf.gii
  get $S3/Native/$sub.$H.midthickness.native.surf.gii
  get $S3/fsaverage_LR32k/$sub.$H.midthickness_MSMAll.32k_fs_LR.surf.gii
done
get $S3/Native/$sub.MyelinMap_BC.native.dscalar.nii
if [ "$pilot" == "pilot" ]; then
  for H in L R; do get $S3/fsaverage_LR32k/$sub.$H.sphere.32k_fs_LR.surf.gii; done
  get $S3/fsaverage_LR32k/$sub.MyelinMap_BC_MSMAll.32k_fs_LR.dscalar.nii
fi
echo "done $sub"
