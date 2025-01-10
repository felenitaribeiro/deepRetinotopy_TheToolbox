#!/usr/bin/env bash

while getopts s:h:t:r:m: flag
do
  case "${flag}" in
    s) dirSubs=${OPTARG};;
    t) dirHCP=${OPTARG};;
    h) hemisphere=${OPTARG};
       case "$hemisphere" in
         lh|rh) ;;
         *) echo "Invalid hemisphere argument: $hemisphere"; exit 1;;
       esac;;
    r) map=${OPTARG};
       case "$map" in
         'polarAngle'|'eccentricity'|'pRFsize') ;;
         *) echo "Invalid map argument: $map"; exit 1;;
       esac;;
    m) model=${OPTARG};
       case "$model" in
         model1|model2|model3|model4|model5|average) ;;
         *) echo "Invalid model argument: $model"; exit 1;;
       esac;;
    ?)
      echo "script usage: $(basename "$0") [-s path to subs] [-t path to HCP surfaces] [-h hemisphere] [-r map] [-m model]" >&2
      exit 1;;
  esac
done

echo "Model: $model";

cd $dirSubs
for dirSub in `ls $dirSubs`; 
do 
  if [ "$dirSub" == "fsaverage" ]; then 
        echo "Skipping fsaverage directory..."
        continue
  else
    if [ ! -f $dirSub"/deepRetinotopy/"$dirSub".fs_predicted_"$map"_"$hemisphere"_curvatureFeat_"$model".func.gii" ]; then
      echo "Predicted map is not available for subject $dirSub"
      exit 1
    else
      if [ "$hemisphere" == 'lh' ]; then
        wb_command -metric-resample $dirSub/deepRetinotopy/"$dirSub".fs_predicted_"$map"_"$hemisphere"_curvatureFeat_"$model".func.gii \
        $dirHCP/fs_LR-deformed_to-fsaverage.L.sphere.32k_fs_LR.surf.gii \
        $dirSub/surf/"$hemisphere".sphere.reg.surf.gii ADAP_BARY_AREA $dirSub/deepRetinotopy/"$dirSub".predicted_"$map"_"$model"."$hemisphere".native.func.gii \
        -area-surfs $dirSub/surf/"$dirSub"."$hemisphere".midthickness.32k_fs_LR.surf.gii $dirSub/surf/"$hemisphere".midthickness.surf.gii
        # to edit
        transform_polarangle_lh.py --path $dirSub/deepRetinotopy/       
      else
        wb_command -metric-resample $dirSub/deepRetinotopy/"$dirSub".fs_predicted_"$map"_"$hemisphere"_curvatureFeat_"$model".func.gii \
        $dirHCP/fs_LR-deformed_to-fsaverage.R.sphere.32k_fs_LR.surf.gii \
        $dirSub/surf/"$hemisphere".sphere.reg.surf.gii ADAP_BARY_AREA $dirSub/deepRetinotopy/"$dirSub".predicted_"$map"_"$model"."$hemisphere".native.func.gii \
        -area-surfs $dirSub/surf/"$dirSub"."$hemisphere".midthickness.32k_fs_LR.surf.gii $dirSub/surf/"$hemisphere".midthickness.surf.gii
      fi
    fi
  fi
done