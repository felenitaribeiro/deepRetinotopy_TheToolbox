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

# Inference (pipeline Step 2 only) for the myelin+curvature BENCHMARK models:
# separate polarAngle / eccentricity / pRFsize models trained by
# run_training-beta_slurm.sh with --num_features 2 (single seed, whole brain).
# Writes predicted maps into each subject's deepRetinotopy/ folder with a
# "myelincurvFeat" filename token, alongside -- never overwriting -- the
# curvature-only baseline predictions ("curvatureFeat"). Assumes Step 1 outputs
# (midthickness surfaces + curvature) already exist; for native-space maps run
# 3_fsaverage2native.sh separately (see the toolbox CLI).
#
# --dataset must NOT be 'HCP': that selects the training-only read_HCP branch,
# which needs raw/converted .mat files under the temp processed dir (crashes)
# and hard-codes the 161/10/10 split. Any other name selects read_gifti, which
# reads per-subject GIFTIs via the temp symlinks -- curvature plus, for
# --num_features 2, the myelin maps exported by tmp/make_myelin_giftis.py
# (<sub>.myelinmap-midthickness.<h>.32k_fs_LR.func.gii, from the same
# cifti_myelin_all.mat used in training).
eval "$(conda shell.bash hook)"
conda activate deepretinotopy_2

REPO=/scratch/project/recyle_dl/deepRetinotopy_TheToolbox
FS="$REPO/HCP/freesurfer/"                 # subjects dir (needs curvature files from Step 1)
MODEL_DIR="$REPO/main/output/roi-wholebrain_ep400_bs8_lr0.005_swa_myelincurv"
cd "$REPO/main"

N_MODELS=1

# Training saves per-seed weights (..._model1.pt), but --num_of_models 1 loads
# the seedless name (..._model.pt). Link the single seed to the seedless name;
# a symlink keeps the original file matched to its trainlog/config provenance.
for type in polarAngle eccentricity pRFsize; do
    for HU in LH RH; do
        seed_file="$MODEL_DIR/deepRetinotopy_${type}_${HU}_model1.pt"
        if [ -f "$seed_file" ]; then
            ln -sfn "$(basename "$seed_file")" \
                    "$MODEL_DIR/deepRetinotopy_${type}_${HU}_model.pt"
        else
            echo "WARNING: missing $seed_file -- has training finished?" >&2
        fi
    done
done

for H in lh rh;
do
    for type in polarAngle eccentricity pRFsize;
    do
        echo "=== $type inference ($H, myelin+curv) ==="
        # output: <sub>.fs_predicted_${type}_${H}_myelincurvFeat_${type}-model.func.gii
        python -u ./2_inference.py --path "$FS" --dataset benchmark \
            --prediction_type "$type" --hemisphere "$H" --num_features 2 \
            --num_of_models "$N_MODELS" --model_dir "$MODEL_DIR"
    done
done

# Legacy single-map polarAngle models train on +/-180-shifted LH targets, so
# their LH predictions are in the shifted frame -- the SAME frame as the
# fs_empirical_polarAngle_lh GIFTIs (compare raw vs those directly). This step
# writes unshifted copies (..._polarAngle-model_transformed.func.gii) in the
# visualCoord/native-space frame, for comparison against the visualCoord
# baseline maps. Raw files are left untouched; RH is never shifted.
echo "=== LH polarAngle post-hoc transform (unshift) ==="
python -u ../tmp/transform_polarangle_lh_fsaverage.py --path "$FS" \
    --feat myelincurvFeat --model polarAngle-model
