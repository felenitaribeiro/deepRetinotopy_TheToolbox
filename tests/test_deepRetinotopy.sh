#!/usr/bin/env bash
set -e

# Get the directory where the current script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Source the common setup file
source "$SCRIPT_DIR/common_setup.sh"

test_deepretinotopy_full() {
    setup_environment
    setup_unique_directory
    setup_data_directories
    get_deepretinotopy_paths
    setup_path_and_bins
    
    cd "$TOOLBOX_PATH"
    
    local list_of_maps="polarAngle,eccentricity,pRFsize"
    IFS=',' read -ra maps <<< "$list_of_maps"
    echo "Maps: ${maps[*]}"

    echo "[DEBUG]: Testing deepRetinotopy with model management..."
    
    declare -A test_scenarios=(
        ["single_subject"]="-i 1"
        ["all_subjects"]=""
        ["single_subject_output"]="-i 1 -o $OUTPUT_DIR"
    )

    for scenario_name in "${!test_scenarios[@]}"; do
        local flags="${test_scenarios[$scenario_name]}"
        echo "[DEBUG]: Running scenario '$scenario_name' with flags: $flags"
        for map in "${maps[@]}"; do
            copy_models "$map"
            setup_subject_directories
            
            eval "deepRetinotopy -s $DIR_SUBS -t $DIR_HCP -d $DATASET_NAME -m $map $flags"
            
            clean_models
        done

        if [ $scenario_name == "single_subject_output" ]; then
            if [ -d "$OUTPUT_DIR" ]; then
                test_output "Output directory created successfully for scenario '$scenario_name'" "SUCCESS"
                # check if output files are present
                if find "$OUTPUT_DIR" -name "*${map}*.gii" | grep -q .; then
                    test_output "Output files found in $OUTPUT_DIR for scenario '$scenario_name'" "SUCCESS"
                else
                    test_output "No output files found in $OUTPUT_DIR for scenario '$scenario_name'" "ERROR"
                fi
            else
                test_output "Failed to create output directory for scenario '$scenario_name'" "ERROR"
            fi
        fi
    done
    cleanup_tmp_directory
    test_output "Full deepRetinotopy test complete!" "SUCCESS"
}

# Run if called directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    test_deepretinotopy_full
fi
