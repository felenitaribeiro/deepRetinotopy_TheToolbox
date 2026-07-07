#!/bin/bash
#SBATCH --nodes=1
#SBATCH --job-name=RetInfer
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=50G
#SBATCH --account=a_ai_collab
#SBATCH --time=06:00:00
#SBATCH -o output_models_inference.txt
#SBATCH -e error_models_inference.txt
#SBATCH --partition=gpu_cuda
#SBATCH --qos=gpu
#SBATCH --gres=gpu:1

# Direct inference with 2_inference.py (pipeline Step 2 only): writes predicted
# maps into each subject's deepRetinotopy/ folder, in fsaverage curvature-feature
# space. Assumes Step 1 outputs (midthickness surfaces + curvature) already exist;
# for native-space maps run 3_fsaverage2native.sh separately (see the toolbox CLI).
#   visualCoord model -> predicted polarAngle + eccentricity (one forward pass)
#   pRFsize     model -> predicted pRFsize
eval "$(conda shell.bash hook)"
conda activate deepretinotopy_2

REPO=/scratch/project/recyle_dl/deepRetinotopy_TheToolbox
FS="$REPO/HCP/freesurfer/"                 # subjects dir (needs curvature files from Step 1)
cd "$REPO/main"

# Trained-model locations. --num_of_models N runs the per-seed files
# model1..modelN found in --model_dir, writing one output per seed.
EP=400; BS=8; LR=0.005; N_MODELS=5
VC_DIR="$REPO/main/output/loss-euclidean_ep${EP}_bs${BS}_lr${LR}_swa"  # visualCoord seeds
PRF_DIR="$REPO/main/output"                                            # pRFsize seeds
VC_TAG="visualCoord"                       # visualCoord output token -> <tag>_model<i> per seed

for H in lh rh;
do
    echo "=== visualCoord inference ($H, $N_MODELS seeds) -> polarAngle + eccentricity ==="
    # outputs: <sub>.fs_predicted_{polarAngle,eccentricity}_${H}_curvatureFeat_${VC_TAG}_model{1..N}.func.gii
    python -u ./2_inference.py --path "$FS" --dataset hcp \
        --prediction_type visualCoord --hemisphere "$H" --num_features 1 \
        --model_dir "$VC_DIR" --num_of_models "$N_MODELS" --tag "$VC_TAG"

    echo "=== pRFsize inference ($H, $N_MODELS seeds) ==="
    # outputs: <sub>.fs_predicted_pRFsize_${H}_curvatureFeat_model{1..N}.func.gii
    python -u ./2_inference.py --path "$FS" --dataset hcp \
        --prediction_type pRFsize --hemisphere "$H" --num_features 1 \
        --model_dir "$PRF_DIR" --num_of_models "$N_MODELS"
done

# For a SINGLE deployed model instead of all seeds: use the toolbox models/ dir
# (models/deepRetinotopy_<type>_<H>_model.pt) with default --num_of_models 1, or
# pass --model_path <one .pt> explicitly.
