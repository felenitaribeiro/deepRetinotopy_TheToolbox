#!/bin/bash
WORK=/scratch/project_mnt/S0210/deepRetinotopy_TheToolbox/sandbox/spherereg_targets
cat $WORK/subjects.txt | xargs -P 8 -I{} $(cd "$(dirname "$0")" && pwd)/download_subject.sh {} > $WORK/download_all.log 2>&1
echo "exit $?" >> $WORK/download_all.log
grep -c "^done" $WORK/download_all.log
