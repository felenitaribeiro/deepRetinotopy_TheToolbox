# DeepRetinotopy -- The toolbox
This repository contains (restructured) code for the general use of deepRetinotopy with a command line interface.

## Table of Contents
* [Requirements](#installation-and-requirements)
* [Software containers](#software-containers)
* [Pre-trained models](#pre-trained-models)
* [Citation](#citation)
* [Acknowledgements](#acknowledgements)
* [Contact](#contact)

## Requirements 

- HCP "fs_LR-deformed_to-fsaverage" surfaces (available at: https://github.com/Washington-University/HCPpipelines/tree/master/global/templates/standard_mesh_atlases/resample_fsaverage)
- Docker / Singularity container

## Software containers
Before running deepRetinotopy, you need to install Docker or Singularity and clone this repository.

```bash
git clone https://github.com/felenitaribeiro/deepRetinotopy_TheToolbox.git
```

### Docker
To pull, run, and execute a Docker container, run the following:

```bash
docker pull vnmd/deepretinotopy_1.0.1:latest
docker run -it -v ~:/tmp/ --name deepret -u $(id -u):$(id -g) vnmd/deepretinotopy_1.0.1:latest
# docker exec -it deepret bash
```

In the container, you can run **deepRetinotopy.sh**: 
```bash
cd $path_to_tool/deepRetinotopy_TheToolbox
bash deepRetinotopy.sh -s $path_freesurfer_dir -t $path_hcp_template_surfaces -d $dataset_name
```
### Singularity
First, you can download our Singularity container using the following command (for Asian/Australian locations):

```bash
cd $path_to_tool/deepRetinotopy_TheToolbox
export container=deepretinotopy_1.0.1_20230922
curl -X GET https://objectstorage.ap-sydney-1.oraclecloud.com/n/sd63xuke79z3/b/neurodesk/o/${container}.simg -O
```

Then, you can run the container (so long Singularity is already available on your computing environment) using the following command:

```bash
singularity exec --nv ./deepretinotopy_1.0.1_20230922.simg bash deepRetinotopy.sh -s $path_freesurfer_dir -t $path_hcp_template_surfaces -d $dataset_name
```

For different locations see the [Neurodesk documentation](https://www.neurodesk.org/docs/getting-started/neurocontainers/singularity/).

## Pre-trained models

Our pre-trained models are available on [OSF](https://osf.io/ermbz/).


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
