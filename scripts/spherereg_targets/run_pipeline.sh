#!/bin/bash
# Reproduce the MSMAll -> sphere.reg re-expression of the HCP retinotopy training
# targets (polar angle, eccentricity, pRF size, R2; fits 1-3) and the myelin input,
# for all 181 participants. See README.md in this folder and the run report in
# sandbox/spherereg_targets/report.md.
#
# Usage:
#   run_pipeline.sh            # run every stage in order (skips nothing)
#   run_pipeline.sh <stage>    # run a single stage by name
#
# Stages: download checkpoint0 extract resample analyze mats checkpoint4 loader plots export repro
#
# Requirements (as used for the 2026-10-09 run):
#   - Connectome Workbench 1.5.0 via deepretinotopy_1.0.18_20250909.simg (wrapper: ./wb)
#   - conda env deepretinotopy_2 (python 3.12.8, numpy 2.0.1, scipy 1.15.1, nibabel 5.3.2)
#   - conda env deepretinotopy_validation_plot (matplotlib) for the plots stage
#   - AWS CLI with credentials able to read s3://hcp-openaccess
#   - Slurm (resample stage submits resample_all.sbatch; account a_ai_collab)
#
# Paths are fixed to this filesystem on purpose (exact provenance of the run):
#   toolbox   /scratch/project_mnt/S0210/deepRetinotopy_TheToolbox
#   workdir   <toolbox>/sandbox/spherereg_targets  (hardcoded inside the stage scripts;
#             change lib.py / resample_subject.sh / download_subject.sh together if moving)
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
TOOLBOX=/scratch/project_mnt/S0210/deepRetinotopy_TheToolbox
WORK=$TOOLBOX/sandbox/spherereg_targets
PY() { conda run -n deepretinotopy_2 python "$@"; }

stage_download() {
    mkdir -p $WORK/{hcp,gii,mat,checks,templates}
    # subject list from the .mat field names (181 subjects)
    PY $HERE/mk_subjects.py
    # per-subject HCP S1200 surfaces + native myelin; "pilot" adds the 32k sphere and
    # 32k MSMAll myelin used by checkpoints 0 and 1b
    for s in 100610 102311 102816 104416 105923; do $HERE/download_subject.sh $s pilot; done
    cat $WORK/subjects.txt | xargs -P 8 -I{} $HERE/download_subject.sh {}
    # canonical template spheres: the (subject-invariant) fs_LR 32k sphere and the 2016
    # fs_LR-deformed_to-fsaverage spheres from the toolbox templates/ (checksums in report)
    PY - <<'PYEOF'
import shutil
W='/scratch/project_mnt/S0210/deepRetinotopy_TheToolbox/sandbox/spherereg_targets'
R='/scratch/project_mnt/S0210/deepRetinotopy_TheToolbox'
for H in 'LR':
    shutil.copy2(f'{W}/hcp/100610/100610.{H}.sphere.32k_fs_LR.surf.gii',
                 f'{W}/templates/S1200.{H}.sphere.32k_fs_LR.surf.gii')
    shutil.copy2(f'{R}/templates/fs_LR-deformed_to-fsaverage.{H}.sphere.32k_fs_LR.surf.gii',
                 f'{W}/templates/fs_LR-deformed_to-fsaverage.{H}.sphere.32k_fs_LR.surf.gii')
PYEOF
}

stage_checkpoint0() {
    PY $HERE/checkpoint0_full.py          # file census + native vertex-count identity
    PY $HERE/provenance_census.py         # curvature provenance, all 362 files
    PY $HERE/cp1b2.py                     # cifti_curv_all.mat is NOT the training curvature
}

stage_extract() {
    # .mat -> per-subject GIFTI columns (cos/sin PA, ecc, pRF, R2, validity; fits 1-3)
    PY $HERE/extract_giftis.py --fits fit1 fit2 fit3 \
        --subjects $(cat $WORK/subjects.txt | tr '\n' ' ')
}

stage_resample() {
    # all wb_command steps per subject (steps 2-3, round trips, geometry, myelin routes)
    sbatch --wait $HERE/resample_all.sbatch
    n=$(ls $WORK/gii/*/targets.rh.32k_sphereregRT.func.gii | wc -l)
    [ "$n" -eq 181 ] || { echo "resample incomplete: $n/181"; exit 1; }
}

stage_analyze() {
    PY $HERE/analyze_full.py              # checkpoints 0.3, 1.2, 2.1-2.3, 3.1-3.2 -> CSV
    PY $HERE/cp23_extra.py                # criterion exceedance counts + cp3.3 consistency
}

stage_mats() {
    PY $HERE/write_mats.py                # the 11 cifti_*_all_spherereg.mat files
}

stage_checkpoint4() {
    PY $HERE/checkpoint4.py               # coverage, distributions, ranges, split halves
}

stage_loader() {
    PY $HERE/loader_test.py               # read_HCP on the new files (checkpoint 4.5)
}

stage_plots() {
    conda run -n deepretinotopy_validation_plot python $HERE/visual_check.py   # checkpoint 4.6
}

stage_export() {
    # per-subject empirical GIFTIs into HCP/freesurfer/<sub>/surf/ (-spherereg token at 32k)
    PY $HERE/export_empirical_giftis.py
}

stage_repro() {
    # checkpoint 5: one participant end-to-end must be byte-identical
    md5sum $WORK/gii/100610/* | sort > $WORK/checks/repro_before.md5
    PY $HERE/extract_giftis.py --fits fit1 fit2 fit3 --subjects 100610
    $HERE/resample_subject.sh 100610 pilot
    md5sum $WORK/gii/100610/* | sort > $WORK/checks/repro_after.md5
    diff $WORK/checks/repro_before.md5 $WORK/checks/repro_after.md5 \
        && echo "repro: byte-identical" || { echo "repro: DIFFERENCES"; exit 1; }
}

STAGES="download checkpoint0 extract resample analyze mats checkpoint4 loader plots export repro"
if [ $# -ge 1 ]; then
    stage_$1
else
    for s in $STAGES; do
        echo "=== stage: $s ==="
        stage_$s
    done
fi
echo "pipeline done"
