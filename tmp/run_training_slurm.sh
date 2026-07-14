#!/bin/bash
#SBATCH --nodes=1
#SBATCH --job-name=RetMaps
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=80G
#SBATCH --account=a_ai_collab
#SBATCH --time=48:00:00
#SBATCH -o output_models.txt
#SBATCH -e error_models.txt
#SBATCH --partition=gpu_cuda
#SBATCH --qos=gpu
#SBATCH --gres=gpu:h100:1     # full H100 -- whole brain is ~20x the edges of the
                              # old ROI; "gpu:1" can land on a slow A100 MIG slice.

eval "$(conda shell.bash hook)"
conda activate deepretinotopy_2
cd ../main

# Finalized training recipe (Stage 3): ep400 / bs8 / lr0.005, grad-clip 1.0 +
# cosine LR + SWA (one averaged model per seed) + per-seed seeding. 5 seeds/hemi.
# ROI = WHOLE BRAIN (all 32492 vertices/hemisphere -- the new toolbox default),
# passed explicitly so the run is reproducible regardless of the code default.
EP=400; BS=8; LR=0.005; SEEDS=5; CLIP=1.0; SWA_START=300
ROI=wholebrain

# 1) visualCoord: joint polar angle + eccentricity as Cartesian (x, y), Euclidean
#    loss. Replaces the separate polarAngle + eccentricity models (one forward
#    pass -> both maps). Writes provenance (config.json + trainlog.csv).
#    Output: output/<TAG>/deepRetinotopy_visualCoord_<H>_model<k>.pt
#    TAG is ROI-namespaced so whole-brain weights never collide with / overwrite
#    the wang_fovea baseline in output/loss-euclidean_...swa/.
TAG="roi-${ROI}_ep${EP}_bs${BS}_lr${LR}_swa"
for hemisphere in LH RH;
do
    echo "=== Training visualCoord model ($ROI) for $hemisphere hemisphere ==="
    python -u ./train.py --path ./../HCP/ --path2list ./../HCP/subs.txt \
        --roi "$ROI" --prediction_type visualCoord --hemisphere "$hemisphere" \
        --n_epochs "$EP" --batch_size "$BS" --lr "$LR" \
        --grad_clip "$CLIP" --swa --swa_start "$SWA_START" --n_seeds "$SEEDS" --tag "$TAG"
done

# 2) pRF size: single-output model, SAME hyperparameters. Single-output maps
#    always train with the legacy Smooth-L1 objective (fixed by prediction_type,
#    no loss flag). With --tag the weights go to output/<TAG>/ alongside the
#    visualCoord models; provenance in output/<TAG>/config_pRFsize_<H>.json.
for hemisphere in LH RH;
do
    echo "=== Training pRFsize model ($ROI) for $hemisphere hemisphere ==="
    python -u ./train.py --path ./../HCP/ --path2list ./../HCP/subs.txt \
        --roi "$ROI" --prediction_type pRFsize --hemisphere "$hemisphere" \
        --n_epochs "$EP" --batch_size "$BS" --lr "$LR" \
        --grad_clip "$CLIP" --swa --swa_start "$SWA_START" --n_seeds "$SEEDS" --tag "$TAG"
done
