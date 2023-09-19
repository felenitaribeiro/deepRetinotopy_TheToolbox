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

cd $dirSubs
for dirSub in `ls $dirSubs`; 
do 
  wb_command -metric-resample $dirSub/deepRetinotopy/"$dirSub".fs_predicted_"$map"_"$hemisphere"_curvatureFeat_"$model".func.gii \
  $dirHCP/fs_LR-deformed_to-fsaverage.L.sphere.32k_fs_LR.surf.gii \
  $dirSub/surf/"$hemisphere".sphere.reg.surf.gii ADAP_BARY_AREA $dirSub/"$dirSub".predicted_"$map"_"$model"."$hemisphere".native.func.gii \
  -area-surfs $dirSub/surf/"$dirSub"."$hemisphere".midthickness.32k_fs_LR.surf.gii $dirSub/surf/"$hemisphere".midthickness.surf.gii
done
