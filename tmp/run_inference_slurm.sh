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
# SELECTION run: loops all N_MODELS seeds symlinked in ./models/ as
# deepRetinotopy_<type>_<H>_model{1..N}.pt (default model_dir), writing one output
# per seed. Evaluate seeds, then deploy the chosen one as a seedless _model.pt for
# the container (which runs --num_of_models 1).
eval "$(conda shell.bash hook)"
conda activate deepretinotopy_2

REPO=/scratch/project/recyle_dl/deepRetinotopy_TheToolbox
FS="$REPO/HCP/freesurfer/"                 # subjects dir (needs curvature files from Step 1)
cd "$REPO/main"

N_MODELS=5                                  # number of seeds per hemisphere in ./models/

for H in lh rh;
do
    echo "=== visualCoord inference ($H, $N_MODELS seeds) -> polarAngle + eccentricity ==="
    # outputs: <sub>.fs_predicted_{polarAngle,eccentricity,x,y}_${H}_curvatureFeat_visualCoord-model{1..N}.func.gii
    python -u ./2_inference.py --path "$FS" --dataset hcp \
        --prediction_type visualCoord --hemisphere "$H" --num_features 1 \
        --num_of_models "$N_MODELS"

    echo "=== pRFsize inference ($H, $N_MODELS seeds) ==="
    # outputs: <sub>.fs_predicted_pRFsize_${H}_curvatureFeat_pRFsize-model{1..N}.func.gii
    python -u ./2_inference.py --path "$FS" --dataset hcp \
        --prediction_type pRFsize --hemisphere "$H" --num_features 1 \
        --num_of_models "$N_MODELS"
done

# After selecting a seed, deploy it seedless for the container CLI, e.g.:
#   ln -sfn <target>/deepRetinotopy_visualCoord_LH_model3.pt \
#           models/deepRetinotopy_visualCoord_LH_model.pt
# then the toolbox default (--num_of_models 1) picks it up.
