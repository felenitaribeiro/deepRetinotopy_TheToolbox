# DeepRetinotopy - A deep learning-based toolkit for retinotopic mapping
![Logo](/figures/logo_v1.png)

DeepRetinotopy is a toolkit that leverages a geometric deep learning model to predict retinotopic maps from brain shape. Our toolkit integrates (1) standard neuroimaging software (FreeSurfer 7.3.2 and Connectome Workbench 1.5.0) for anatomical MRI data preprocessing, (2) a [deep-learning model for predicting retinotopic maps](https://www.sciencedirect.com/science/article/pii/S1053811921008971) at the individual level, and (3) an efficient implementation of the visual field sign analysis for aiding early visual areas parcellation. These components are packaged into Docker and Singularity software containers, which can be easily downloaded and are available on [NeuroDesk](https://www.neurodesk.org/).

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
DeepRetinotopy (pre-trained models) and required software are packaged in software containers available through Neurodesk and Dockerhub.

### Neurodesk
You can run deepRetinotopy on [Neurodesktop](https://www.neurodesk.org/docs/getting-started/neurodesktop/) or using [Neurocommand](https://www.neurodesk.org/docs/getting-started/neurocommand/linux-and-hpc/) through the following commands:

```bash
ml deepretinotopy/1.0.10
deepRetinotopy -s $path_freesurfer_dir -t $path_hcp_template_surfaces -d $dataset_name -m $maps
```

The following arguments are required:
- **-s** path to the freesurfer directory
- **-t** path to the folder containing the HCP "fs_LR-deformed_to-fsaverage" surfaces
- **-d** dataset name (e.g. "hcpP")
- **-m** maps to be generated (e.g. "polarAngle,eccentricity,pRFsize")

### Docker
If you prefer running deepRetinotopy locally via Docker, you can pull our container from Dockerhub and run it using the following commands:

```bash
docker pull vnmd/deepretinotopy_1.0.10:latest
docker run -it -v ~:/tmp/ --name deepret -u $(id -u):$(id -g) vnmd/deepretinotopy_1.0.10:latest
# docker exec -it deepret bash
```

If you would like Python scripts to print output to the terminal in real-time, you can set the appropriate environment variable when running the container (e.g., 'docker run -e PYTHONUNBUFFERED=1 -it -v ~:/tmp/ --name deepret -u $(id -u):$(id -g) vnmd/deepretinotopy_1.0.10:latest').


Once in the container (the working directory is deepRetinotopy_TheToolbox), you can run **deepRetinotopy**: 
```bash
deepRetinotopy -s $path_freesurfer_dir -t $path_hcp_template_surfaces -d $dataset_name -m $maps
```

### Singularity
Alternatively, you can also download the Singularity container using the following command (for Asian/Australian locations) to run it locally or on your HPC:

```bash
date_tag=20250409
export container=deepretinotopy_1.0.10_$date_tag
curl -X GET https://objectstorage.ap-sydney-1.oraclecloud.com/n/sd63xuke79z3/b/neurodesk/o/${container}.simg -O
```

Then, you can execute the container (so long as Singularity is already available on your computing environment) using the following command:

```bash
singularity exec ./deepretinotopy_1.0.10_$date_tag.simg deepRetinotopy -s $path_freesurfer_dir -t $path_hcp_template_surfaces -d $dataset_name -m $maps
```

For different locations, see the [Neurodesk documentation](https://www.neurodesk.org/docs/getting-started/neurocontainers/singularity/).

## Usage

The main functionality of this toolbox is to generate retinotopic maps (polar angle, eccentricity, and pRF size) from freesurfer-based data (specifically, data in the 'surf' directory). However, you can also generate visual field sign maps after running 'deepRetinotopy' to help with manual delineation of visual areas by using the following command:

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

Files with 'fs_predicted' in their name are GIFTI files containing the predicted maps in the 32k fsaverage space, and files with 'native' are GIFTI files containing the predicted maps in the native space of the subject.

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
