export DEBIAN_FRONTEND=noninteractive
ls /cvmfs/neurodesk.ardc.edu.au/containers

echo "[DEBUG]: mkdir directories for bind mounts"
sudo mkdir -p /storage/deep_retinotopy/data
sudo mkdir -p /storage/deep_retinotopy/templates

export APPTAINER_BINDPATH='/cvmfs,/mnt,/home,/storage/deep_retinotopy/data,/storage/deep_retinotopy/templates'
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

echo "[DEBUG]: data download from osf"
echo -e "[osf]\nproject = $OSF_PROJECT_ID\nusername = $OSF_USERNAME" > ~/.osfcli.config
osf -p 4p6yk list > /tmp/osf_list.txt
for i in $(cat /tmp/osf_list.txt);
do
   path=${i:10} 
   sudo mkdir -p /storage/deep_retinotopy${path%/*}
   sudo chmod 777 /storage/deep_retinotopy${path%/*}
   osf -p 4p6yk fetch $i /storage/deep_retinotopy${i:10} 
   echo $i
done

cd /storage/deep_retinotopy/data/1/
unzip surf.zip
rm surf.zip
sudo chmod 777 -R /storage/deep_retinotopy/data/

echo "Testing general settings done!"
