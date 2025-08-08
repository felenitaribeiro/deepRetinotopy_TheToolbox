#!/usr/bin/env bash

# Get the directory of the current script
script_dir=$(dirname "$(realpath "$0")")

while getopts s:h:t:r:m:j: flag
do
  case "${flag}" in
    s) dirSubs=${OPTARG};;
    t) dirHCP=${OPTARG};;
    h) hemisphere=${OPTARG};
       case "$hemisphere" in
         lh|rh) ;;
         *) echo "Invalid hemisphere argument: $hemisphere"; exit 1;;
       esac;;
    r) map=${OPTARG};
       case "$map" in
         'polarAngle'|'eccentricity'|'pRFsize') ;;
         *) echo "Invalid map argument: $map"; exit 1;;
       esac;;
    m) model=${OPTARG};
       case "$model" in
         model1|model2|model3|model4|model5|average|model) ;;
         *) echo "Invalid model argument: $model"; exit 1;;
       esac;;
    j) n_jobs=${OPTARG};;
    ?)
      echo "script usage: $(basename "$0") [-s path to subs] [-t path to HCP surfaces] [-h hemisphere] [-r map] [-m model] [-j number of cores for parallelization]" >&2
      exit 1;;
  esac
done

echo "Model: $model"
echo "Map: $map"
echo "Hemisphere: $hemisphere"
echo "Using $n_jobs parallel jobs"

# Start total timing
total_start_time=$(date +%s)

