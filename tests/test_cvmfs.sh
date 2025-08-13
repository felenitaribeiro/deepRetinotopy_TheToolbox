export DEBIAN_FRONTEND=noninteractive

echo "[DEBUG]: mkdir directories for bind mounts"
sudo mkdir -p /storage/deep_retinotopy/data
sudo mkdir -p /storage/deep_retinotopy/templates


echo "[DEBUG]: lmod configuration"
export APPTAINER_BINDPATH='/cvmfs,/mnt,/home,/storage,/storage/deep_retinotopy/data,/storage/deep_retinotopy/templates'
# Setting up the environment for LMOD
export LMOD_CMD=/usr/share/lmod/lmod/libexec/lmod
# Create the module/ml function directly
module() { eval $($LMOD_CMD bash "$@") 2>/dev/null; }
export -f module

ml() { module load "$@"; }
export -f ml

# add neurodesk modules
module use /cvmfs/neurodesk.ardc.edu.au/neurodesk-modules/*
ml deepretinotopy

# REMINDER: Uncomment the following lines if you want to download data from OSF - RUNNER HAVE PERSISTENT STORAGE
# echo "[DEBUG]: data download from osf"
# echo -e "[osf]\nproject = $OSF_PROJECT_ID\nusername = $OSF_USERNAME" > ~/.osfcli.config
# osf -p 4p6yk list > /tmp/osf_list.txt
# for i in $(cat /tmp/osf_list.txt);
# do
#    path=${i:10} 
#    sudo mkdir -p /storage/deep_retinotopy${path%/*}
#    sudo chmod 777 /storage/deep_retinotopy${path%/*}
#    osf -p 4p6yk fetch $i /storage/deep_retinotopy${i:10} 
#    echo $i
# done

# cd /storage/deep_retinotopy/data/1/
# unzip surf.zip
# rm surf.zip
# sudo chmod 777 -R /storage/deep_retinotopy/data/

echo "[DEBUG]: test if deepRetinotopy repo is cloned"
# use the runner name form current path to create a unique directory
current_dir=$(pwd)
tmp_dir=${current_dir:9:32}
echo "Current directory: $tmp_dir"

if find .-name "deepRetinotopy" -size +0 | grep -q '.'; then
    echo "deepRetinotopy repo is cloned"
else
    echo "deepRetinotopy repo is not cloned"
fi
sudo mkdir -p /storage/deep_retinotopy/$tmp_dir/deepRetinotopy_TheToolbox/
sudo chmod 777 /storage/deep_retinotopy/$tmp_dir/deepRetinotopy_TheToolbox/
cp -r ./* /storage/deep_retinotopy/$tmp_dir/deepRetinotopy_TheToolbox/

export tmp_dir

echo "Testing general settings done!"
