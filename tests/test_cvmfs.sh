export DEBIAN_FRONTEND=noninteractive
sudo wget https://github.com/apptainer/apptainer/releases/download/v1.1.5/apptainer_1.1.5_amd64.deb
sudo apt-get install -y ./apptainer_1.1.5_amd64.deb

echo "[DEBUG]: CVMFS set up"

sudo apt-get install lsb-release
wget https://ecsft.cern.ch/dist/cvmfs/cvmfs-release/cvmfs-release-latest_all.deb

echo "[DEBUG]: adding cvmfs repo"
sudo dpkg -i cvmfs-release-latest_all.deb

echo "[DEBUG]: apt-get update"
sudo apt-get update --allow-unauthenticated

echo "[DEBUG]: apt-get install cvmfs"
sudo apt-get install -y cvmfs lmod --allow-unauthenticated 

sudo mkdir -p /etc/cvmfs/keys/ardc.edu.au/


echo "-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAwUPEmxDp217SAtZxaBep
Bi2TQcLoh5AJ//HSIz68ypjOGFjwExGlHb95Frhu1SpcH5OASbV+jJ60oEBLi3sD
qA6rGYt9kVi90lWvEjQnhBkPb0uWcp1gNqQAUocybCzHvoiG3fUzAe259CrK09qR
pX8sZhgK3eHlfx4ycyMiIQeg66AHlgVCJ2fKa6fl1vnh6adJEPULmn6vZnevvUke
I6U1VcYTKm5dPMrOlY/fGimKlyWvivzVv1laa5TAR2Dt4CfdQncOz+rkXmWjLjkD
87WMiTgtKybsmMLb2yCGSgLSArlSWhbMA0MaZSzAwE9PJKCCMvTANo5644zc8jBe
NQIDAQAB
-----END PUBLIC KEY-----" | sudo tee /etc/cvmfs/keys/ardc.edu.au/neurodesk.ardc.edu.au.pub


echo "CVMFS_USE_GEOAPI=yes" | sudo tee /etc/cvmfs/config.d/neurodesk.ardc.edu.au.conf
echo 'CVMFS_SERVER_URL="http://cvmfs1.neurodesk.org/cvmfs/@fqrn@;http://cvmfs2.neurodesk.org/cvmfs/@fqrn@;http://cvmfs3.neurodesk.org/cvmfs/@fqrn@"' | sudo tee -a /etc/cvmfs/config.d/neurodesk.ardc.edu.au.conf 
echo 'CVMFS_KEYS_DIR="/etc/cvmfs/keys/ardc.edu.au/"' | sudo tee -a /etc/cvmfs/config.d/neurodesk.ardc.edu.au.conf
echo "CVMFS_HTTP_PROXY=DIRECT" | sudo tee  /etc/cvmfs/default.local
echo "CVMFS_QUOTA_LIMIT=5000" | sudo tee -a  /etc/cvmfs/default.local

sudo cvmfs_config setup
sudo cvmfs_config chksetup

ls /cvmfs/neurodesk.ardc.edu.au/containers

cvmfs_config stat -v neurodesk.ardc.edu.au

echo "[DEBUG]: mkdir directories for bind mounts"
sudo mkdir /data
sudo mkdir /templates
sudo chmod 777 /data
sudo chmod 777 /templates
export APPTAINER_BINDPATH='/cvmfs,/mnt,/home,/data,/templates'

echo "[DEBUG]: module setup"
echo "# system-wide profile.modules                                          #
# Initialize modules for all sh-derivative shells                      #
#----------------------------------------------------------------------#
trap "" 1 2 3

case "$0" in
    -bash|bash|*/bash) . /usr/share/lmod/6.6/init/bash ;;
       -ksh|ksh|*/ksh) . /usr/share/lmod/6.6/init/ksh ;;
       -zsh|zsh|*/zsh) . /usr/share/lmod/6.6/init/zsh ;;
          -sh|sh|*/sh) . /usr/share/lmod/6.6/init/sh ;;
                    *) . /usr/share/lmod/6.6/init/sh ;;  # default for scripts
esac

trap - 1 2 3
" | sudo tee /usr/share/module.sh

source /usr/share/module.sh
module use /cvmfs/neurodesk.ardc.edu.au/neurodesk-modules/*
ml deepretinotopy/1.0.2
mris_expand

echo "[DEBUG]: data download from osf"
echo -e "[osf]\nproject = $OSF_PROJECT_ID\nusername = $OSF_USERNAME" > ~/.osfcli.config
osf -p 4p6yk list > /tmp/osf_list.txt
for i in $(cat /tmp/osf_list.txt);
do
   path=${i:10} 
   sudo mkdir -p ${path%/*}
   sudo chmod 777 ${path%/*}
   osf -p 4p6yk fetch $i ${i:10} 
   echo $i
done

cd /data/1/
unzip surf.zip
rm surf.zip
sudo chmod 777 -R /data/

echo "Testing general settings done!"
