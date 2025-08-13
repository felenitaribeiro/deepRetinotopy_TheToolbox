#!/usr/bin/env bash

# Auto-detect number of cores (leave 1 core free)
auto_cores=$(($(nproc) - 1))
[ $auto_cores -lt 1 ] && auto_cores=1  # Ensure at least 1 core

# Default values
n_jobs=$auto_cores
subject_id=""

while getopts s:t:h:g:j:i: flag
do
    case "${flag}" in
        s) dirSubs=${OPTARG};;
        t) dirHCP=${OPTARG};;
        h) hemisphere=${OPTARG};
           case "$hemisphere" in
               lh|rh) ;;
               *) echo "Invalid hemisphere argument: $hemisphere"; exit 1;;
           esac;;
        g) fast=${OPTARG};
            case "$fast" in
            'yes'|'no') ;;
            *) echo "Invalid fast argument: $fast"; exit 1;;
            esac;;
        j) n_jobs=${OPTARG};;
        i) subject_id=${OPTARG};;
        ?)
            echo "script usage: $(basename "$0") [-s path to subs] [-t path to HCP surfaces] [-h hemisphere] [-g fast generation of midthickness surface] [-j number of cores for parallelization] [-i subject ID for single subject processing]" >&2
            exit 1;;
    esac
done

echo "Hemisphere: $hemisphere"

# Check if processing single subject or multiple subjects
if [ -n "$subject_id" ]; then
    echo "Processing single subject: $subject_id"
else
    echo "Using $n_jobs parallel jobs for multiple subjects"
fi

# Start total timing
total_start_time=$(date +%s)

# Define the processing function
process_subject() {
    local dirSub=$1
    local hemisphere=$2
    local fast=$3
    local dirSubs=$4
    local dirHCP=$5
    
    echo "=== Processing Step 1 for subject: $dirSub ==="
    
    if [ -d "$dirSubs/$dirSub/surf" ]; then
        start_time=$(date +%s)
        
        if [ "$fast" == "yes" ]; then
            echo "[$dirSub] Fast mode enabled."
            echo "[$dirSub] [Step 1.1] Generating mid-thickness surface and curvature data if not available..."
            if [ ! -f "$dirSubs/$dirSub/surf/$hemisphere.graymid" ]; then
                if [ ! -f "$dirSubs/$dirSub/surf/$hemisphere.white" ]; then
                    echo "[$dirSub] ERROR: No white surface found"
                    exit 1
                else
                    echo "[$dirSub] Converting surfaces..."
                    mris_convert "$dirSubs/$dirSub/surf/$hemisphere.white" "$dirSubs/$dirSub/surf/$hemisphere.white.gii"
                    mris_convert "$dirSubs/$dirSub/surf/$hemisphere.pial" "$dirSubs/$dirSub/surf/$hemisphere.pial.gii"
                    echo "[$dirSub] Generating midthickness surface..."
                    midthickness_surf.py --path "$dirSubs/$dirSub/surf/" --hemisphere $hemisphere 
                    mris_convert "$dirSubs/$dirSub/surf/$hemisphere.graymid.gii" "$dirSubs/$dirSub/surf/$hemisphere.graymid"
                    echo "[$dirSub] Computing curvature..."
                    mris_curvature -w "$dirSubs/$dirSub/surf/$hemisphere.graymid"
                fi
                echo "[$dirSub] Mid-thickness surface has been generated"
            else 
                echo "[$dirSub] Mid-thickness surface and curvature data already available"
            fi
        else
            echo "[$dirSub] [Step 1.1] Generating mid-thickness surface and curvature data if not available..."
            if [ ! -f "$dirSubs/$dirSub/surf/$hemisphere.graymid" ]; then
                if [ ! -f "$dirSubs/$dirSub/surf/$hemisphere.white" ]; then
                    echo "[$dirSub] ERROR: No white surface found"
                    exit 1
                else
                    echo "[$dirSub] Expanding white surface to midthickness..."
                    mris_expand -thickness "$dirSubs/$dirSub/surf/$hemisphere.white" 0.5 "$dirSubs/$dirSub/surf/$hemisphere.graymid"
                    echo "[$dirSub] Computing curvature..."
                    mris_curvature -w "$dirSubs/$dirSub/surf/$hemisphere.graymid"
                fi
                echo "[$dirSub] Mid-thickness surface has been generated"
            else 
                echo "[$dirSub] Mid-thickness surface and curvature data already available"
            fi
        fi    
        
        echo "[$dirSub] [Step 1.2] Preparing native surfaces for resampling..."
        if [ ! -f "$dirSubs/$dirSub/surf/$dirSub.curvature-midthickness.$hemisphere.32k_fs_LR.func.gii" ]; then
            echo "[$dirSub] Running freesurfer-resample-prep..."
            if [ "$hemisphere" == "lh" ]; then
                wb_shortcuts -freesurfer-resample-prep "$dirSubs/$dirSub/surf/$hemisphere.white" "$dirSubs/$dirSub/surf/$hemisphere.pial" \
                "$dirSubs/$dirSub/surf/$hemisphere.sphere.reg" "$dirHCP/fs_LR-deformed_to-fsaverage.L.sphere.32k_fs_LR.surf.gii" \
                "$dirSubs/$dirSub/surf/$hemisphere.midthickness.surf.gii" "$dirSubs/$dirSub/surf/$dirSub.$hemisphere.midthickness.32k_fs_LR.surf.gii" \
                "$dirSubs/$dirSub/surf/$hemisphere.sphere.reg.surf.gii"
                
                echo "[$dirSub] Converting curvature data..."
                mris_convert -c "$dirSubs/$dirSub/surf/$hemisphere.graymid.H" "$dirSubs/$dirSub/surf/$hemisphere.graymid" "$dirSubs/$dirSub/surf/$hemisphere.graymid.H.gii"
                
                echo "[$dirSub] Resampling native data to fsaverage space..."
                wb_command -metric-resample "$dirSubs/$dirSub/surf/$hemisphere.graymid.H.gii" \
                "$dirSubs/$dirSub/surf/$hemisphere.sphere.reg.surf.gii" "$dirHCP/fs_LR-deformed_to-fsaverage.L.sphere.32k_fs_LR.surf.gii" \
                ADAP_BARY_AREA "$dirSubs/$dirSub/surf/$dirSub.curvature-midthickness.$hemisphere.32k_fs_LR.func.gii" \
                -area-surfs "$dirSubs/$dirSub/surf/$hemisphere.midthickness.surf.gii" "$dirSubs/$dirSub/surf/$dirSub.$hemisphere.midthickness.32k_fs_LR.surf.gii"
            else
                wb_shortcuts -freesurfer-resample-prep "$dirSubs/$dirSub/surf/$hemisphere.white" "$dirSubs/$dirSub/surf/$hemisphere.pial" \
                "$dirSubs/$dirSub/surf/$hemisphere.sphere.reg" "$dirHCP/fs_LR-deformed_to-fsaverage.R.sphere.32k_fs_LR.surf.gii" \
                "$dirSubs/$dirSub/surf/$hemisphere.midthickness.surf.gii" "$dirSubs/$dirSub/surf/$dirSub.$hemisphere.midthickness.32k_fs_LR.surf.gii" \
                "$dirSubs/$dirSub/surf/$hemisphere.sphere.reg.surf.gii"
                
                echo "[$dirSub] Converting curvature data..."
                mris_convert -c "$dirSubs/$dirSub/surf/$hemisphere.graymid.H" "$dirSubs/$dirSub/surf/$hemisphere.graymid" "$dirSubs/$dirSub/surf/$hemisphere.graymid.H.gii"
                
                echo "[$dirSub] Resampling native data to fsaverage space..."
                wb_command -metric-resample "$dirSubs/$dirSub/surf/$hemisphere.graymid.H.gii" \
                "$dirSubs/$dirSub/surf/$hemisphere.sphere.reg.surf.gii" "$dirHCP/fs_LR-deformed_to-fsaverage.R.sphere.32k_fs_LR.surf.gii" \
                ADAP_BARY_AREA "$dirSubs/$dirSub/surf/$dirSub.curvature-midthickness.$hemisphere.32k_fs_LR.func.gii" \
                -area-surfs "$dirSubs/$dirSub/surf/$hemisphere.midthickness.surf.gii" "$dirSubs/$dirSub/surf/$dirSub.$hemisphere.midthickness.32k_fs_LR.surf.gii"
            fi
            echo "[$dirSub] Data resampling complete"
        else
            echo "[$dirSub] Resampled curvature data already available"
        fi
        
        end_time=$(date +%s)
        execution_time=$((end_time-start_time))
        execution_time_minutes=$((execution_time / 60))
        echo "=== Subject $dirSub completed in $execution_time_minutes minutes ==="         
    else
        echo "[$dirSub] ERROR: No surface directory found"
        exit 1
    fi
}

