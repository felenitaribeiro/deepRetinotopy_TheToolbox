#!/usr/bin/env bash
set -e

# Get the directory where the current script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Source the common setup file
source "$SCRIPT_DIR/common_setup.sh"

test_module1() {
    common_init
    
    cd "$TOOLBOX_PATH"
    
    # Clean existing surfaces for testing
    rm -f "$DIR_SUBS"/*/surf/*curvature-midthickness* 2>/dev/null || true
    rm -f "$DIR_SUBS"/*/surf/*graymid* 2>/dev/null || true
    
    export DEPLOY_BINS="midthickness_surf.py:$DEPLOY_BINS"
    
    cd main
    
    for hemisphere in lh rh; do
        echo "Hemisphere: $hemisphere"
        echo "[DEBUG]: Module 1: Generating mid-thickness surface and curvature data..."
        
        local command="./1_native2fsaverage.sh -s $DIR_SUBS -t $DIR_HCP -h $hemisphere -g yes"
        echo "$command"
        eval "$command"

        # Validate outputs
        if find "$DIR_SUBS" -name "*${hemisphere}.midthickness.32k_fs_LR.surf.gii" -size +0 | grep -q '.'; then
            test_output "Mid-thickness surface generated for $hemisphere" "SUCCESS"
        else
            test_output "Mid-thickness surface NOT generated for $hemisphere" "ERROR"
        fi

        if find "$DIR_SUBS" -name "*curvature-midthickness.${hemisphere}.32k_fs_LR.func.gii" -size +0 | grep -q '.'; then
            test_output "Curvature data generated for $hemisphere" "SUCCESS"
        else
            test_output "Curvature data NOT generated for $hemisphere" "ERROR"
        fi
    done
    
    cleanup_tmp_directory
    test_output "Module 1 test complete!" "SUCCESS"
}

# Run if called directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    test_module1
fi
