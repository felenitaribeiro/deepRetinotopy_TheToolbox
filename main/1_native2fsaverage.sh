#!/bin/sh

# export FREESURFER_HOME=/usr/local/freesurfer
# source $FREESURFER_HOME/SetUpFreeSurfer.sh

while getopts s:t:h: flag
do
    case "${flag}" in
        s) dirSubs=${OPTARG};;
        t) dirHCP=${OPTARG};;
        h) hemisphere=${OPTARG};;
	?)
		echo "script usage: $(basename "$0") [-s path to subs] [-t path to HCP surfaces] [-h hemisphere]" >&2
		exit 1
	esac
done

echo "Path: $dirSubs";
echo "Hemisphere: $hemisphere";
echo "Resampling native to fsaverage space...";

for i in `ls $dirSubs`; 
do 
 mris_expand -thickness $dirSubs/surf/"$hemisphere".white 0.5 graymid
 mris_curvature -w $dirSubs/surf/"$hemisphere".graymid
 wb_shortcuts -freesurfer-resample-prep $dirSubs/surf/"$hemisphere".white $dirSubs/surf/"$hemisphere".pial \
 $dirSubs/surf/"$hemisphere".sphere.reg ./$dirHCP/fs_LR-deformed_to-fsaverage.L.sphere.32k_fs_LR.surf.gii \
 $dirSubs/surf/"$hemisphere".midthickness.surf.gii $dirSubs/surf/"$dirSubs"."$hemisphere".midthickness.32k_fs_LR.surf.gii $dirSubs/surf/"$hemisphere".sphere.reg.surf.gii
 mris_convert -c $dirSubs/surf/"$hemisphere".graymid.H $dirSubs/surf/"$hemisphere".graymid $dirSubs/surf/"$hemisphere".graymid.H.gii
 wb_command -metric-resample $dirSubs/surf/"$hemisphere".graymid.H.gii \
 $dirSubs/surf/"$hemisphere".sphere.reg.surf.gii $dirHCP/fs_LR-deformed_to-fsaverage.L.sphere.32k_fs_LR.surf.gii \
 ADAP_BARY_AREA $dirSubs/surf/"$dirSubs".curvature-midthickness."$hemisphere".32k_fs_LR.func.gii \
 -area-surfs $dirSubs/surf/"$hemisphere".midthickness.surf.gii $dirSubs/surf/"$dirSubs"."$hemisphere".midthickness.32k_fs_LR.surf.gii

done