cd $dirSubs

# Process single subject or multiple subjects
if [ -n "$subject_id" ]; then
    # Single subject processing
    if [ ! -d "$subject_id" ]; then
        echo "ERROR: Subject directory '$subject_id' not found in $dirSubs"
        exit 1
    fi
    
    echo "Processing subject: $subject_id"
    process_subject "$subject_id" "$hemisphere" "$fast" "$dirSubs" "$dirHCP"
    
else
    # Multiple subjects processing (original behavior)
    # Export the function and variables for parallel processing
    export -f process_subject
    export hemisphere fast dirSubs dirHCP
    
    # Collect subjects
    subjects=()
    for dirSub in `ls .`; do
        if [ "$dirSub" != "fsaverage" ] && [[ "$dirSub" != .* ]] && [ "$dirSub" != "processed" ]; then
            subjects+=("$dirSub")
        fi
    done

    echo "Found ${#subjects[@]} subjects to process: ${subjects[*]}"

    # Process in parallel
    printf '%s\n' "${subjects[@]}" | xargs -I {} -P $n_jobs bash -c "process_subject '{}' '$hemisphere' '$fast' '$dirSubs' '$dirHCP'"
fi

# Calculate and display total time
total_end_time=$(date +%s)
total_execution_time=$((total_end_time-total_start_time))
total_minutes=$((total_execution_time / 60))
total_seconds=$((total_execution_time % 60))

echo ""
echo "==============================================="
echo "[Step 1] COMPLETED!"
echo "Total execution time: ${total_minutes}m ${total_seconds}s"

if [ -n "$subject_id" ]; then
    echo "Subject processed: $subject_id"
else
    echo "Subjects processed: ${#subjects[@]}"
    echo "Average time per subject: $((total_minutes * 60 + total_seconds))s ÷ ${#subjects[@]} = $(( (total_minutes * 60 + total_seconds) / ${#subjects[@]} ))s"
    echo "Parallel jobs used: $n_jobs"
fi
echo "==============================================="