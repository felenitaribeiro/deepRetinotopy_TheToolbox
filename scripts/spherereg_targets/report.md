# Re-expression of the HCP retinotopy training targets in the sphere.reg frame

Run of record: 2026-10-09/10 · pipeline in `scripts/spherereg_targets/` · repository-relative
paths; the working directory for downloads, intermediates and `.mat` outputs is
`sandbox/spherereg_targets/` (not under version control).

## Summary

The HCP 7T retinotopy targets (polar angle, eccentricity, pRF size, R2; fits 1–3) and the
myelin input were re-expressed from the MSMAll frame into the FreeSurfer `sphere.reg` frame
of the training curvature, for all 181 participants: 32k → native through MSMAll, then
native → 32k through `sphere.reg` with the exact command and the exact 2016 template that
produced the training curvature. Data integrity is verified (round trips lossless to ~1–2°,
native-space consistency ~1.6°, recomputed curvature byte-exact, reruns byte-identical).
The frame change itself is large and systematic: median 12.3–12.7° polar angle change and
~4.8 mm displacement in V1–V3.

**One checkpoint family fails as literally specified** (checkpoint 4.2, distribution
medians within a *fixed* V1–V3 ROI): eccentricity medians drop systematically (median −16%)
because the maps move ~5 mm along the eccentricity gradient while the ROI stays put. The
control round trip (MSMAll out and back, same ROI, same reconstruction) preserves those
medians to 0.1% — the shift is the frame change, not a processing artifact. See “Decision
on checkpoint 4.2”.

## Inputs and provenance checks

| item | result |
|---|---|
| Subjects | 181, derived from the `.mat` field names; all have complete FreeSurfer and HCP S1200 files (checkpoint 0: 0 missing) |
| Targets | `HCP/raw/converted/cifti_{polarAngle,eccentricity,pRFsize}_all.mat` (+ `_fit2_`, `_fit3_`), `cifti_R2_all.mat`, `cifti_myelin_all.mat` |
| fit2/fit3 + curv sources | restored from the project’s research-data archive; the archive’s fit1 files are md5-identical to the local ones (`8c9b8164…`) |
| HCP S1200 per subject | `s3://hcp-openaccess/HCP_1200/<sub>/MNINonLinear/{Native,fsaverage_LR32k}/` — MSMAll native sphere, native + 32k-MSMAll midthickness, native & 32k myelin (3.1 GB total) |
| Native mesh identity | HCP `sphere.MSMAll.native` = FreeSurfer `sphere.reg` = `midthickness` vertex counts for all 181 × 2 hemispheres |
| Hemisphere order | V1–V3 polar angles in the expected hemifield: median fraction 0.986 (LH) / 0.975 (RH); minima 0.57/0.70 are low-R2 subjects |

### Template spheres (SHA-256)

| file | sha256 |
|---|---|
| `fs_LR-deformed_to-fsaverage.L.sphere.32k_fs_LR.surf.gii` (2016, repo `templates/`) | `d29e8e7d7dd88a4cfd227796fb13f6f869f1b5b94d00d7da2dc445a4df3162c7` |
| `fs_LR-deformed_to-fsaverage.R.sphere.32k_fs_LR.surf.gii` (2016) | `3647269965e07c8373722b24554836501c7ec3b5b16e0481aa20aaa7062819d2` |
| `S1200(_7T_Retinotopy181).L.sphere.32k_fs_LR.surf.gii` | `1846b053f870405466776d004d714cc1da0cec7361761c65a864782dd09f30a8` |
| `S1200.R.sphere.32k_fs_LR.surf.gii` | `1a898433a9f1070e4e0435d4db966776ecc3291bfcd444efc7910aeffb91561c` |

The repo 2016 templates are md5-identical (`f902cf11…`/`9b236e70…`) to the archived copies.
The fs_LR 32k sphere is byte-identical across subjects, and the OSF
`S1200_7T_Retinotopy181.L` sphere (osf.io/95w4y, `data/raw/`) is byte-identical to it.

### Software

- Connectome Workbench **1.5.0** (commit `76441605d20`, 2021-02-16), run inside the
  deepretinotopy 1.0.18 container via the `wb` wrapper
- Python 3.12.8: numpy 2.0.1, scipy 1.15.1, nibabel 5.3.2
- AWS CLI 2.27.32 (HCP S3 download)

## Pipeline (per participant and hemisphere)

Scripts: `2_extract_giftis.py` → `3_resample_subject.sh` → `4_write_mats.py` (step 4 in
`lib.reconstruct`). Exact wb_command calls are in `3_resample_subject.sh`; the step-3 call
is verbatim the toolbox step-1 curvature command.

