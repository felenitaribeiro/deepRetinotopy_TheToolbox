#!/usr/bin/env bash

while getopts s:t:h:g: flag
do
    case "${flag}" in
        s) dirSubs=${OPTARG};;
        t) dirHCP=${OPTARG};;
        h) hemisphere=${OPTARG};
           case "$hemisphere" in
               lh|rh) ;;
               *) echo "Invalid hemisphere argument: $hemisphere"; exit 1;;
           esac;;
        g) fast=${OPTARG};
            case "$fast" in
            'yes'|'no') ;;
            *) echo "Invalid fast argument: $fast"; exit 1;;
            esac;;
        ?)
            echo "script usage: $(basename "$0") [-s path to subs] [-t path to HCP surfaces] [-h hemisphere]  [-g fast generation of midthickness surface]" >&2
            exit 1;;
    esac
done

echo "Hemisphere: $hemisphere";

cd $dirSubs
for dirSub in `ls .`; 
do 
    # exclude fsaverage directory
    if [ "$dirSub" == "fsaverage" ]; then 
        echo "Skipping fsaverage directory..."
        continue
    else
        if [ -d $dirSub/surf ]; then
            start_time=`date +%s`
            if [ "$fast" == 'yes' ]; then
                echo "Fast mode enabled."
                echo "[Step 1.1] Generating mid-thickness surface and curvature data if not available..."
                if [ ! -f $dirSub/surf/"$hemisphere".graymid ]; then
                    if [ ! -f $dirSub/surf/"$hemisphere".white ]; then
                        echo "No white surface found for subject $dirSub"
                        exit 1
                    else
                        mris_convert $dirSub/surf/"$hemisphere".white $dirSub/surf/"$hemisphere".white.gii
                        mris_convert $dirSub/surf/"$hemisphere".pial $dirSub/surf/"$hemisphere".pial.gii
                        python ./../utils/midthickness_surf.py --path $dirSub/surf/ --hemisphere $hemisphere # add to PATH
                        mris_convert $dirSub/surf/"$hemisphere".graymid.gii $dirSub/surf/"$hemisphere".graymid
                        mris_curvature -w $dirSub/surf/"$hemisphere".graymid
                    fi
                    echo "Mid-thickness surface has been generated."
                else 
                    echo "Mid-thickness surface and curvature data is already available."
                fi
            else
                echo "[Step 1.1] Generating mid-thickness surface and curvature data if not available..."
                if [ ! -f $dirSub/surf/"$hemisphere".graymid ]; then
                    if [ ! -f $dirSub/surf/"$hemisphere".white ]; then
                        echo "No white surface found for subject $dirSub"
                        exit 1
                    else
                        mris_expand -thickness $dirSub/surf/"$hemisphere".white 0.5 $dirSub/surf/"$hemisphere".graymid
                        mris_curvature -w $dirSub/surf/"$hemisphere".graymid
                    fi
                    echo "Mid-thickness surface has been generated."
                else 
                    echo "Mid-thickness surface and curvature data is already available."
                fi
            fi    
            echo "[Step 1.2] Preparing native surfaces for resampling if not available..."
            if [ ! -f $dirSub/surf/"$dirSub".curvature-midthickness."$hemisphere".32k_fs_LR.func.gii ]; then
                if [ "$hemisphere" == 'lh' ]; then
                    wb_shortcuts -freesurfer-resample-prep $dirSub/surf/"$hemisphere".white $dirSub/surf/"$hemisphere".pial \
                    $dirSub/surf/"$hemisphere".sphere.reg $dirHCP/fs_LR-deformed_to-fsaverage.L.sphere.32k_fs_LR.surf.gii \
                    $dirSub/surf/"$hemisphere".midthickness.surf.gii $dirSub/surf/"$dirSub"."$hemisphere".midthickness.32k_fs_LR.surf.gii \
                    $dirSub/surf/"$hemisphere".sphere.reg.surf.gii
                    mris_convert -c $dirSub/surf/"$hemisphere".graymid.H $dirSub/surf/"$hemisphere".graymid $dirSub/surf/"$hemisphere".graymid.H.gii
                    
                    echo "Resampling native data to fsaverage space..."
                    wb_command -metric-resample $dirSub/surf/"$hemisphere".graymid.H.gii \
                    $dirSub/surf/"$hemisphere".sphere.reg.surf.gii $dirHCP/fs_LR-deformed_to-fsaverage.L.sphere.32k_fs_LR.surf.gii \
                    ADAP_BARY_AREA $dirSub/surf/"$dirSub".curvature-midthickness."$hemisphere".32k_fs_LR.func.gii \
                    -area-surfs $dirSub/surf/"$hemisphere".midthickness.surf.gii $dirSub/surf/"$dirSub"."$hemisphere".midthickness.32k_fs_LR.surf.gii
                else
                    wb_shortcuts -freesurfer-resample-prep $dirSub/surf/"$hemisphere".white $dirSub/surf/"$hemisphere".pial \
                    $dirSub/surf/"$hemisphere".sphere.reg $dirHCP/fs_LR-deformed_to-fsaverage.R.sphere.32k_fs_LR.surf.gii \
                    $dirSub/surf/"$hemisphere".midthickness.surf.gii $dirSub/surf/"$dirSub"."$hemisphere".midthickness.32k_fs_LR.surf.gii \
                    $dirSub/surf/"$hemisphere".sphere.reg.surf.gii
                    mris_convert -c $dirSub/surf/"$hemisphere".graymid.H $dirSub/surf/"$hemisphere".graymid $dirSub/surf/"$hemisphere".graymid.H.gii
                    
                    echo "Resampling native data to fsaverage space..."
                    wb_command -metric-resample $dirSub/surf/"$hemisphere".graymid.H.gii \
                    $dirSub/surf/"$hemisphere".sphere.reg.surf.gii $dirHCP/fs_LR-deformed_to-fsaverage.R.sphere.32k_fs_LR.surf.gii \
                    ADAP_BARY_AREA $dirSub/surf/"$dirSub".curvature-midthickness."$hemisphere".32k_fs_LR.func.gii \
                    -area-surfs $dirSub/surf/"$hemisphere".midthickness.surf.gii $dirSub/surf/"$dirSub"."$hemisphere".midthickness.32k_fs_LR.surf.gii
                fi
                echo "Data resampling is complete."
            else
                echo "Resampled curvature data is already available."
            fi
            end_time=`date +%s`
            execution_time=$((end_time-start_time))
            execution_time_minutes=$((execution_time / 60))
            echo "Execution time: $execution_time_minutes minutes"         
        else
            echo "No surface directory found for subject $dirSub"
            exit 1
        fi
    fi
done


