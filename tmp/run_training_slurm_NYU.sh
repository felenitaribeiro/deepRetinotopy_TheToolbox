#!/bin/bash
#SBATCH --nodes=1
#SBATCH --job-name=RetMaps
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=50G
#SBATCH --account=a_barth
#SBATCH --time=01:00:00
#SBATCH -o output_model_nyu.txt
#SBATCH -e error_model_nyu.txt
#SBATCH --partition=gpu_cuda
#SBATCH --qos=gpu
#SBATCH --gres=gpu:a100:1

eval "$(conda shell.bash hook)"
conda activate deepretinotopy_2
cd ../main

for prediction_type in pRFsize;
do
    for hemisphere in LH RH; 
    do
        echo Training $prediction_type models for $hemisphere hemisphere
        python -u ./train.py --path ./../NYU/BULK/LABDATA/openneuro/ds003787/derivatives/ --path2list ./../NYU/BULK/LABDATA/openneuro/ds003787/derivatives/subs.txt --prediction_type $prediction_type --hemisphere $hemisphere --dataset NYU --n_seeds 1 --loss probabilistic
    done
done
