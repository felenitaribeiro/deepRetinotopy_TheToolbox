#!/bin/bash
#SBATCH --nodes=1
#SBATCH --job-name=RetMaps
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=50G
#SBATCH --account=a_barth
#SBATCH --time=00:30:00
#SBATCH -o output_models_myelincurv.txt
#SBATCH -e error_models_myelincurv.txt
#SBATCH --partition=gpu_cuda
#SBATCH --qos=gpu
#SBATCH --gres=gpu:a100:1

eval "$(conda shell.bash hook)"
conda activate deepretinotopy_2
cd ../main

# for prediction_type in polarAngle eccentricity pRFsize;
# do
#     for hemisphere in LH RH; 
#     do
#         echo Training $prediction_type models for $hemisphere hemisphere
#         python -u ./train.py --path ./../HCP/ --path2list ./../HCP/subs.txt --prediction_type $prediction_type --hemisphere $hemisphere --num_features 2 --n_seeds 1
#     done
# done

for prediction_type in polarAngle eccentricity pRFsize;
do
    for hemisphere in lh; # LH RH for training
    do
        echo Training $prediction_type models for $hemisphere hemisphere
        rm -r ./../HCP/freesurfer/processed/
        python ./../main/2_inference.py --path ./../HCP/freesurfer/ --dataset hcp --prediction_type $prediction_type --hemisphere $hemisphere --num_features 2 
        rm -r ./../HCP/freesurfer/processed/
    done
done