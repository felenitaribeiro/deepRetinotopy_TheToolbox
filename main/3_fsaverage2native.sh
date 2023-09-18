#!/bin/sh

while getopts s:h:t:r:m: flag
do
    case "${flag}" in
        s) dirSubs=${OPTARG};;
        t) dirHCP=${OPTARG};;
        h) hemisphere=${OPTARG};;
        r) map=${OPTARG};;
        m) model=${OPTARG};;
	?)
		echo "script usage: $(basename "$0") [-s path to subs] [-t path to HCP surfaces] [-h hemisphere] [-r map] [-m model] " >&2
		exit 1
	esac
done

echo "Path: $dirSubs";
echo "Hemisphere: $hemisphere";
echo "Map: $map";
echo "Model: $model";
echo "Resampling fsaverage to native space...";

for i in `ls $dirSubs`; 
do 
  wb_command -metric-resample $dirSubs/predictions/"$dirSubs"_fs_predicted_"$hemisphere"_"$map"_"$model".func.gii \
  $dirHCP/fs_LR-deformed_to-fsaverage.L.sphere.32k_fs_LR.surf.gii \
  $dirSubs/surf/"$hemisphere".sphere.reg.surf.gii ADAP_BARY_AREA $dirSubs/"$dirSubs".predicted_"$map"_"$model"."$hemisphere".native.func.gii \
  -area-surfs $dirSubs/surf/"$dirSubs"."$hemisphere".midthickness.32k_fs_LR.surf.gii $dirSubs/surf/"$hemisphere".midthickness.surf.gii
done
