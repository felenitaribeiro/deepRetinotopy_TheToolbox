#!/bin/bash
# All wb_command resampling steps for one subject.
# Usage: resample_subject.sh <sub> [pilot]
# "pilot" additionally runs the 32k-myelin-route comparison inputs.
set -euo pipefail
sub=$1
pilot=${2:-}
WORK=/scratch/project_mnt/S0210/deepRetinotopy_TheToolbox/sandbox/spherereg_targets
FS=/scratch/project_mnt/S0210/deepRetinotopy_TheToolbox/HCP/freesurfer/$sub/surf
D=$WORK/hcp/$sub
G=$WORK/gii/$sub
T=$WORK/templates
WB=$(cd "$(dirname "$0")" && pwd)/wb

for pair in "L lh" "R rh"; do
  set -- $pair; H=$1; h=$2
  S32=$T/S1200.$H.sphere.32k_fs_LR.surf.gii                      # fs_LR 32k standard sphere
  SNAT_MSM=$D/$sub.$H.sphere.MSMAll.native.surf.gii              # native mesh, MSMAll position
  SREG=$FS/$h.sphere.reg.surf.gii                                # native mesh, fsaverage position
  SDEF=$T/fs_LR-deformed_to-fsaverage.$H.sphere.32k_fs_LR.surf.gii  # 32k mesh, fsaverage position (2016)
  AMID32_MSM=$D/$sub.$H.midthickness_MSMAll.32k_fs_LR.surf.gii
  AMIDNAT_HCP=$D/$sub.$H.midthickness.native.surf.gii
  AMIDNAT_FS=$FS/$h.midthickness.surf.gii
  AMID32_FS=$FS/$sub.$h.midthickness.32k_fs_LR.surf.gii

  # Step 2: targets 32k -> native through MSMAll
  $WB -metric-resample $G/targets.$h.32k.func.gii $S32 $SNAT_MSM ADAP_BARY_AREA \
      $G/targets.$h.native.func.gii -area-surfs $AMID32_MSM $AMIDNAT_HCP

  # Step 3: native -> 32k through sphere.reg (the curvature route)
  $WB -metric-resample $G/targets.$h.native.func.gii $SREG $SDEF ADAP_BARY_AREA \
      $G/targets.$h.32k_spherereg.func.gii -area-surfs $AMIDNAT_FS $AMID32_FS

  # Checkpoint 2.1: control round trip, native -> 32k back through MSMAll
  $WB -metric-resample $G/targets.$h.native.func.gii $SNAT_MSM $S32 ADAP_BARY_AREA \
      $G/targets.$h.32k_msmallRT.func.gii -area-surfs $AMIDNAT_HCP $AMID32_MSM

  # Checkpoint 2.2/2.3: step-3 output -> native through sphere.reg, and back to 32k
  $WB -metric-resample $G/targets.$h.32k_spherereg.func.gii $SDEF $SREG ADAP_BARY_AREA \
      $G/targets.$h.native_spherereg.func.gii -area-surfs $AMID32_FS $AMIDNAT_FS
  $WB -metric-resample $G/targets.$h.native_spherereg.func.gii $SREG $SDEF ADAP_BARY_AREA \
      $G/targets.$h.32k_sphereregRT.func.gii -area-surfs $AMIDNAT_FS $AMID32_FS

  # Checkpoint 1.2: recompute the training curvature through step-3 route
  $WB -metric-resample $FS/$h.graymid.H.gii $SREG $SDEF ADAP_BARY_AREA \
      $G/curv_recomputed.$h.32k.func.gii -area-surfs $AMIDNAT_FS $AMID32_FS

  # Checkpoint 3.2: native midthickness coordinates to 32k via both routes (BARYCENTRIC)
  $WB -surface-coordinates-to-metric $AMIDNAT_HCP $G/xyz.$h.native.func.gii
  $WB -metric-resample $G/xyz.$h.native.func.gii $SNAT_MSM $S32 BARYCENTRIC \
      $G/xyz.$h.32k_msmall.func.gii
  $WB -metric-resample $G/xyz.$h.native.func.gii $SREG $SDEF BARYCENTRIC \
      $G/xyz.$h.32k_spherereg.func.gii

  # Step 5 (preferred myelin route): native myelin -> 32k through sphere.reg
  STRUCT=CORTEX_LEFT; [ $H == R ] && STRUCT=CORTEX_RIGHT
  $WB -cifti-separate $D/$sub.MyelinMap_BC.native.dscalar.nii COLUMN \
      -metric $STRUCT $G/myelin_native.$h.func.gii -roi $G/myelin_roi_native.$h.func.gii
  $WB -metric-resample $G/myelin_native.$h.func.gii $SREG $SDEF ADAP_BARY_AREA \
      $G/myelin.$h.32k_spherereg.func.gii -area-surfs $AMIDNAT_FS $AMID32_FS
  $WB -metric-resample $G/myelin_roi_native.$h.func.gii $SREG $SDEF ADAP_BARY_AREA \
      $G/myelin_roi.$h.32k_spherereg.func.gii -area-surfs $AMIDNAT_FS $AMID32_FS

  if [ "$pilot" == "pilot" ]; then
    # Alternative myelin route: 32k MSMAll map through steps 2-3
    $WB -metric-resample $G/myelin_mat.$h.32k.func.gii $S32 $SNAT_MSM ADAP_BARY_AREA \
        $G/myelin_mat.$h.native.func.gii -area-surfs $AMID32_MSM $AMIDNAT_HCP
    $WB -metric-resample $G/myelin_mat.$h.native.func.gii $SREG $SDEF ADAP_BARY_AREA \
        $G/myelin_mat.$h.32k_spherereg.func.gii -area-surfs $AMIDNAT_FS $AMID32_FS
  fi
done
echo "resampled $sub"
