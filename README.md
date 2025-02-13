# DeepRetinotopy -- The toolbox
This repository contains code for the general use of deepRetinotopy with a command line interface.

## Table of Contents
* [Requirements](#installation-and-requirements)
* [Software containers](#software-containers)
* [Contributors](#contributors)
* [Citation](#citation)
* [Acknowledgements](#acknowledgements)
* [Contact](#contact)

## Requirements 

- Docker / Singularity container
- freesurfer directory
- HCP "fs_LR-deformed_to-fsaverage" surfaces (available at: https://github.com/Washington-University/HCPpipelines/tree/master/global/templates/standard_mesh_atlases/resample_fsaverage)

## Software containers
DeepRetinotopy, pre-trained models, and required software are packaged in software containers available through Dockerhub and Neurodesk.

### Docker
If you want to run deepRetinotopy locally, you can install Docker and pull our container from Dockerhub using the following command:

```bash
docker pull vnmd/deepretinotopy_1.0.8:latest
docker run -it -v ~:/tmp/ --name deepret -u $(id -u):$(id -g) vnmd/deepretinotopy_1.0.8:latest
# docker exec -it deepret bash
```

If you would like Python scripts to print output to the terminal in real-time, you can set the appropriate environment variable when running the container (e.g., 'docker run -e PYTHONUNBUFFERED=1 -it -v ~:/tmp/ --name deepret -u $(id -u):$(id -g) vnmd/deepretinotopy_1.0.8:latest').


Once in the container (the working directory is deepRetinotopy_TheToolbox), you can run **deepRetinotopy**: 
```bash
deepRetinotopy -s $path_freesurfer_dir -t $path_hcp_template_surfaces -d $dataset_name -m $maps
```

The following arguments are required:
- **-s** path to the freesurfer directory
- **-t** path to the HCP "fs_LR-deformed_to-fsaverage" surfaces
- **-d** dataset name (e.g. "HCP")
- **-m** maps to be generated (e.g. "polarAngle,eccentricity,pRFsize")

### Singularity
Alternatevely, you can run your analysis on [Neurodesktop](https://www.neurodesk.org/docs/getting-started/neurodesktop/) or using [Neurocommand](https://www.neurodesk.org/docs/getting-started/neurocommand/linux-and-hpc/) through the following commands:

```bash
ml deepretinotopy/1.0.8
deepRetinotopy -s $path_freesurfer_dir -t $path_hcp_template_surfaces -d $dataset_name -m $maps
```

You can also download the Singularity container using the following command (for Asian/Australian locations) to run it locally or on your HPC:

```bash
date_tag=20250207
export container=deepretinotopy_1.0.8_$date_tag
curl -X GET https://objectstorage.ap-sydney-1.oraclecloud.com/n/sd63xuke79z3/b/neurodesk/o/${container}.simg -O
```

Then, you can execute the container (so long Singularity is already available on your computing environment) using the following command:

```bash
singularity exec ./deepretinotopy_1.0.8_$date_tag.simg deepRetinotopy -s $path_freesurfer_dir -t $path_hcp_template_surfaces -d $dataset_name -m $maps
```

For different locations see the [Neurodesk documentation](https://www.neurodesk.org/docs/getting-started/neurocontainers/singularity/).

## Usage

The main functionality of this toolbox is to generate retinotopic maps (polar angle, eccentricity, and pRF size) from freesurfer-based data (specifically, data in the 'surf' directory).
However, you can also generate visual field sign maps after running 'deepRetinotopy' to help with manual delineation of visual areas, using the following command:

```bash
signMaps -s $path_freesurfer_dir -t $path_hcp_template_surfaces -d $dataset_name 
```

## Output

The output of deepRetinotopy is a folder named "deepRetinotopy", in each freesurfer subject directory, containing the following files:

```bash
└── freesurfer
				└── [sub_id]
					└── deepRetinotopy
						├── [sub_id].fs_predicted_eccentricity_lh_curvatureFeat_model.func.gii
						├── [sub_id].fs_predicted_eccentricity_rh_curvatureFeat_model.func.gii
						├── [sub_id].fs_predicted_fieldSignMap_lh_model.func.gii
						├── [sub_id].fs_predicted_fieldSignMap_rh_model.func.gii
						├── [sub_id].fs_predicted_pRFsize_lh_curvatureFeat_model.func.gii
						├── [sub_id].fs_predicted_pRFsize_rh_curvatureFeat_model.func.gii
						├── [sub_id].fs_predicted_polarAngle_lh_curvatureFeat_model.func.gii
						├── [sub_id].fs_predicted_polarAngle_rh_curvatureFeat_model.func.gii
						├── [sub_id].predicted_eccentricity_model.lh.native.func.gii
						├── [sub_id].predicted_eccentricity_model.rh.native.func.gii
						├── [sub_id].predicted_fieldSignMap_model.lh.native.func.gii
						├── [sub_id].predicted_fieldSignMap_model.rh.native.func.gii
						├── [sub_id].predicted_pRFsize_model.lh.native.func.gii
						├── [sub_id].predicted_pRFsize_model.rh.native.func.gii
						├── [sub_id].predicted_polarAngle_model.lh.native.func.gii
						└── [sub_id].predicted_polarAngle_model.rh.native.func.gii
```

Files with 'fs_predicted' in their name are GIFTI files containing the predicted maps in the 32k fsaverage space, and files with 'native' in their name are GIFTI files containing the predicted maps in the native space of the subject.

## Contributors
If you want to contribute to this repository, please follow the instructions below:

1. Fork the repository
2. Create a new branch (e.g. `git checkout -b my-new-branch`)
3. Commit your changes (e.g. `git commit -am 'Add some feature'`)
4. Push the branch (e.g. `git push origin my-new-branch`)
5. Create a new Pull Request

## Citation

Please cite our work if you used our model:

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

## Acknowledgements

Docker and Singularity containers were generated and are available through [Neurodesk](https://www.neurodesk.org/). 

## Contact
Fernanda Ribeiro <[fernanda.ribeiro@uq.edu.au](fernanda.ribeiro@uq.edu.au)>
