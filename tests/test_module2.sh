#!/usr/bin/env bash
set -e

# Get the directory where the current script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Source the common setup file
source "$SCRIPT_DIR/common_setup.sh"

test_module2() {
    setup_environment
    setup_unique_directory
    setup_data_directories
    get_deepretinotopy_paths
    setup_path_and_bins
    
    # Copy specific models for polarAngle LH
    cd "$DEEPRETINOTOPY_PATH/$DEEPRETINOTOPY_DIR.simg/opt/deepRetinotopy_TheToolbox"
    sudo mkdir -p "$TOOLBOX_PATH/models/"
    sudo chmod 777 "$TOOLBOX_PATH"
    sudo cp -r models/deepRetinotopy_polarAngle_LH_* "$TOOLBOX_PATH/models/"
    
    echo "[DEBUG]: deepRetinotopy inference..."
    cd "$TOOLBOX_PATH/main"
    
    for hemisphere in lh; do  # Could expand to rh
        for map in polarAngle; do  # Could expand to eccentricity, pRFsize
            echo "Hemisphere: $hemisphere"
            setup_subject_directories
            
            # Debug: list surfaces
            for i in $(ls "$DIR_SUBS"); do
                ls "$DIR_SUBS/$i/surf/" || true
            done
            
            python ./2_inference.py --path "$DIR_SUBS" --dataset "$DATASET_NAME" --prediction_type "$map" --hemisphere "$hemisphere"
            
            # Clean up processed directory
            sudo rm -r "$DIR_SUBS/processed" 2>/dev/null || true
        done
    done
    
    cleanup_tmp_directory
    test_output "Module 2 inference complete!" "SUCCESS"
}

# Run if called directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    test_module2
fi