1. Targets packed as GIFTI columns: cos/sin of polar angle (never the angle itself),
   eccentricity, pRF size, R2 (fit1), validity (= finite PA & finite ecc), one set per fit;
   invalid vertices zero-filled.
2. 32k → native, `ADAP_BARY_AREA`, spheres S1200-32k → `sphere.MSMAll.native`, areas
   `midthickness_MSMAll.32k` → `midthickness.native` (HCP).
3. native → 32k, `ADAP_BARY_AREA`, spheres `sphere.reg` → 2016 deformed template, areas
   FS `midthickness` → `<sub>.<h>.midthickness.32k_fs_LR` (the curvature route).
4. Reconstruction: PA = atan2(sin,cos) mod 360; ecc/pRF/R2 divided by the resampled
   validity; everything NaN where validity < 0.99; negative float noise clamped to 0.
5. Myelin: **final = “mat route”** (32k MSMAll map through steps 2–3 like a scalar), see
   “Myelin route decision”. The native route (native `MyelinMap_BC` directly through step 3)
   was also computed for all 181; route agreement r = 0.986/0.987 (median LH/RH; min 0.92).

## Checkpoint results

Reported as median [min, max] over 181 subjects × 2 hemispheres in V1–V3 (fixed 32k ROI),
original R2 > 15%, unless noted. Full per-subject tables in the working directory:
`checks/full_metrics.csv`, `checks/checkpoint4.csv`.

### Checkpoint 1 — the curvature route is exactly reproduced: PASS
- Provenance census over all 362 training-curvature GIFTIs: every file records exactly the
  step-3 command (graymid.H → sphere.reg → 2016 template, ADAP_BARY_AREA, the right area
  surfaces). 0 non-conforming.
- Recomputing the curvature with the pipeline’s own command/template: correlation 1.000 and
  max |diff| 0 on **all 362** hemispheres (float-exact).
- 1b: `cifti_myelin_all.mat` ≡ `MyelinMap_BC_MSMAll.32k` dscalar (r = 1.0, diff 0; 5 subjects).
  `cifti_curv_all.mat` vs training curvature: r = −0.29…−0.38 (5 subjects) — confirmed *not*
  the training curvature (opposite sign convention); not used further.

### Checkpoint 2 — round trips: PASS (9/362 mild p90 tails)
| check | PA median | PA p90 | ecc median | criterion |
|---|---|---|---|---|
| control RT (MSMAll ↔) | 1.76/1.80° [0.93–2.41] | 5.3° [0.9–8.3] | 0.065/0.069° | med<2.5 ✓ all; p90<7 ✗ in 9/362 (max 8.3°); ecc<0.15 ✗ in 3/362 (worst: 169444, see notes) |
| sphere.reg RT | 1.08/1.12° | 3.4° [1.6–5.5] | 0.036/0.037° | all pass |
| native consistency (2.3) | 1.61/1.61° [0.79–2.36] | 5.3° | — | med<2.5 ✓ **all 362** |

The native-consistency check is the substantive one — the new targets are the same native
data in another frame — and it passes everywhere.

### Checkpoint 3 — size of the frame change (descriptive): plausible
- PA change: median 12.7° (LH) / 12.3° (RH) per subject [5.0–29.6], p90 ≈ 41–43° — matches
  the expected 12–14°; no subject near 0 (wrong file) or above 40° median (convention error).
- Geometric displacement (native midthickness via both routes): median 4.8 mm [2.7–10.2],
  p90 8.6/8.8 mm.
- Consistency across participants: per-vertex change fields correlate with the group mean
  field at r ≈ 0.25 (median; both PA change and displacement), sign agreement ≈ 0.53. The
  frame change has a modest systematic component (group-mean |PA change| ≈ 5°; systematic
  eccentricity shift below) and a **substantial participant-specific component** — which is
  the reason to re-express targets per participant rather than learn one fixed offset.

### Checkpoint 4 — validity of the new training data
- **4.1 coverage: PASS.** V1–V3 valid fraction 1.00 before and after; worst drop 1.1 pp (< 5).
- **4.2 distributions: FAILS as specified** for ecc/pRF medians; PA largely passes.
  - PA circular-mean shift: median 2.1°, >5° in 64/362 (max 14.4°).
  - ecc median change: >5% in 254/362 (median 9.1%, max 44%), **systematically downward**
    (−16% signed median); pRF: >5% in 194/362 (median 5.8%); R2: >5% in 39/362 (median 1.9%).
  - Diagnosis: the control round trip (same registration out and back, same masks, same
    reconstruction) changes these medians by ≤3.3% (median −0.1%) — the pipeline is clean.
    The shift appears only with the frame change: the maps move ~5 mm relative to the ROI,
    V1–V3 eccentricity roughly doubles over a few mm near the fovea, and the fixed ROI
    (drawn in the original frame) now samples a more foveal portion of the maps. A
    three-way comparison (orig-32k | native | new-32k medians) shows the native medians sit
    between the two projections. This is a property of the re-expression, not an error;
    with a ~12° median PA change (expected by checkpoint 3), a ≤5% ecc-median criterion in
    a fixed ROI is not attainable.
