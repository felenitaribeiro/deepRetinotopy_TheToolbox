#!/bin/bash
#SBATCH --job-name=sreg_resample
#SBATCH --account=a_ai_collab
#SBATCH --partition=general
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=24
#SBATCH --mem=48G
#SBATCH --time=04:00:00
#SBATCH --output=/scratch/project_mnt/S0210/deepRetinotopy_TheToolbox/sandbox/spherereg_targets/resample_all_%j.log

WORK=/scratch/project_mnt/S0210/deepRetinotopy_TheToolbox/sandbox/spherereg_targets
SCRIPTS=/scratch/project_mnt/S0210/deepRetinotopy_TheToolbox/scripts/spherereg_targets
cat $WORK/subjects.txt | xargs -P 12 -I{} bash -c \
  "$SCRIPTS/resample_subject.sh {} pilot > $WORK/gii/{}.resample.log 2>&1 || echo 'FAILED {}'"
echo "all done"
