#!/usr/bin/env bash

# Auto-detect number of cores (leave 1 core free)
auto_cores=$(($(nproc) - 1))
[ $auto_cores -lt 1 ] && auto_cores=1  # Ensure at least 1 core

# Default values
n_jobs=$auto_cores
subject_id=""
output_dir=""

while getopts s:t:h:g:j:i:o: flag
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
        o) output_dir=${OPTARG};;
        ?)
            echo "script usage: $(basename "$0") [-s path to subs] [-t path to HCP surfaces] [-h hemisphere] [-g fast generation of midthickness surface] [-j number of cores for parallelization] [-i subject ID for single subject processing] [-o output directory]" >&2
            exit 1;;
    esac
done

# Normalize paths: the script cd's into $dirSubs, so relative -s/-t/-o arguments
# would silently resolve against the wrong base afterwards.
dirSubs=$(realpath "$dirSubs")
dirHCP=$(realpath "$dirHCP")
[ -n "$output_dir" ] && output_dir=$(realpath -m "$output_dir")

# Fail fast if a required tool is missing (otherwise every subject fails
# mid-function with 'command not found' noise).
required_tools="mris_convert mris_curvature wb_shortcuts wb_command"
if [ "$fast" == "yes" ]; then
    required_tools="$required_tools midthickness_surf.py"
else
    required_tools="$required_tools mris_expand"
fi
for tool in $required_tools; do
    if ! command -v "$tool" > /dev/null; then
        echo "[Step 1] ERROR: required tool '$tool' not found on PATH. Run inside the deepRetinotopy container or load FreeSurfer + Connectome Workbench."
        exit 2   # environment problem: fatal for every subject, caller must abort
    fi
