#!/usr/bin/env bash

data_download_setup() {
    setup_environment
    
    echo "[DEBUG]: Testing general settings..."
    
    # REMINDER: This only necessary if the runner doesn't have persistent storage
    echo "[DEBUG]: data download from osf"
    echo -e "[osf]\nproject = $OSF_PROJECT_ID\nusername = $OSF_USERNAME" > ~/.osfcli.config
    osf -p 4p6yk list > /tmp/osf_list.txt
    for i in $(cat /tmp/osf_list.txt); do
        path=${i:10} 
        sudo mkdir -p "/storage/deep_retinotopy${path%/*}"
        sudo chmod 777 "/storage/deep_retinotopy${path%/*}"
        osf -p 4p6yk fetch $i "/storage/deep_retinotopy${i:10}"
        echo $i
    done
    
    cd /storage/deep_retinotopy/data/1/
    unzip surf.zip
    rm surf.zip
    sudo chmod 777 -R /storage/deep_retinotopy/data/

    test_output "Data download complete!" "SUCCESS"
}

# Run if called directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    data_download_setup
fi

