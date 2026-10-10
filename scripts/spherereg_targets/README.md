# spherereg_targets — re-expression of the HCP training targets

Re-expresses the HCP 7T retinotopy training targets (polar angle, eccentricity, pRF size,
R2; fits 1–3) and the myelin input from the HCP **MSMAll** frame into the FreeSurfer
**`sphere.reg`** frame of the training curvature, for all 181 participants: 32k → native
through MSMAll, then native → 32k through `sphere.reg` with the exact command and 2016
`fs_LR-deformed_to-fsaverage` template that produced the training curvature. This puts the
model inputs and targets in one frame (they were ~5 mm apart in early visual cortex).

`report.md` is the run of record: software versions, template checksums, and all
checkpoint results.

## Layout

Numbered scripts are the pipeline in execution order (as in `main/`); `checks/` holds the
checkpoint/validation scripts, `tests/` the reader tests, `lib.py`/`wb` shared helpers.

1. `1_download_hcp.sh` — subject list; HCP S1200 surfaces + native myelin from
   `s3://hcp-openaccess`; template spheres.
2. `2_extract_giftis.py` — `.mat` → per-subject GIFTI columns (cos/sin polar angle,
   eccentricity, pRF size, R2, validity; invalid vertices zero-filled).
3. `3_resample_subject.sh` (per subject; `3_resample_all.sbatch` batches it) — all
   `wb_command` resampling: the two pipeline steps, round trips, native consistency,
   geometry, both myelin routes.
4. `4_write_mats.py` — the `cifti_*_all_spherereg.mat` files (same structure as the
   originals; originals never modified).
5. `5_export_empirical_giftis.py` — per-subject GIFTIs into the FreeSurfer tree:
   `<sub>.empirical_<map>_<fit>-spherereg.<h>.32k_fs_LR.func.gii`, the same maps in
   native space, and `<sub>.myelinmap-spherereg.<h>.32k_fs_LR.func.gii`.

`run_pipeline.sh` drives everything (`./run_pipeline.sh [stage]`); checkpoints run
between the numbered steps — see the stage list in its header.

## Requirements and paths

Connectome Workbench ≥ 1.5 (the `wb` wrapper calls it inside the project container — edit
for your setup), Python 3 with numpy/scipy/nibabel, matplotlib for the plots check, and
AWS credentials that can read the HCP S3 bucket. The resample batch script is written for
Slurm but just loops `3_resample_subject.sh`. Data paths (toolbox root and the working
directory for downloads/intermediates/outputs) are set at the top of `lib.py`,
`1_download_hcp.sh`, `3_resample_subject.sh`, `3_resample_all.sbatch` and
`run_pipeline.sh` — change them together.

## Training on the new data

`utils/read_data.py::read_HCP_gifti` reads the exported GIFTIs with the same outputs and
semantics as `read_HCP` (including the legacy LH polar-angle ±180° shift), and
`utils/dataset.py` accepts `dataset='HCP_spherereg'` (same split; caches are namespaced by
dataset name). Train with `--dataset HCP_spherereg`. Verified by
`tests/reader_equiv_test.py` (bit-exact vs `read_HCP` on the `_spherereg.mat` files) and
`tests/dataset_smoke_test.py` (full dataset build).

## Key implementation notes

- Polar angle is resampled as cos/sin and reconstructed with atan2 (0/360 wrap).
- Scalars are zero-filled where invalid and divided by the resampled validity;
  NaN where validity < 0.99.
- Myelin ships from the 32k map through both steps (not the native map, which carries
  vessel outliers that HCP's own 32k maps exclude); route agreement r ≈ 0.986.
- `scipy.io.savemat` needs `long_field_names=True` (field names exceed 31 characters).
