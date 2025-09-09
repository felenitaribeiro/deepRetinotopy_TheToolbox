#!/usr/bin/env bash

# Auto-detect number of cores (leave 1 core free)
auto_cores=$(($(nproc) - 1))
[ $auto_cores -lt 1 ] && auto_cores=1  # Ensure at least 1 core

# Default values
n_jobs=$auto_cores
subject_id=""
output_dir=""

# Get the directory of the current script
script_dir=$(dirname "$(realpath "$0")")

while getopts s:h:t:r:m:j:i:o: flag
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
    i) subject_id=${OPTARG};;
    o) output_dir=${OPTARG};;
    ?)
      echo "script usage: $(basename "$0") [-s path to subs] [-t path to HCP surfaces] [-h hemisphere] [-r map] [-m model] [-j number of cores for parallelization] [-i subject ID for single subject processing] [-o output directory]" >&2
      exit 1;;
  esac
done

echo "Model: $model"
echo "Map: $map"
echo "Hemisphere: $hemisphere"

# Check if processing single subject or multiple subjects
if [ -n "$subject_id" ]; then
    echo "Processing single subject: $subject_id"
else
    echo "Using $n_jobs parallel jobs for multiple subjects"
fi

# Check output directory setup
if [ -n "$output_dir" ]; then
    echo "Output directory: $output_dir"
    # Create output directory if it doesn't exist
    mkdir -p "$output_dir"
else
    echo "Output mode: In-place (within FreeSurfer directory structure)"
fi

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
    local output_dir=$8
    
    echo "=== Processing Step 3 for subject: $dirSub ==="
    
    # Determine input and output paths
    if [ -n "$output_dir" ]; then
        local subject_output_dir="$output_dir/$dirSub"
        local deepret_output_dir="$subject_output_dir/deepRetinotopy"
        local surf_output_dir="$subject_output_dir/surf"
        mkdir -p "$deepret_output_dir"
        echo "[$dirSub] Using custom output directory: $subject_output_dir"
        
        # Check for input files in custom output directory first, then original location
        local input_prediction_file="$deepret_output_dir/$dirSub.fs_predicted_${map}_${hemisphere}_curvatureFeat_${model}.func.gii"
        if [ ! -f "$input_prediction_file" ]; then
            input_prediction_file="$dirSubs/$dirSub/deepRetinotopy/$dirSub.fs_predicted_${map}_${hemisphere}_curvatureFeat_${model}.func.gii"
        fi
        
        # Surface files for resampling
        local surf_midthickness_32k="$surf_output_dir/$dirSub.$hemisphere.midthickness.32k_fs_LR.surf.gii"
        local surf_midthickness_native="$surf_output_dir/$hemisphere.midthickness.surf.gii"
        local surf_sphere_reg="$surf_output_dir/$hemisphere.sphere.reg.surf.gii"
        
        # Fallback to original locations if not in custom output
        if [ ! -f "$surf_midthickness_32k" ]; then
            surf_midthickness_32k="$dirSubs/$dirSub/surf/$dirSub.$hemisphere.midthickness.32k_fs_LR.surf.gii"
        fi
        if [ ! -f "$surf_midthickness_native" ]; then
            surf_midthickness_native="$dirSubs/$dirSub/surf/$hemisphere.midthickness.surf.gii"
        fi
        if [ ! -f "$surf_sphere_reg" ]; then
            surf_sphere_reg="$dirSubs/$dirSub/surf/$hemisphere.sphere.reg.surf.gii"
        fi
    else
        local deepret_output_dir="$dirSubs/$dirSub/deepRetinotopy"
        local input_prediction_file="$deepret_output_dir/$dirSub.fs_predicted_${map}_${hemisphere}_curvatureFeat_${model}.func.gii"
        local surf_midthickness_32k="$dirSubs/$dirSub/surf/$dirSub.$hemisphere.midthickness.32k_fs_LR.surf.gii"
        local surf_midthickness_native="$dirSubs/$dirSub/surf/$hemisphere.midthickness.surf.gii"
        local surf_sphere_reg="$dirSubs/$dirSub/surf/$hemisphere.sphere.reg.surf.gii"
        echo "[$dirSub] Using FreeSurfer directory: $deepret_output_dir"
    fi
    
    if [ ! -f "$input_prediction_file" ]; then
        echo "[$dirSub] ERROR: Predicted map is not available: $input_prediction_file"
        exit 1
    else
        start_time=$(date +%s)
        
        if [ "$hemisphere" == 'lh' ]; then
            echo "[$dirSub] Resampling ROI from fsaverage to native space for the left hemisphere..."
            wb_command -label-resample "$script_dir/../labels/ROI_WangPlusFovea/ROI.fs_lh.label.gii" \
            "$dirHCP/fs_LR-deformed_to-fsaverage.L.sphere.32k_fs_LR.surf.gii" \
            "$surf_sphere_reg" ADAP_BARY_AREA "$deepret_output_dir/$dirSub.ROI.$hemisphere.native.label.gii" \
            -area-surfs "$surf_midthickness_32k" "$surf_midthickness_native"

            echo "[$dirSub] Resampling predicted map from fsaverage to native space for the left hemisphere..."
            wb_command -metric-resample "$input_prediction_file" \
            "$dirHCP/fs_LR-deformed_to-fsaverage.L.sphere.32k_fs_LR.surf.gii" \
            "$surf_sphere_reg" ADAP_BARY_AREA "$deepret_output_dir/$dirSub.predicted_${map}_${model}.$hemisphere.native.func.gii" \
            -area-surfs "$surf_midthickness_32k" "$surf_midthickness_native" \
            -current-roi "$script_dir/../labels/ROI_WangPlusFovea/ROI.fs_lh.label.gii"

            if [ "$map" == "polarAngle" ]; then
                echo "[$dirSub] Transforming polar angle map of the left hemisphere..."
                transform_polarangle_lh.py --path "$deepret_output_dir/" --model "$model"
            fi
            
            echo "[$dirSub] Applying mask to the predicted map of the left hemisphere..."
            wb_command -metric-mask "$deepret_output_dir/$dirSub.predicted_${map}_${model}.$hemisphere.native.func.gii" \
            "$deepret_output_dir/$dirSub.ROI.$hemisphere.native.label.gii" \
            "$deepret_output_dir/$dirSub.predicted_${map}_${model}.$hemisphere.native.func.gii"

        else
            echo "[$dirSub] Resampling ROI from fsaverage to native space for the right hemisphere..."
            wb_command -label-resample "$script_dir/../labels/ROI_WangPlusFovea/ROI.fs_rh.label.gii" \
            "$dirHCP/fs_LR-deformed_to-fsaverage.R.sphere.32k_fs_LR.surf.gii" \
            "$surf_sphere_reg" ADAP_BARY_AREA "$deepret_output_dir/$dirSub.ROI.$hemisphere.native.label.gii" \
            -area-surfs "$surf_midthickness_32k" "$surf_midthickness_native"

            echo "[$dirSub] Resampling predicted map from fsaverage to native space for the right hemisphere..."
            wb_command -metric-resample "$input_prediction_file" \
            "$dirHCP/fs_LR-deformed_to-fsaverage.R.sphere.32k_fs_LR.surf.gii" \
            "$surf_sphere_reg" ADAP_BARY_AREA "$deepret_output_dir/$dirSub.predicted_${map}_${model}.$hemisphere.native.func.gii" \
            -area-surfs "$surf_midthickness_32k" "$surf_midthickness_native" \
            -current-roi "$script_dir/../labels/ROI_WangPlusFovea/ROI.fs_rh.label.gii"

            echo "[$dirSub] Applying mask to the predicted map of the right hemisphere..."
            wb_command -metric-mask "$deepret_output_dir/$dirSub.predicted_${map}_${model}.$hemisphere.native.func.gii" \
            "$deepret_output_dir/$dirSub.ROI.$hemisphere.native.label.gii" \
            "$deepret_output_dir/$dirSub.predicted_${map}_${model}.$hemisphere.native.func.gii"
        fi
        
        end_time=$(date +%s)
        execution_time=$((end_time-start_time))
        execution_time_minutes=$((execution_time / 60))
        echo "=== Subject $dirSub completed in $execution_time_minutes minutes ==="
    fi
}