# Define the processing function
process_subject_step3() {
    local dirSub=$1
    local hemisphere=$2
    local map=$3
    local model=$4
    local dirSubs=$5
    local dirHCP=$6
    local script_dir=$7
    
    echo "=== Processing Step 3 for subject: $dirSub ==="
    
    if [ ! -f "$dirSubs/$dirSub/deepRetinotopy/$dirSub.fs_predicted_${map}_${hemisphere}_curvatureFeat_${model}.func.gii" ]; then
        echo "[$dirSub] ERROR: Predicted map is not available"
        exit 1
    else
        start_time=$(date +%s)
        
        if [ "$hemisphere" == 'lh' ]; then
            echo "[$dirSub] Resampling ROI from fsaverage to native space for the left hemisphere..."
            wb_command -label-resample "$script_dir/../labels/ROI_WangPlusFovea/ROI.fs_lh.label.gii" \
            "$dirHCP/fs_LR-deformed_to-fsaverage.L.sphere.32k_fs_LR.surf.gii" \
            "$dirSubs/$dirSub/surf/$hemisphere.sphere.reg.surf.gii" ADAP_BARY_AREA "$dirSubs/$dirSub/deepRetinotopy/$dirSub.ROI.$hemisphere.native.label.gii" \
            -area-surfs "$dirSubs/$dirSub/surf/$dirSub.$hemisphere.midthickness.32k_fs_LR.surf.gii" "$dirSubs/$dirSub/surf/$hemisphere.midthickness.surf.gii"

            echo "[$dirSub] Resampling predicted map from fsaverage to native space for the left hemisphere..."
            wb_command -metric-resample "$dirSubs/$dirSub/deepRetinotopy/$dirSub.fs_predicted_${map}_${hemisphere}_curvatureFeat_${model}.func.gii" \
            "$dirHCP/fs_LR-deformed_to-fsaverage.L.sphere.32k_fs_LR.surf.gii" \
            "$dirSubs/$dirSub/surf/$hemisphere.sphere.reg.surf.gii" ADAP_BARY_AREA "$dirSubs/$dirSub/deepRetinotopy/$dirSub.predicted_${map}_${model}.$hemisphere.native.func.gii" \
            -area-surfs "$dirSubs/$dirSub/surf/$dirSub.$hemisphere.midthickness.32k_fs_LR.surf.gii" "$dirSubs/$dirSub/surf/$hemisphere.midthickness.surf.gii" \
            -current-roi "$script_dir/../labels/ROI_WangPlusFovea/ROI.fs_lh.label.gii"

            if [ "$map" == "polarAngle" ]; then
                echo "[$dirSub] Transforming polar angle map of the left hemisphere..."
                transform_polarangle_lh.py --path "$dirSubs/$dirSub/deepRetinotopy/" --model "$model"
            fi
            
            echo "[$dirSub] Applying mask to the predicted map of the left hemisphere..."
            wb_command -metric-mask "$dirSubs/$dirSub/deepRetinotopy/$dirSub.predicted_${map}_${model}.$hemisphere.native.func.gii" \
            "$dirSubs/$dirSub/deepRetinotopy/$dirSub.ROI.$hemisphere.native.label.gii" \
            "$dirSubs/$dirSub/deepRetinotopy/$dirSub.predicted_${map}_${model}.$hemisphere.native.func.gii"

        else
            echo "[$dirSub] Resampling ROI from fsaverage to native space for the right hemisphere..."
            wb_command -label-resample "$script_dir/../labels/ROI_WangPlusFovea/ROI.fs_rh.label.gii" \
            "$dirHCP/fs_LR-deformed_to-fsaverage.R.sphere.32k_fs_LR.surf.gii" \
            "$dirSubs/$dirSub/surf/$hemisphere.sphere.reg.surf.gii" ADAP_BARY_AREA "$dirSubs/$dirSub/deepRetinotopy/$dirSub.ROI.$hemisphere.native.label.gii" \
            -area-surfs "$dirSubs/$dirSub/surf/$dirSub.$hemisphere.midthickness.32k_fs_LR.surf.gii" "$dirSubs/$dirSub/surf/$hemisphere.midthickness.surf.gii"

            echo "[$dirSub] Resampling predicted map from fsaverage to native space for the right hemisphere..."
            wb_command -metric-resample "$dirSubs/$dirSub/deepRetinotopy/$dirSub.fs_predicted_${map}_${hemisphere}_curvatureFeat_${model}.func.gii" \
            "$dirHCP/fs_LR-deformed_to-fsaverage.R.sphere.32k_fs_LR.surf.gii" \
            "$dirSubs/$dirSub/surf/$hemisphere.sphere.reg.surf.gii" ADAP_BARY_AREA "$dirSubs/$dirSub/deepRetinotopy/$dirSub.predicted_${map}_${model}.$hemisphere.native.func.gii" \
            -area-surfs "$dirSubs/$dirSub/surf/$dirSub.$hemisphere.midthickness.32k_fs_LR.surf.gii" "$dirSubs/$dirSub/surf/$hemisphere.midthickness.surf.gii" \
            -current-roi "$script_dir/../labels/ROI_WangPlusFovea/ROI.fs_rh.label.gii"

            echo "[$dirSub] Applying mask to the predicted map of the right hemisphere..."
            wb_command -metric-mask "$dirSubs/$dirSub/deepRetinotopy/$dirSub.predicted_${map}_${model}.$hemisphere.native.func.gii" \
            "$dirSubs/$dirSub/deepRetinotopy/$dirSub.ROI.$hemisphere.native.label.gii" \
            "$dirSubs/$dirSub/deepRetinotopy/$dirSub.predicted_${map}_${model}.$hemisphere.native.func.gii"
        fi
        
        end_time=$(date +%s)
        execution_time=$((end_time-start_time))
        execution_time_minutes=$((execution_time / 60))
        echo "=== Subject $dirSub completed in $execution_time_minutes minutes ==="
    fi
}

# Export the function and variables
export -f process_subject_step3
export hemisphere map model dirSubs dirHCP script_dir

cd $dirSubs

# Collect subjects
subjects=()
for dirSub in `ls $dirSubs`; do
    if [ "$dirSub" != "fsaverage" ] && [[ "$dirSub" != .* ]]; then
        subjects+=("$dirSub")
    fi
done

echo "Found ${#subjects[@]} subjects to process: ${subjects[*]}"

# Process in parallel
printf '%s\n' "${subjects[@]}" | xargs -I {} -P $n_jobs bash -c "process_subject_step3 {} $hemisphere $map $model $dirSubs $dirHCP $script_dir"

# Calculate and display total time
total_end_time=$(date +%s)
total_execution_time=$((total_end_time-total_start_time))
total_minutes=$((total_execution_time / 60))
total_seconds=$((total_execution_time % 60))

echo ""
echo "==============================================="
echo "[Step 3] COMPLETED!"
echo "Total execution time: ${total_minutes}m ${total_seconds}s"
echo "Subjects processed: ${#subjects[@]}"
echo "Map: $map | Model: $model | Hemisphere: $hemisphere"
echo "Average time per subject: $((total_minutes * 60 + total_seconds))s ÷ ${#subjects[@]} = $(( (total_minutes * 60 + total_seconds) / ${#subjects[@]} ))s"
echo "Parallel jobs used: $n_jobs"
echo "==============================================="