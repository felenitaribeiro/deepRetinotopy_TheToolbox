#!/bin/bash
#SBATCH --nodes=1
#SBATCH --job-name=RetMaps
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=50G
#SBATCH --account=a_barth
#SBATCH --time=06:00:00
#SBATCH -o output_models_inference_nyu.txt
#SBATCH -e error_models_inference_nyu.txt
#SBATCH --partition=gpu_cuda
#SBATCH --qos=gpu
#SBATCH --gres=gpu:a100:1

eval "$(conda shell.bash hook)"
conda activate deepretinotopy_2
cd ../main

for prediction_type in polarAngle eccentricity pRFsize;
do
    for hemisphere in lh rh; 
    do
        echo Training $prediction_type models for $hemisphere hemisphere
        python ./../main/2_inference.py --path ./../NYU/BULK/LABDATA/openneuro/ds003787/derivatives/freesurfer/ --dataset nyu --prediction_type $prediction_type --hemisphere $hemisphere --stimulus bars
        rm -r ./../NYU/BULK/LABDATA/openneuro/ds003787/derivatives/freesurfer/processed/
    done
done