# Process single subject or multiple subjects
if [ -n "$subject_id" ]; then
    # Single subject processing
    if [ ! -d "$dirSubs/$subject_id" ]; then
        echo "ERROR: Subject directory '$subject_id' not found in $dirSubs"
        exit 1
    fi
    
    echo "Processing subject: $subject_id"
    process_subject_step3 "$subject_id" "$hemisphere" "$map" "$model" "$dirSubs" "$dirHCP" "$script_dir" "$output_dir"
    
else
    # Multiple subjects processing (original behavior)
    # Export the function and variables for parallel processing
    export -f process_subject_step3
    export hemisphere map model dirSubs dirHCP script_dir output_dir
    
    # Change to subjects directory for listing
    cd $dirSubs
    
    # Collect subjects
    subjects=()
    for dirSub in `ls .`; do
        if [ "$dirSub" != "fsaverage" ] && [[ "$dirSub" != .* ]] && [ "$dirSub" != processed_* ] && [[ "$dirSub" != *.txt ]] && [[ "$dirSub" != *.log ]] && [[ "$dirSub" != "logs" ]]; then
            subjects+=("$dirSub")
        fi
    done

    echo "Found ${#subjects[@]} subjects to process: ${subjects[*]}"

    # Process in parallel
    printf '%s\n' "${subjects[@]}" | xargs -I {} -P $n_jobs bash -c "process_subject_step3 '{}' '$hemisphere' '$map' '$model' '$dirSubs' '$dirHCP' '$script_dir' '$output_dir'"
fi

# Calculate and display total time
total_end_time=$(date +%s)
total_execution_time=$((total_end_time-total_start_time))
total_minutes=$((total_execution_time / 60))
total_seconds=$((total_execution_time % 60))

echo ""
echo "==============================================="
echo "[Step 3] COMPLETED!"
echo "Total execution time: ${total_minutes}m ${total_seconds}s"

if [ -n "$subject_id" ]; then
    echo "Subject processed: $subject_id"
    echo "Map: $map | Model: $model | Hemisphere: $hemisphere"
else
    echo "Subjects processed: ${#subjects[@]}"
    echo "Map: $map | Model: $model | Hemisphere: $hemisphere"
    echo "Average time per subject: $((total_minutes * 60 + total_seconds))s ÷ ${#subjects[@]} = $(( (total_minutes * 60 + total_seconds) / ${#subjects[@]} ))s"
    echo "Parallel jobs used: $n_jobs"
fi

if [ -n "$output_dir" ]; then
    echo "Output location: $output_dir"
else
    echo "Output location: In-place within FreeSurfer directory"
fi
echo "==============================================="