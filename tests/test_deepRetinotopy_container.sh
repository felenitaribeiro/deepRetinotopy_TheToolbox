#!/usr/bin/env bash
set -e

# Get the directory where the current script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Source the common setup file
source "$SCRIPT_DIR/common_setup.sh"


test_container_simple() {
    setup_environment
    setup_unique_directory
    setup_data_directories
    
    local list_of_maps="polarAngle,eccentricity,pRFsize"
    IFS=',' read -ra maps <<< "$list_of_maps"
    echo "Maps: ${maps[*]}"

    echo "[DEBUG]: Testing deepRetinotopy container..."
    
    for map in "${maps[@]}"; do
        setup_subject_directories
        deepRetinotopy -s "$DIR_SUBS" -t "$DIR_HCP" -d "$DATASET_NAME" -m "$map"
    done
    
    test_output "Container test complete!" "SUCCESS"
}

# Run if called directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    test_container_simple
fi