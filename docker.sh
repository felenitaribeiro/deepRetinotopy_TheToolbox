docker pull vnmd/deepretinotopy_1.0.1:latest
docker run -t -d -v ~:/tmp --name deepret vnmd/deepretinotopy_1.0.1:latest
docker exec -it deepret

export FS_LICENSE=/tmp/Desktop/deepRetinotopy_general/freesurfer/license.txt
source /opt/freesurfer-7.1.1/SetUpFreeSurfer.sh

cd /tmp/Projects/deepRetinotopy_TheToolbox/main
bash 1_native2fsaverage.sh -s /tmp/Desktop/deepRetinotopy_general/4Fernanda/ -t /tmp/Desktop/deepRetinotopy_general/standard_mesh_atlases/resample_fsaverage/ -h lh 
