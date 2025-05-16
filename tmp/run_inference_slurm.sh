#!/bin/bash
#SBATCH --nodes=1
#SBATCH --job-name=RetMaps
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=50G
#SBATCH --account=a_barth
#SBATCH --time=06:00:00
#SBATCH -o output_models_inference.txt
#SBATCH -e error_models_inference.txt
#SBATCH --partition=gpu_cuda
#SBATCH --qos=gpu
#SBATCH --gres=gpu:a100:1

eval "$(conda shell.bash hook)"
conda activate deepretinotopy_2

module use /sw/local/rocky8/noarch/neuro/software/neurocommand/local/containers/modules/
export APPTAINER_BINDPATH=/scratch,/QRISdata

ml connectomeworkbench/1.5.0
ml freesurfer/7.3.2

cd ..

PATH=$PATH:/scratch/project/recyle_dl/deepRetinotopy_TheToolbox/:/scratch/project/recyle_dl/deepRetinotopy_TheToolbox/main/:/scratch/project/recyle_dl/deepRetinotopy_TheToolbox/utils/
export PATH
DEPLOY_BINS="1_native2fsaverage.sh:2_inference.py:3_fsaverage2native.sh:4_signmaps.py:transform_polarangle_lh.py:midthickness_surf.py"
export DEPLOY_BINS

./deepRetinotopy -s /scratch/project/recyle_dl/deepRetinotopy_TheToolbox/HCP/freesurfer/ -t /scratch/project/recyle_dl/deepRetinotopy_TheToolbox/templates/ -d hcp -m 'polarAngle,eccentricity,pRFsize'