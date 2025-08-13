#!/usr/bin/env bash
set -e

# Get the directory where the current script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Source the common setup file
source "$SCRIPT_DIR/common_setup.sh"

test_module3() {
    common_init
    
    local model="model"
    echo "Model: $model"
    
    # Setup resampling data
    echo "[DEBUG]: Setting up resampling data..."
    cd /storage/deep_retinotopy/resampling/
    if [ ! -d /storage/deep_retinotopy/resampling/resampling/ ]; then
        unzip resampling.zip
    else
        echo "Resampling directory already exists, skipping unzipping"
    fi
    sudo chmod 777 -R /storage/deep_retinotopy/resampling/
    cp /storage/deep_retinotopy/resampling/resampling/* "$DIR_SUBS/1/deepRetinotopy/" 2>/dev/null || true

    cd "$TOOLBOX_PATH/main"
    export DEPLOY_BINS="$DEPLOY_BINS:transform_polarangle_lh.py"

    for hemisphere in lh; do  # Could expand to rh
        for map in polarAngle; do  # Could expand to others
            echo "Hemisphere: $hemisphere"
            echo "[DEBUG]: Module 3: Resampling data back to native space..."
            
            local command="./3_fsaverage2native.sh -s $DIR_SUBS -t $DIR_HCP -h $hemisphere -r $map -m $model"
            echo "$command"
            eval "$command"

            # Validate output
            if find "$DIR_SUBS" -name "*.predicted_${map}_${model}.${hemisphere}.native.func.gii" -size +0 | grep -q '.'; then
                test_output "Retinotopic map in native surface space generated" "SUCCESS"
            else
                test_output "Retinotopic map in native surface space NOT generated" "ERROR"
                ls -R "$DIR_SUBS" || true
            fi
        done
    done
    
    cleanup_tmp_directory
    test_output "Module 3 resampling complete!" "SUCCESS"
}

# Run if called directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    test_module3
fi
