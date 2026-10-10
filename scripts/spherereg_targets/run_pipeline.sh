#!/bin/bash
# Reproduce the MSMAll -> sphere.reg re-expression of the HCP retinotopy training
# targets (polar angle, eccentricity, pRF size, R2; fits 1-3) and the myelin input,
# for all 181 participants. See README.md in this folder and report.md (run of record).
#
# Pipeline steps are the numbered scripts (1_ .. 5_); validation lives in checks/,
# code tests in tests/.
#
# Usage:
#   run_pipeline.sh            # run every stage in order (skips nothing)
#   run_pipeline.sh <stage>    # run a single stage by name
#
# Stages: download checkpoint0 extract resample analyze mats checkpoint4 loader plots export repro tests
#
# Requirements (as used for the 2026-10-09 run):
#   - Connectome Workbench 1.5.0 via deepretinotopy_1.0.18_20250909.simg (wrapper: ./wb)
#   - conda env deepretinotopy_2 (python 3.12.8, numpy 2.0.1, scipy 1.15.1, nibabel 5.3.2)
#   - conda env deepretinotopy_validation_plot (matplotlib) for the plots stage
#   - AWS CLI with credentials able to read s3://hcp-openaccess
#   - Slurm (resample stage submits 3_resample_all.sbatch; account a_ai_collab)
#
# Paths are fixed to this filesystem on purpose (exact provenance of the run):
#   toolbox   /scratch/project_mnt/S0210/deepRetinotopy_TheToolbox
#   workdir   <toolbox>/sandbox/spherereg_targets  (hardcoded inside the stage scripts;
#             change lib.py / 1_download_hcp.sh / 3_resample_subject.sh together if moving)
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
WORK=/scratch/project_mnt/S0210/deepRetinotopy_TheToolbox/sandbox/spherereg_targets
PY() { conda run -n deepretinotopy_2 python "$@"; }

stage_download() {
    $HERE/1_download_hcp.sh            # subject list + S3 surfaces/myelin + templates
}

stage_checkpoint0() {
    PY $HERE/checks/checkpoint0_inputs.py   # census, vertex counts, provenance, 1b.2
}

stage_extract() {
    # .mat -> per-subject GIFTI columns (cos/sin PA, ecc, pRF, R2, validity; fits 1-3)
    PY $HERE/2_extract_giftis.py --fits fit1 fit2 fit3 \
        --subjects $(cat $WORK/subjects.txt | tr '\n' ' ')
}

stage_resample() {
    # all wb_command steps per subject (steps 2-3, round trips, geometry, myelin routes)
    sbatch --wait $HERE/3_resample_all.sbatch
    n=$(ls $WORK/gii/*/targets.rh.32k_sphereregRT.func.gii | wc -l)
    [ "$n" -eq 181 ] || { echo "resample incomplete: $n/181"; exit 1; }
}

stage_analyze() {
    PY $HERE/checks/checkpoint2_3_analyze.py       # checkpoints 1.2, 2.1-2.3, 3.1-3.2 -> CSV
    PY $HERE/checks/checkpoint2_3_consistency.py   # criterion exceedances + cp3.3 consistency
}

stage_mats() {
    PY $HERE/4_write_mats.py           # the 11 cifti_*_all_spherereg.mat files
}

stage_checkpoint4() {
    PY $HERE/checks/checkpoint4.py     # coverage, distributions, ranges, split halves
}

stage_loader() {
    PY $HERE/checks/checkpoint4_loader.py   # read_HCP on the new files (checkpoint 4.5)
}

stage_plots() {
    conda run -n deepretinotopy_validation_plot python $HERE/checks/checkpoint4_visual.py  # 4.6
}

stage_export() {
    # per-subject empirical GIFTIs into HCP/freesurfer/<sub>/surf/ (-spherereg token at 32k)
    PY $HERE/5_export_empirical_giftis.py
}

stage_repro() {
    # checkpoint 5: one participant end-to-end must be byte-identical
    md5sum $WORK/gii/100610/* | sort > $WORK/checks/repro_before.md5
    PY $HERE/2_extract_giftis.py --fits fit1 fit2 fit3 --subjects 100610
    $HERE/3_resample_subject.sh 100610 pilot
    md5sum $WORK/gii/100610/* | sort > $WORK/checks/repro_after.md5
    diff $WORK/checks/repro_before.md5 $WORK/checks/repro_after.md5 \
        && echo "repro: byte-identical" || { echo "repro: DIFFERENCES"; exit 1; }
}

stage_tests() {
    # code tests for the HCP_spherereg reader (not part of the data pipeline)
    PY $HERE/tests/reader_equiv_test.py
    PY $HERE/tests/dataset_smoke_test.py
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
