#!/usr/bin/env bash
# common_setup.sh - Shared setup functions for deepRetinotopy tests

#################################################################################
# COMMON CONFIGURATION AND SETUP FUNCTIONS
#################################################################################

setup_environment() {
    set -e
    export DEBIAN_FRONTEND=noninteractive
    
    echo "[DEBUG]: Setting up environment..."
    
    # Create bind mount directories
    sudo mkdir -p /storage/deep_retinotopy/data
    sudo mkdir -p /storage/deep_retinotopy/templates

    # LMOD configuration
    export APPTAINER_BINDPATH='/cvmfs,/mnt,/home,/storage,/storage/deep_retinotopy/data,/storage/deep_retinotopy/templates'
    export LMOD_CMD=/usr/share/lmod/lmod/libexec/lmod

    # Create module functions
    module() { eval $($LMOD_CMD bash "$@") 2>/dev/null; }
    export -f module

    ml() { module load "$@"; }
    export -f ml

    # Load neurodesk modules
    module use /cvmfs/neurodesk.ardc.edu.au/neurodesk-modules/*
    ml deepretinotopy
}

setup_unique_directory() {
    echo "[DEBUG]: Setting up unique directory..."
    
    # Create unique directory from current path
    local current_dir=$(pwd)
    export TMP_DIR=${current_dir:9:32}
    echo "Using unique directory: $TMP_DIR"
    
    # Check if deepRetinotopy repo is cloned
    if find . -name "deepRetinotopy" -size +0 | grep -q '.'; then
        echo "deepRetinotopy repo is cloned"
    else
        echo "deepRetinotopy repo is not cloned"
    fi
    
    # Create and setup toolbox directory
    export TOOLBOX_PATH="/storage/deep_retinotopy/$TMP_DIR/deepRetinotopy_TheToolbox/"
    sudo mkdir -p "$TOOLBOX_PATH"
    sudo chmod 777 "$TOOLBOX_PATH"
    cp -r ./* "$TOOLBOX_PATH"
}

setup_data_directories() {
    echo "[DEBUG]: Setting up data directories..."
    
    export DIR_SUBS="/storage/deep_retinotopy/$TMP_DIR/data"
    export DIR_HCP="/storage/deep_retinotopy/templates/"
    export DATASET_NAME="TEST"
    export OUTPUT_DIR="/storage/deep_retinotopy/output/"
    
    echo "Path to freesurfer data: $DIR_SUBS"
    echo "Path to template surfaces: $DIR_HCP"
    echo "Dataset name: $DATASET_NAME"
    
    sudo mkdir -p "$DIR_SUBS"
    sudo chmod 777 "$DIR_SUBS"
    sudo mkdir -p "$OUTPUT_DIR"
    sudo chmod 777 "$OUTPUT_DIR"
    
    # Copy data if it exists
    if [ -d "/storage/deep_retinotopy/data" ]; then
        cp -r /storage/deep_retinotopy/data/* "$DIR_SUBS"
    fi
}

setup_path_and_bins() {
    echo "[DEBUG]: Setting up PATH and DEPLOY_BINS..."
    # Resolve the module's container location BEFORE the repo checkout shadows
    # the deepRetinotopy module wrapper on PATH (and never clobber it if a test
    # already resolved it).
    if [ -z "${DEEPRETINOTOPY_PATH:-}" ] || [ -z "${DEEPRETINOTOPY_DIR:-}" ]; then
        get_deepretinotopy_paths
    fi
    export PATH="$TOOLBOX_PATH:$TOOLBOX_PATH/main/:$TOOLBOX_PATH/utils/:$PATH"
    export DEPLOY_BINS="wb_view:wb_command:wb_shortcuts:python:deepRetinotopy:signMaps:1_native2fsaverage.sh:2_inference.py:3_fsaverage2native.sh:4_signmaps.py:transform_polarangle_lh.py:reconstruct_coords_native.py:midthickness_surf.py:mris_convert:mris_curvature:mris_expand"

    # Step 1 fail-fast checks require FreeSurfer tools (mris_convert,
    # mris_curvature, mris_expand). Released modules <= 1.0.19 never exposed
    # them on the host PATH (they are in deploy.bins from 1.1.0), so shim any
    # missing one by exec'ing into the container sandbox the module ships.
    local runtime sandbox tool
    runtime=$(command -v apptainer || command -v singularity || true)
    sandbox="$DEEPRETINOTOPY_PATH/$DEEPRETINOTOPY_DIR.simg"
    if [ -n "$runtime" ] && [ -e "$sandbox" ]; then
        mkdir -p "$TOOLBOX_PATH/fs_bins"
        for tool in mris_convert mris_curvature mris_expand; do
            if ! command -v "$tool" > /dev/null; then
                printf '#!/usr/bin/env bash\nexec "%s" exec "%s" %s "$@"\n' \
                    "$runtime" "$sandbox" "$tool" > "$TOOLBOX_PATH/fs_bins/$tool"
                chmod +x "$TOOLBOX_PATH/fs_bins/$tool"
            fi
        done
        export PATH="$TOOLBOX_PATH/fs_bins:$PATH"
    fi
}

get_deepretinotopy_paths() {
    local executable=$(which deepRetinotopy)
    echo "DeepRetinotopy executable: $executable"
    
    export DEEPRETINOTOPY_PATH=${executable%/*}
    export DEEPRETINOTOPY_DIR=${DEEPRETINOTOPY_PATH##*/}
    
    echo "DeepRetinotopy path: $DEEPRETINOTOPY_PATH"
    echo "DeepRetinotopy dir: $DEEPRETINOTOPY_DIR"
}

setup_subject_directories() {
    for i in $(ls "$DIR_SUBS" 2>/dev/null || echo ""); do
        if [ -d "$DIR_SUBS/$i" ]; then
            sudo chmod 777 "$DIR_SUBS/$i"
            sudo mkdir -p "$DIR_SUBS/$i/deepRetinotopy/"
            sudo chmod 777 "$DIR_SUBS/$i/deepRetinotopy/"
        fi
    done
}

cleanup_tmp_directory() {
    echo "[DEBUG]: Cleaning up temporary directory..."
    sudo rm -rf "/storage/deep_retinotopy/$TMP_DIR" 2>/dev/null || true
}

copy_models() {
    local map=$1
    echo "[DEBUG]: Copying models for $map..."
    
    sudo mkdir -p "$TOOLBOX_PATH/models/"
    sudo chmod 777 "$TOOLBOX_PATH"
    
    # Only copy if the model files don't already exist
    if ! ls "$TOOLBOX_PATH/models/deepRetinotopy_${map}_"* 1> /dev/null 2>&1; then
        echo "No deepRetinotopy_${map} model files found in destination, copying..."
        sudo cp -r "$DEEPRETINOTOPY_PATH/$DEEPRETINOTOPY_DIR.simg/opt/deepRetinotopy_TheToolbox/models/deepRetinotopy_${map}_"* "$TOOLBOX_PATH/models/"
    else
        echo "deepRetinotopy_${map} model files already exist in destination, skipping copy"
    fi
}

clean_models() {
    echo "[DEBUG]: Cleaning models..."
    sudo rm -r "$TOOLBOX_PATH/models/"* 2>/dev/null || true
}

test_output() {
    local message=$1
    local status=${2:-"INFO"}
    echo "[$status]: $message"
}

# Common initialization function
common_init() {
    echo "[DEBUG]: General configuration for testing deepRetinotopy"

    setup_environment
    setup_unique_directory
    setup_data_directories
    setup_path_and_bins
}
# End of common setup functions