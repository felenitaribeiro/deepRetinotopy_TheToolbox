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

Requirements:
- HCP "fs_LR-deformed_to-fsaverage" surfaces (available at: https://github.com/Washington-University/HCPpipelines/tree/master/global/templates/standard_mesh_atlases/resample_fsaverage)
- Docker / Singularity container

## Software containers

### Docker
To pull, run, and execute a Docker container, run the following:

```bash
docker pull vnmd/deepretinotopy_1.0.1:latest
docker run -it -v ~:/tmp/ --name deepret2 -u $(id -u):$(id -g) vnmd/deepretinotopy_1.0.1:latest
docker exec -it deepret bash
```

In the container, you can run **deepRetinotopy.sh**: 
```bash
cd $path/deepRetinotopy_TheToolbox
bash deepRetinotopy.sh -s $path_freesurfer_dir -t $path_hcp_template_surfaces -d $dataset_name
```
### Singularity


## Pre-trained models

#TODO

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

Docker and Singularity containers were generated and are available through the [Neurodesk](https://www.neurodesk.org/). 

## Contact
Fernanda Ribeiro <[fernanda.ribeiro@uq.edu.au](fernanda.ribeiro@uq.edu.au)>
