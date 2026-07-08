#!/bin/bash
#SBATCH --nodes=1
#SBATCH --job-name=RetMaps
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=50G
#SBATCH --account=a_ai_collab
#SBATCH --time=36:00:00
#SBATCH -o output_models.txt
#SBATCH -e error_models.txt
#SBATCH --partition=gpu_cuda
#SBATCH --qos=gpu
#SBATCH --gres=gpu:1

eval "$(conda shell.bash hook)"
conda activate deepretinotopy_2
cd ../main

# Finalized training recipe (Stage 3): ep400 / bs8 / lr0.005, grad-clip 1.0 +
# cosine LR + SWA (one averaged model per seed) + per-seed seeding. 5 seeds/hemi.
EP=400; BS=8; LR=0.005; SEEDS=5; CLIP=1.0; SWA_START=300

# 1) visualCoord: joint polar angle + eccentricity as Cartesian (x, y), Euclidean
#    loss. Replaces the separate polarAngle + eccentricity models (one forward
#    pass -> both maps). Writes provenance (config.json + trainlog.csv).
#    Output: output/<TAG>/deepRetinotopy_visualCoord_<H>_model<k>.pt
TAG="loss-euclidean_ep${EP}_bs${BS}_lr${LR}_swa"
for hemisphere in LH RH;
do
    echo "=== Training visualCoord model for $hemisphere hemisphere ==="
    python -u ./train.py --path ./../HCP/ --path2list ./../HCP/subs.txt \
        --prediction_type visualCoord --hemisphere "$hemisphere" \
        --loss euclidean --n_epochs "$EP" --batch_size "$BS" --lr "$LR" \
        --grad_clip "$CLIP" --swa --swa_start "$SWA_START" --n_seeds "$SEEDS" --tag "$TAG"
done

# 2) pRF size: single-output model, SAME hyperparameters. This is the legacy
#    (non-coordinate) path, so --loss is not used here -- it trains with the
#    built-in Smooth-L1 objective. Output: output/deepRetinotopy_pRFsize_<H>_model<k>.pt
for hemisphere in LH RH;
do
    echo "=== Training pRFsize model for $hemisphere hemisphere ==="
    python -u ./train.py --path ./../HCP/ --path2list ./../HCP/subs.txt \
        --prediction_type pRFsize --hemisphere "$hemisphere" \
        --n_epochs "$EP" --batch_size "$BS" --lr "$LR" \
        --grad_clip "$CLIP" --swa --swa_start "$SWA_START" --n_seeds "$SEEDS"
done
