# spherereg_targets — re-expression of the HCP training targets

Pipeline that re-expresses the HCP 7T retinotopy training targets (polar angle,
eccentricity, pRF size, R2; fits 1–3) and the myelin input from the HCP **MSMAll** frame
into the FreeSurfer **`sphere.reg`** frame of the training curvature, for all 181
participants: 32k → native through MSMAll, then native → 32k through `sphere.reg` with the
exact command and 2016 `fs_LR-deformed_to-fsaverage` template that produced the training
curvature (verified byte-exact, see the run report).

Run of record: 2026-10-09, report with all checkpoint results, versions and checksums in
`sandbox/spherereg_targets/report.md`.

## Running

```
./run_pipeline.sh            # all stages in order
./run_pipeline.sh <stage>    # one stage: download checkpoint0 extract resample
                             #            analyze mats checkpoint4 loader plots export repro
```

Working data lives in `sandbox/spherereg_targets/` (hcp/ downloads, gii/ intermediates,
mat/ outputs, checks/ metrics+plots). Paths are hardcoded to this filesystem for exact
provenance — to relocate, change the constants at the top of `lib.py`,
`1_download_hcp.sh`, `2_extract_giftis.py`, `3_resample_subject.sh`,
`3_resample_all.sbatch`, `run_pipeline.sh`.

## Layout

Numbered scripts are the pipeline, in execution order (like `main/` in the toolbox);
`checks/` holds the checkpoint/validation scripts; `tests/` the code tests for the
reader; `lib.py` and `wb` are shared helpers.

| stage | script | what it does |
|---|---|---|
| download | `1_download_hcp.sh` | subject list from the `.mat` fields; HCP S1200 surfaces + native myelin from `s3://hcp-openaccess`; canonical template spheres |
| checkpoint0 | `checks/checkpoint0_inputs.py` | file census, native vertex-count identity, curvature provenance (all 362 files), `cifti_curv_all.mat` ≠ training curvature |
| extract | `2_extract_giftis.py` | `.mat` → per-subject GIFTI columns: cos/sin polar angle (never the angle itself), ecc, pRF, R2, validity; invalid vertices zero-filled |
| resample | `3_resample_all.sbatch` → `3_resample_subject.sh` | all wb_command steps: steps 2–3, both round trips, native consistency, xyz geometry, both myelin routes (Slurm, ~15 min) |
| analyze | `checks/checkpoint2_3_analyze.py`, `checks/checkpoint2_3_consistency.py` | checkpoints 1.2, 2.1–2.3, 3.1–3.3 → `checks/full_metrics.csv` |
| mats | `4_write_mats.py` | the 11 `cifti_*_all_spherereg.mat` files (same structure as the originals; myelin = mat route) |
| checkpoint4 | `checks/checkpoint4.py` | coverage, distributions, ranges, myelin pattern, split halves → `checks/checkpoint4.csv` |
| loader | `checks/checkpoint4_loader.py` | `read_HCP` loads the new files with identical shapes (symlink layout in `loader_test/`) |
| plots | `checks/checkpoint4_visual.py` | side-by-side polar angle maps, 3 subjects (needs env `deepretinotopy_validation_plot`) |
| export | `5_export_empirical_giftis.py` | per-subject GIFTIs into `HCP/freesurfer/<sub>/surf/`: `<sub>.empirical_<map>_<fit>-spherereg.<h>.32k_fs_LR.func.gii`, `…_<fit>.<h>.native.func.gii`, `<sub>.myelinmap-spherereg.<h>.32k_fs_LR.func.gii` |
| repro | (inline in `run_pipeline.sh`) | checkpoint 5: participant 100610 end-to-end is byte-identical |
| tests | `tests/reader_equiv_test.py`, `tests/dataset_smoke_test.py` | reader bit-exactness + full `HCP_spherereg` dataset build |

## Training on the new data

`utils/read_data.py` has `read_HCP_gifti` (same outputs and semantics as `read_HCP`,
including the legacy LH polar-angle ±180° shift) reading the exported per-subject
GIFTIs, and `utils/dataset.py` accepts `dataset='HCP_spherereg'` (same 161/10/10 split;
cache stem includes the dataset name, so caches never mix with `HCP`). Train with
`--dataset HCP_spherereg`; everything else unchanged. Tests (`./run_pipeline.sh tests`):
- `tests/reader_equiv_test.py` — `read_HCP_gifti` is bit-exact vs `read_HCP` on the
  `_spherereg.mat` files (3 subjects × 2 hemispheres × 4 predictions × myelin on/off).
- `tests/dataset_smoke_test.py` — full `Retinotopy(dataset='HCP_spherereg')` build, split sizes.

Alternatively, `read_HCP` works unmodified on the `_spherereg.mat` files through a
symlink layout like `sandbox/spherereg_targets/loader_test/HCP_new/`.

## Key implementation notes

- Polar angle is resampled as cos/sin and reconstructed with atan2 (0/360 wrap).
- Scalars are zero-filled where invalid and divided by the resampled validity column;
  NaN where validity < 0.99.
- Myelin ships from the **mat route** (32k MSMAll → native → 32k `sphere.reg`): the native
  `MyelinMap_BC` carries vessel outliers (max ≈ 19) that HCP's own 32k maps exclude
  (max ≈ 3.6). Native-route maps are kept in `gii/` for comparison (agreement r ≈ 0.986).
- `scipy.io.savemat` needs `long_field_names=True` (eccentricity field names are 32 chars).
- `wb` wraps wb_command 1.5.0 inside `deepretinotopy_1.0.18_20250909.simg`.
- Original `.mat` files are never modified; new files end in `_spherereg.mat`.
