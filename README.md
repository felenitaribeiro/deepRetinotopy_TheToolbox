# DeepRetinotopy - A deep learning-based toolkit for retinotopic mapping
![Logo](/figures/logo_v1.png)

DeepRetinotopy is a toolkit that leverages a geometric deep learning model to predict retinotopic maps from brain shape. Our toolkit integrates (1) standard neuroimaging software (FreeSurfer 7.3.2 and Connectome Workbench 1.5.0) for anatomical MRI data preprocessing, (2) a [deep-learning model for predicting retinotopic maps](https://www.sciencedirect.com/science/article/pii/S1053811921008971) at the individual level, and (3) an efficient implementation of the visual field sign analysis for aiding early visual areas parcellation. These components are packaged into Docker and Singularity software containers, which can be easily downloaded and are available on [NeuroDesk](https://www.neurodesk.org/).

## Table of Contents
* [Requirements](#installation-and-requirements)
* [Software containers](#software-containers)
* [Usage](#usage)
  * [Basic Usage](#basic-usage)
  * [Advanced Options](#advanced-options)
  * [Single Subject Processing](#single-subject-processing)
  * [Custom Output Directory](#custom-output-directory)
  * [Field Sign Maps](#field-sign-maps)
* [Output](#output)
* [Contributors](#contributors)
* [Citation](#citation)
* [Acknowledgements](#acknowledgements)
* [Contact](#contact)

## Requirements 

- Docker / Singularity container / Neurodesk
- freesurfer directory
- HCP "fs_LR-deformed_to-fsaverage" surfaces (available at: https://github.com/Washington-University/HCPpipelines/tree/master/global/templates/standard_mesh_atlases/resample_fsaverage)

## Software containers
DeepRetinotopy (pre-trained models) and required software are packaged in software containers available through Neurodesk and Dockerhub.

### Neurodesk
You can run deepRetinotopy on [Neurodesktop](https://www.neurodesk.org/docs/getting-started/neurodesktop/) or using [Neurocommand](https://www.neurodesk.org/docs/getting-started/neurocommand/linux-and-hpc/) through the following commands:

```bash
ml deepretinotopy/1.0.18
deepRetinotopy -s $path_freesurfer_dir -t $path_hcp_template_surfaces -d $dataset_name -m $maps
```

### Docker
If you prefer running deepRetinotopy locally via Docker, you can pull our container from Dockerhub and run it using the following commands:

```bash
docker pull vnmd/deepretinotopy_1.0.18
docker run -it -v ~:/tmp/ --name deepret -u $(id -u):$(id -g) vnmd/deepretinotopy_1.0.18
# docker exec -it deepret bash
```

If you would like Python scripts to print output to the terminal in real-time, you can set the appropriate environment variable when running the container (e.g., 'docker run -e PYTHONUNBUFFERED=1 -it -v ~:/tmp/ --name deepret -u $(id -u):$(id -g) vnmd/deepretinotopy_1.0.18').

Once in the container (the working directory is deepRetinotopy_TheToolbox), you can run **deepRetinotopy**: 
```bash
deepRetinotopy -s $path_freesurfer_dir -t $path_hcp_template_surfaces -d $dataset_name -m $maps
```

### Singularity
Alternatively, you can also download the Singularity/Apptainer container using the following command to run it locally or on your HPC:

```bash
date_tag=20250902
export container=deepretinotopy_1.0.18_$date_tag
curl -X GET https://neurocontainers.neurodesk.org/${container}.simg -O
```

Then, you can execute the container (so long as Singularity/Apptainer is already available on your computing environment) using the following command:

```bash
apptainer exec ./deepretinotopy_1.0.18_$date_tag.simg deepRetinotopy -s $path_freesurfer_dir -t $path_hcp_template_surfaces -d $dataset_name -m $maps
```


### Containers for GPU inference
Our "deepretinotopy_1.0.18" containers are meant for GPU inference with CUDA 12.4, compatible with H100, A100, and L40. You may see warnings like 'An issue occurred while importing pyg-lib' due to GLIBC version differences between PyTorch Geometric and FreeSurfer base image, but these can be safely ignored as they don't affect inference behaviour. You can also use the same container for a broader CPU-based inference pipeline. 

To run our tool using a GPU, you need to pass the --nv flag.

```bash
apptainer exec --nv  ./deepretinotopy_1.0.18_$date_tag.simg deepRetinotopy -s $path_freesurfer_dir -t $path_hcp_template_surfaces -d $dataset_name -m $maps
```

## Usage

### Required FreeSurfer Data

For optimal storage efficiency when working with large datasets, the toolbox only requires a minimal subset of FreeSurfer outputs. You can significantly reduce storage requirements by downloading only the following files per subject:

```
# Essential Files
<subject_id>/surf/
├── lh.white          # White matter surface
├── lh.pial           # Pial surface  
├── lh.sphere.reg     # Spherical surface for resampling
├── rh.white          # White matter surface
├── rh.pial           # Pial surface
└── rh.sphere.reg     # Spherical surface for resampling
```

**_Note_**: The toolbox automatically generates the midthickness surfaces and curvature data from these base files during processing. All other FreeSurfer outputs (thickness maps, parcellations, etc.) are not required for retinotopic mapping prediction.

### Basic Usage

The main functionality of this toolbox is to generate retinotopic maps (polar angle, eccentricity, and pRF size) from FreeSurfer-based data (specifically, data in the 'surf' directory).

**Required arguments:**
- **-s** path to the FreeSurfer directory
- **-t** path to the folder containing the HCP "fs_LR-deformed_to-fsaverage" surfaces
- **-d** dataset name (e.g. "hcp")
- **-m** maps to be generated (e.g. "polarAngle,eccentricity,pRFsize")

```bash
deepRetinotopy -s /path/to/freesurfer -t /path/to/hcp/surfaces -d hcp -m "polarAngle,eccentricity,pRFsize"
```

### Processing Step Control

By default, DeepRetinotopy runs the complete pipeline (Steps 1-3). For greater flexibility and efficiency, you can run individual steps using the following flags:

#### Available Step Flags

| Flag | Description | Requirements |
|------|-------------|--------------|
| `--step1` | Generate midthickness surfaces and curvature maps | None |
| `--step2` | Retinotopic map prediction | Requires Step 1 outputs |
| `--step3` | Resample predictions to native space | Requires Steps 1+2 outputs |

**_Examples:_**
```bash
# Generate input data only
deepRetinotopy -s /path/to/freesurfer -t /path/to/hcp/surfaces -d hcp -m "polarAngle,eccentricity,pRFsize" --step1
```

### Advanced Options

**Optional arguments:**
- **-g** fast generation of midthickness surface (`yes` or `no`, default: `yes`)
- **-j** number of cores for parallelization (default: auto-detected or 1 for single subject processing)
- **-i** subject ID for single subject processing
- **-o** output directory for generated files

### Single Subject Processing

Process a specific subject instead of all subjects in the directory:

```bash
## Process single subject
deepRetinotopy -s /path/to/freesurfer -t /path/to/hcp/surfaces -d hcp -m "polarAngle,eccentricity" -i sub-001
```

### Custom Output Directory

Store generated files in a separate directory (useful for DataLad and version control workflows):

```bash
# All outputs to custom directory
deepRetinotopy -s /path/to/freesurfer -t /path/to/hcp/surfaces -d hcp -m "polarAngle,eccentricity" -o /path/to/output

# Single subject with custom output
deepRetinotopy -s /path/to/freesurfer -t /path/to/hcp/surfaces -d hcp -m "polarAngle" -i sub-001 -o /path/to/output
```

When using a custom output directory, files will be organized as:
```
output_directory/
├── sub-001/
│   ├── surf/
│   │   └── ... (surface processing files)
│   └── deepRetinotopy/
│       └── ... (prediction files)
└── sub-002/
    └── ...
```

### Error Handling and Logging

Pipeline execution logs are automatically saved with timestamps for easy identification:
- **Output log**: `deepRetinotopy_YYYYMMDD_HHMMSS_output.log`
- **Error log**: `deepRetinotopy_YYYYMMDD_HHMMSS_error.log`

**Log Location Priority:**
1. Output directory (if specified with `-o` flag)
2. FreeSurfer subjects directory (fallback)

**Automatic Subject Exclusion:**
If subjects are missing required curvature files from Step 1, they will be automatically excluded from processing and logged in `removed_subjects_*.txt` files. These exclusion logs are saved in the output directory (if previously provided) or the FreeSurfer directory.

### Field Sign Maps

Generate visual field sign maps after running `deepRetinotopy` to help with manual delineation of visual areas:

```bash
# Process all subjects
signMaps --path /path/to/freesurfer --hemisphere lh --map fs_predicted

# Process single subject
signMaps --path /path/to/freesurfer --hemisphere lh --map fs_predicted --subject_id sub-001

# Process from custom output directory
signMaps --path /path/to/output --hemisphere lh --map fs_predicted --subject_id sub-001
```

**signMaps arguments:**
- **--path** path to the directory containing deepRetinotopy results (FreeSurfer or custom output directory)
- **--hemisphere** hemisphere to process (`lh` or `rh`)
- **--map** map type to use (default: `fs_predicted`)
- **--subject_id** subject ID for single subject processing (optional)

## Output

### Default Output (In-place)
When no custom output directory is specified, files are saved within the FreeSurfer directory structure:

```bash
└── freesurfer
	└── [sub_id]
		├── surf
		│   ├── [sub_id].curvature-midthickness.lh.32k_fs_LR.func.gii
		│   ├── [sub_id].curvature-midthickness.rh.32k_fs_LR.func.gii
		│   └── ... (other surface processing files)
		└── deepRetinotopy
			├── [sub_id].fs_predicted_eccentricity_lh_curvatureFeat_model.func.gii
			├── [sub_id].fs_predicted_eccentricity_rh_curvatureFeat_model.func.gii
			├── [sub_id].fs_predicted_pRFsize_lh_curvatureFeat_model.func.gii
			├── [sub_id].fs_predicted_pRFsize_rh_curvatureFeat_model.func.gii
			├── [sub_id].fs_predicted_polarAngle_lh_curvatureFeat_model.func.gii
			├── [sub_id].fs_predicted_polarAngle_rh_curvatureFeat_model.func.gii
			├── [sub_id].predicted_eccentricity_model.lh.native.func.gii
			├── [sub_id].predicted_eccentricity_model.rh.native.func.gii
			├── [sub_id].predicted_pRFsize_model.lh.native.func.gii
			├── [sub_id].predicted_pRFsize_model.rh.native.func.gii
			├── [sub_id].predicted_polarAngle_model.lh.native.func.gii
			└── [sub_id].predicted_polarAngle_model.rh.native.func.gii
```

### Custom Output Directory
When using `-o /path/to/output`, the same file structure is replicated in the specified output directory, keeping the original FreeSurfer data unchanged.

**File descriptions:**
- Files with `fs_predicted` in their name are GIFTI files containing the predicted maps in the 32k fsaverage space
- Files with `native` are GIFTI files containing the predicted maps in the native space of the subject
- Files with `fieldSignMap` are generated by the `signMaps` command (only generated if signMaps command has been run)

## Contributors
If you want to contribute to this repository, please follow the instructions below:

1. Fork the repository
2. Create a new branch (e.g. `git checkout -b my-new-branch`)
3. Add your changes (e.g.,`git add new_script.py`)
4. Commit your changes (e.g. `git commit -m 'Add some feature'`)
5. Push the branch (e.g. `git push origin my-new-branch`)
6. Create a new Pull Request

## Citation

Please cite our earlier work if you find it helpful:

	@article{Ribeiro2021,
		author = {Ribeiro, Fernanda L and Bollmann, Steffen and Puckett, Alexander M},
		doi = {https://doi.org/10.1016/j.neuroimage.2021.118624},
		issn = {1053-8119},
		journal = {NeuroImage},
		keywords = {cortical surface, high-resolution fMRI, machine learning, manifold, visual hierarchy,Vision},
		pages = {118624},
		title = {{Predicting the retinotopic organization of human visual cortex from anatomy using geometric deep learning}},
		url = {https://www.sciencedirect.com/science/article/pii/S1053811921008971},
		year = {2021}
	}

	@article{Renton2024,
            author = {Renton, Angela I and Dao, Thuy T and Johnstone, Tom and Civier, Oren and Sullivan, Ryan P and White, David J and Lyons, Paris and Slade, Benjamin M and Abbott, David F and Amos, Toluwani J and Bollmann, Saskia and Botting, Andy and Campbell, Megan E J and Chang, Jeryn and Close, Thomas G and D{\"{o}}rig, Monika and Eckstein, Korbinian and Egan, Gary F and Evas, Stefanie and Flandin, Guillaume and Garner, Kelly G and Garrido, Marta I and Ghosh, Satrajit S and Grignard, Martin and Halchenko, Yaroslav O and Hannan, Anthony J and Heinsfeld, Anibal S and Huber, Laurentius and Hughes, Matthew E and Kaczmarzyk, Jakub R and Kasper, Lars and Kuhlmann, Levin and Lou, Kexin and Mantilla-Ramos, Yorguin-Jose and Mattingley, Jason B and Meier, Michael L and Morris, Jo and Narayanan, Akshaiy and Pestilli, Franco and Puce, Aina and Ribeiro, Fernanda L and Rogasch, Nigel C and Rorden, Chris and Schira, Mark M and Shaw, Thomas B and Sowman, Paul F and Spitz, Gershon and Stewart, Ashley W and Ye, Xincheng and Zhu, Judy D and Narayanan, Aswin and Bollmann, Steffen},
            doi = {10.1038/s41592-023-02145-x},
            issn = {1548-7105},
            journal = {Nature Methods},
            number = {5},
            pages = {804--808},
            title = {{Neurodesk: an accessible, flexible and portable data analysis environment for reproducible neuroimaging}},
            url = {https://doi.org/10.1038/s41592-023-02145-x},
            volume = {21},
            year = {2024}
    }

## Acknowledgements

Docker and Singularity containers were generated and are available through [Neurodesk](https://www.neurodesk.org/). 

## Contact
Fernanda Ribeiro <[fernanda.ribeiro@uq.edu.au](fernanda.ribeiro@uq.edu.au)>