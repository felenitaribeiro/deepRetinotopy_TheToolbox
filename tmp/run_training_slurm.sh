#!/bin/bash
#SBATCH --nodes=1
#SBATCH --job-name=RetMaps
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=50G
#SBATCH --account=a_barth
#SBATCH --time=36:00:00
#SBATCH -o output_models.txt
#SBATCH -e error_models.txt
#SBATCH --partition=gpu_cuda
#SBATCH --qos=gpu
#SBATCH --gres=gpu:1

eval "$(conda shell.bash hook)"
conda activate deepretinotopy_2
cd ../main

for prediction_type in polarAngle eccentricity pRFsize;
do
    for hemisphere in LH RH; 
    do
        echo Training $prediction_type models for $hemisphere hemisphere
        python -u ./train.py --path ./../HCP/ --path2list ./../HCP/subs.txt --prediction_type $prediction_type --hemisphere $hemisphere
    done
done
