#!/bin/sh

while getopts s:t:d: flag
do
    case "${flag}" in
        s) dirSubs=${OPTARG};;
        t) dirHCP=${OPTARG};;
        d) datasetName=${OPTARG};;
	?)
		echo "script usage: $(basename "$0") [-s path to subs] [-t path to HCP surfaces] [-d name of the dataset]" >&2
		exit 1
	esac
done

echo "Path subs directory: $dirSubs";
echo "Path to fs_LR-deformed_to-fsaverage surfaces: $dirHCP";

cd main
for hemisphere in 'lh'; #'rh'
do 
    for map in 'polarAngle'; #, 'eccentricity', 'pRFsize'
    do
        # Inside the container
        echo $hemisphere
        echo "Generating mid-thickness surface and curvature data..."
        bash 1_native2fsaverage.sh -s $dirSubs \
        -t $dirHCP -h $hemisphere 

        echo "Retinotopy prediction..."
        if [ "$hemisphere" == 'lh' ]; then
            python 2_inference.py --path $dirSubs \
        --dataset $datasetName --prediction_type $map --hemisphere Left
        else
            python 2_inference.py --path $dirSubs \
        --dataset $datasetName --prediction_type $map --hemisphere Right
        fi
        rm -r $dirSubs/processed

        echo "Resampling predictions to native space..."
        for model in 1; #, 2, 3, 4, 5
        do
            bash 3_fsaverage2native.sh -s $dirSubs \
            -t $dirHCP -h $hemisphere -r $map -m $model
        done
    done
done