- **4.3 ranges: PASS.** PA ∈ [0,360], ecc/pRF ≥ 0, R2 ∈ [0,100] everywhere; no all-NaN
  participant. Myelin (mat route): within the original range for all 362 (max overshoot
  −0.005), V1–V3 median change ≤ 2.2%, V1 > V2/V3 pattern in 349/362 after vs 359/362
  before — the 10 flips are subjects whose V1-vs-V2/3 contrast was already ≈0.01–0.03.
- **4.4 split halves: PASS with note.** fit2-vs-fit3 median PA difference 3.93° before →
  3.41° after; |change| > 1° in 41/362, median change −0.59° — the halves agree slightly
  *more* after (resampling smoothing); no degradation anywhere.
- **4.5 loader: PASS.** `read_HCP` on the new files (3 subjects × 2 hemispheres ×
  {polarAngle, eccentricity, pRFsize, visualCoord} × myelination on/off): identical tensor
  shapes, mask counts within 1.6%.
- **4.6 visual: PASS.** `checks/plots/<sub>.<h>.pa.png` (3 pilot subjects): identical
  native maps, modest warp between the 32k frames.

### Checkpoint 5 — reproducibility: PASS
Re-running participant 100610 end-to-end (extraction + all resampling) reproduces all 38
per-subject files **byte-identically**. The `.mat` files are regenerated deterministically
in content; their 116-byte MAT header embeds a creation timestamp, so “byte-identical”
applies to the data payload, not the header.

## Myelin route decision

The spec preferred resampling the native myelin directly (one resampling). Implemented and
compared for all 181: route agreement r = 0.986/0.987 (median; min 0.92). However, HCP’s own
32k maps exclude high outliers the native map still carries (100610: native max 19.4 vs 32k
max 3.6; the native route reaches 11.9), which violates checkpoint 4.3’s range criterion and
would feed the model outliers the original training input never had. The **final myelin
therefore uses the mat route** (32k MSMAll → native → 32k sphere.reg), which is bounded by
convexity and matches the smoothness class of the original input. Native-route intermediates
are kept (`gii/<sub>/myelin.<h>.32k_spherereg.func.gii`).

## Outputs

- Working directory `mat/`: `cifti_{polarAngle,eccentricity,pRFsize}{,_fit2,_fit3}_all_spherereg.mat`,
  `cifti_R2_all_spherereg.mat`, `cifti_myelin_all_spherereg.mat` — same variable names,
  field names, metadata and subcortical entries as the originals (verified); originals untouched.
- Working directory `gii/<sub>/`: all intermediates (32k inputs, native, sphere.reg-32k,
  round trips, xyz geometry, myelin routes, recomputed curvature).
- Per-subject GIFTIs in `HCP/freesurfer/<sub>/surf/` (exported 2026-10-10 after CP4.2 was
  accepted, 42 files × 181 subjects):
  `<sub>.empirical_<map>_<fit>-spherereg.<h>.32k_fs_LR.func.gii` (sphere.reg frame),
  `<sub>.empirical_<map>_<fit>.<h>.native.func.gii` (native space),
  `<sub>.myelinmap-spherereg.<h>.32k_fs_LR.func.gii` (mat route).
- Reader: `utils/read_data.py::read_HCP_gifti` + `dataset='HCP_spherereg'` in
  `utils/dataset.py` (same split/semantics incl. the legacy LH polar-angle ±180° shift;
  bit-exact vs `read_HCP` on the `_spherereg.mat` files; full dataset build smoke-tested).

## Participant notes

- **169444 RH**: only 1 V1–V3 vertex with R2 > 15% in the original data (R2 max 17.7), 0
  after; distribution statistics are undefined for this hemisphere. Data present, simply
  near-zero signal. Worth considering for exclusion from RH training/evaluation.
- 9 subject-hemispheres exceed the control-RT p90 criterion mildly (7.8–8.3° vs 7°):
  239136 LH, 169343 RH, 910241 RH, 214019 LH, 155938 RH, + 4 more ≤7.8° (see CSV).

## Decision on checkpoint 4.2

Checkpoint 4.2’s pass criterion (ecc/pRF medians within 5% in the fixed V1–V3 ROI) is
violated by the frame change itself; the control round trip demonstrates the pipeline adds
≤0.3% of such shift. **Accepted 2026-10-10 (F. Ribeiro)** as an expected descriptive
consequence of the re-expression, not a failure. Final outputs were released (GIFTI export,
reader) on that basis.
