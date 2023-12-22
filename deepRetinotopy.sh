#!/bin/sh
exec > >(tee -a deepRetinotopy_output.log)
exec 2> >(tee -a deepRetinotopy_error.log >&2)

while getopts s:t:d:m: flag
do
    case "${flag}" in
        s) dirSubs=${OPTARG};;
        t) dirHCP=${OPTARG};;
        d) datasetName=${OPTARG};;
        m) IFS=',' read -ra maps <<< "${OPTARG}";;
	?)
		echo "script usage: $(basename "$0") [-s path to subs] [-t path to HCP surfaces] [-d name of the dataset] [-m list of maps]" >&2
		exit 1
	esac
done

echo "Path subs directory: $dirSubs";
echo "Path to fs_LR-deformed_to-fsaverage surfaces: $dirHCP";
echo "Dataset name: $datasetName";
echo "Maps: ${maps[@]}";

cd main
for hemisphere in 'lh' 'rh';
do 
    echo "Generating mid-thickness surface and curvature data..."
    bash 1_native2fsaverage.sh -s $dirSubs -t $dirHCP -h $hemisphere 

    if [ $? -eq 1 ]; then
        echo "Error in 1_native2fsaverage.sh"
        exit 1
    else
        for map in "${maps[@]}";
        do

            echo "Retinotopy prediction..."
            python 2_inference.py --path $dirSubs --dataset $datasetName --prediction_type $map --hemisphere $hemisphere

            rm -r $dirSubs/processed

            echo "Resampling predictions to native space..."
            for model in model1 model2 model3 model4 model5 average;
            do
                bash 3_fsaverage2native.sh -s $dirSubs -t $dirHCP -h $hemisphere -r $map -m $model
            done
            echo "$map predictions for $hemisphere are done!"
        done
    fi
done
echo "All done!"