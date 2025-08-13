#!/usr/bin/env bash
set -e

# Get the directory where the current script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Source the common setup file
source "$SCRIPT_DIR/common_setup.sh"

test_signmaps() {
    common_init
    
    echo "[DEBUG]: Visual field sign maps generation"
    
    # Setup deepRetinotopy data
    cd "$DIR_SUBS/1/"
    if [ ! -d "$DIR_SUBS/1/deepRetinotopy/" ]; then
        unzip deepRetinotopy.zip
    else
        echo "deepRetinotopy directory already exists, skipping unzipping"
    fi
    sudo chmod 777 -R "$DIR_SUBS/1/deepRetinotopy/"

    cd "$TOOLBOX_PATH/main"
    signMaps -s "$DIR_SUBS" -t "$DIR_HCP" -d "$DATASET_NAME"

    # Validate output
    local file_path="$DIR_SUBS/1/deepRetinotopy/1.fs_predicted_fieldSignMap_lh_model.func.gii"
    if [ -f "$file_path" ]; then
        test_output "Visual field sign map generated successfully" "SUCCESS"
    else
        test_output "Visual field sign map NOT generated" "ERROR"
        exit 1
    fi
    
    cleanup_tmp_directory
    test_output "Sign maps test complete!" "SUCCESS"
}

# Run if called directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    test_signmaps
fi