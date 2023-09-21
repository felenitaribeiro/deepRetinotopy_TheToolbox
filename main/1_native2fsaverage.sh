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

cd $dirSubs
for dirSub in `ls .`; 
do 
    echo "Generating mid-thickness surface and curvature data..."
    mris_expand -thickness $dirSub/surf/"$hemisphere".white 0.5 $dirSub/surf/"$hemisphere".graymid
    mris_curvature -w $dirSub/surf/"$hemisphere".graymid
    
    echo "Preparing native surfaces for resampling..."
    wb_shortcuts -freesurfer-resample-prep $dirSub/surf/"$hemisphere".white $dirSub/surf/"$hemisphere".pial \
    $dirSub/surf/"$hemisphere".sphere.reg $dirHCP/fs_LR-deformed_to-fsaverage.L.sphere.32k_fs_LR.surf.gii \
    $dirSub/surf/"$hemisphere".midthickness.surf.gii $dirSub/surf/"$dirSub"."$hemisphere".midthickness.32k_fs_LR.surf.gii \
    $dirSub/surf/"$hemisphere".sphere.reg.surf.gii
    mris_convert -c $dirSub/surf/"$hemisphere".graymid.H $dirSub/surf/"$hemisphere".graymid $dirSub/surf/"$hemisphere".graymid.H.gii
    
    echo "Resampling native to fsaverage space..."
    wb_command -metric-resample $dirSub/surf/"$hemisphere".graymid.H.gii \
    $dirSub/surf/"$hemisphere".sphere.reg.surf.gii $dirHCP/fs_LR-deformed_to-fsaverage.L.sphere.32k_fs_LR.surf.gii \
    ADAP_BARY_AREA $dirSub/surf/"$dirSub".curvature-midthickness."$hemisphere".32k_fs_LR.func.gii \
    -area-surfs $dirSub/surf/"$hemisphere".midthickness.surf.gii $dirSub/surf/"$dirSub"."$hemisphere".midthickness.32k_fs_LR.surf.gii
done