done

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
process_subject() {
    local dirSub=$1
    local hemisphere=$2
    local fast=$3
    local dirSubs=$4
    local dirHCP=$5
    local output_dir=$6
    
    echo "=== Processing Step 1 for subject: $dirSub ==="
    
    # Determine output paths
    if [ -n "$output_dir" ]; then
        local subject_output_dir="$output_dir/$dirSub"
        local surf_output_dir="$subject_output_dir/surf"
        mkdir -p "$surf_output_dir"
        echo "[$dirSub] Using custom output directory: $subject_output_dir"
    else
        local surf_output_dir="$dirSubs/$dirSub/surf"
        echo "[$dirSub] Using FreeSurfer directory: $surf_output_dir"
    fi
    
    if [ -d "$dirSubs/$dirSub/surf" ]; then
        start_time=$(date +%s)

        # Prerequisites for this subject, checked up front so a missing file gives
        # one clear message instead of mid-run tool errors: white + pial +
        # sphere.reg are always needed (freesurfer-resample-prep); non-fast mode
        # additionally needs thickness (mris_expand -thickness).
        required_files="$hemisphere.white $hemisphere.pial $hemisphere.sphere.reg"
        [ "$fast" != "yes" ] && required_files="$required_files $hemisphere.thickness"
        for req in $required_files; do
            if [ ! -f "$dirSubs/$dirSub/surf/$req" ]; then
                echo "[$dirSub] ERROR: required input surf/$req not found"
                exit 1
            fi
        done

        if [ "$fast" == "yes" ]; then
            echo "[$dirSub] Fast mode enabled."
            echo "[$dirSub] [Step 1.1] Generating mid-thickness surface and curvature data if not available..."
            if [ ! -f "$surf_output_dir/$hemisphere.graymid" ]; then
                if [ ! -f "$dirSubs/$dirSub/surf/$hemisphere.white" ]; then
                    echo "[$dirSub] ERROR: No white surface found"
                    exit 1
                else
                    echo "[$dirSub] Converting surfaces..."
                    mris_convert "$dirSubs/$dirSub/surf/$hemisphere.white" "$surf_output_dir/$hemisphere.white.gii"
                    mris_convert "$dirSubs/$dirSub/surf/$hemisphere.pial" "$surf_output_dir/$hemisphere.pial.gii"
                    echo "[$dirSub] Generating midthickness surface..."
                    midthickness_surf.py --path "$surf_output_dir/" --hemisphere $hemisphere 
                    mris_convert "$surf_output_dir/$hemisphere.graymid.gii" "$surf_output_dir/$hemisphere.graymid"
                    echo "[$dirSub] Computing curvature..."
                    mris_curvature -w "$surf_output_dir/$hemisphere.graymid"
                fi
                echo "[$dirSub] Mid-thickness surface has been generated"
            else 
                echo "[$dirSub] Mid-thickness surface and curvature data already available"
            fi
        else
            echo "[$dirSub] [Step 1.1] Generating mid-thickness surface and curvature data if not available..."
            if [ ! -f "$surf_output_dir/$hemisphere.graymid" ]; then
                if [ ! -f "$dirSubs/$dirSub/surf/$hemisphere.white" ]; then
                    echo "[$dirSub] ERROR: No white surface found"
                    exit 1
                else
                    echo "[$dirSub] Expanding white surface to midthickness..."
                    mris_expand -thickness "$dirSubs/$dirSub/surf/$hemisphere.white" 0.5 "$surf_output_dir/$hemisphere.graymid"
                    echo "[$dirSub] Computing curvature..."
                    mris_curvature -w "$surf_output_dir/$hemisphere.graymid"
                fi
                echo "[$dirSub] Mid-thickness surface has been generated"
            else 
                echo "[$dirSub] Mid-thickness surface and curvature data already available"
            fi
        fi    
        
        echo "[$dirSub] [Step 1.2] Preparing native surfaces for resampling..."
        if [ ! -f "$surf_output_dir/$dirSub.curvature-midthickness.$hemisphere.32k_fs_LR.func.gii" ]; then
            echo "[$dirSub] Running freesurfer-resample-prep..."
            if [ "$hemisphere" == "lh" ]; then
                wb_shortcuts -freesurfer-resample-prep "$dirSubs/$dirSub/surf/$hemisphere.white" "$dirSubs/$dirSub/surf/$hemisphere.pial" \
                "$dirSubs/$dirSub/surf/$hemisphere.sphere.reg" "$dirHCP/fs_LR-deformed_to-fsaverage.L.sphere.32k_fs_LR.surf.gii" \
                "$surf_output_dir/$hemisphere.midthickness.surf.gii" "$surf_output_dir/$dirSub.$hemisphere.midthickness.32k_fs_LR.surf.gii" \
                "$surf_output_dir/$hemisphere.sphere.reg.surf.gii"
                
                echo "[$dirSub] Converting curvature data..."
                mris_convert -c "$surf_output_dir/$hemisphere.graymid.H" "$surf_output_dir/$hemisphere.graymid" "$surf_output_dir/$hemisphere.graymid.H.gii"
                
                echo "[$dirSub] Resampling native data to fsaverage space..."
                wb_command -metric-resample "$surf_output_dir/$hemisphere.graymid.H.gii" \
                "$surf_output_dir/$hemisphere.sphere.reg.surf.gii" "$dirHCP/fs_LR-deformed_to-fsaverage.L.sphere.32k_fs_LR.surf.gii" \
                ADAP_BARY_AREA "$surf_output_dir/$dirSub.curvature-midthickness.$hemisphere.32k_fs_LR.func.gii" \
                -area-surfs "$surf_output_dir/$hemisphere.midthickness.surf.gii" "$surf_output_dir/$dirSub.$hemisphere.midthickness.32k_fs_LR.surf.gii"
            else
                wb_shortcuts -freesurfer-resample-prep "$dirSubs/$dirSub/surf/$hemisphere.white" "$dirSubs/$dirSub/surf/$hemisphere.pial" \
                "$dirSubs/$dirSub/surf/$hemisphere.sphere.reg" "$dirHCP/fs_LR-deformed_to-fsaverage.R.sphere.32k_fs_LR.surf.gii" \
                "$surf_output_dir/$hemisphere.midthickness.surf.gii" "$surf_output_dir/$dirSub.$hemisphere.midthickness.32k_fs_LR.surf.gii" \
                "$surf_output_dir/$hemisphere.sphere.reg.surf.gii"
                
                echo "[$dirSub] Converting curvature data..."
                mris_convert -c "$surf_output_dir/$hemisphere.graymid.H" "$surf_output_dir/$hemisphere.graymid" "$surf_output_dir/$hemisphere.graymid.H.gii"
                
                echo "[$dirSub] Resampling native data to fsaverage space..."
                wb_command -metric-resample "$surf_output_dir/$hemisphere.graymid.H.gii" \
                "$surf_output_dir/$hemisphere.sphere.reg.surf.gii" "$dirHCP/fs_LR-deformed_to-fsaverage.R.sphere.32k_fs_LR.surf.gii" \
                ADAP_BARY_AREA "$surf_output_dir/$dirSub.curvature-midthickness.$hemisphere.32k_fs_LR.func.gii" \
                -area-surfs "$surf_output_dir/$hemisphere.midthickness.surf.gii" "$surf_output_dir/$dirSub.$hemisphere.midthickness.32k_fs_LR.surf.gii"
            fi
            echo "[$dirSub] Data resampling complete"
        else
            echo "[$dirSub] Resampled curvature data already available"
        fi

        # Post-condition: a tool failure above (e.g. wb_command missing or a
        # resample error) must fail this subject, not fall through to "completed".
        if [ ! -f "$surf_output_dir/$dirSub.curvature-midthickness.$hemisphere.32k_fs_LR.func.gii" ]; then
            echo "[$dirSub] ERROR: expected output $dirSub.curvature-midthickness.$hemisphere.32k_fs_LR.func.gii was not produced"
            exit 1
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

# Process single subject or multiple subjects
if [ -n "$subject_id" ]; then
    # Single subject processing
    if [ ! -d "$dirSubs/$subject_id" ]; then
        echo "ERROR: Subject directory '$subject_id' not found in $dirSubs"
        exit 1
    fi
    
    echo "Processing subject: $subject_id"
    process_subject "$subject_id" "$hemisphere" "$fast" "$dirSubs" "$dirHCP" "$output_dir"
    
else
    # Multiple subjects processing (original behavior)
    # Export the function and variables for parallel processing
    export -f process_subject
    export hemisphere fast dirSubs dirHCP output_dir
    
    # Change to subjects directory for listing
    cd $dirSubs
    
    # Collect subjects
    subjects=()
    for dirSub in `ls .`; do
        if [ "$dirSub" != "fsaverage" ] && [[ "$dirSub" != .* ]] && [[ "$dirSub" != processed_* ]] && [[ "$dirSub" != *.txt ]] && [[ "$dirSub" != *.log ]] && [[ "$dirSub" != "logs" ]]; then
            subjects+=("$dirSub")
        fi
    done

    echo "Found ${#subjects[@]} subjects to process: ${subjects[*]}"

    # Process in parallel. xargs returns 123 if ANY per-subject invocation failed;
    # without this check a failed subject is silently dropped and the step
    # reports success (the CLI then only sees missing files much later, if at all).
    printf '%s\n' "${subjects[@]}" | xargs -I {} -P $n_jobs bash -c "process_subject '{}' '$hemisphere' '$fast' '$dirSubs' '$dirHCP' '$output_dir'"
    xargs_status=$?
    if [ $xargs_status -ne 0 ]; then
        # Partial failure: list who failed and exit 1 so the caller can warn and
        # CONTINUE with the subjects that succeeded. If nobody succeeded, exit 2
        # (fatal -- almost certainly an environment or input problem).
        n_ok=0; failed_subjects=""
        for s in "${subjects[@]}"; do
            if [ -n "$output_dir" ]; then
                out="$output_dir/$s/surf/$s.curvature-midthickness.$hemisphere.32k_fs_LR.func.gii"
            else
                out="$dirSubs/$s/surf/$s.curvature-midthickness.$hemisphere.32k_fs_LR.func.gii"
            fi
            if [ -f "$out" ]; then n_ok=$((n_ok+1)); else failed_subjects="$failed_subjects $s"; fi
        done
        echo "[Step 1] WARNING: $(( ${#subjects[@]} - n_ok )) of ${#subjects[@]} subjects FAILED:$failed_subjects"
        if [ $n_ok -eq 0 ]; then
            echo "[Step 1] ERROR: no subject produced output -- aborting."
            exit 2
        fi
        exit 1
    fi
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

if [ -n "$output_dir" ]; then
    echo "Output location: $output_dir"
else
    echo "Output location: In-place within FreeSurfer directory"
fi
echo "==============================================="