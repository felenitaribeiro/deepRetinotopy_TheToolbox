# deepRetinotopy_explain

This repository contains all source code necessary to replicate our recent work entitled "An explainability framework 
for cortical surface-based deep learning" available on [arXiv](). Note that, this repo is an updated version of 
[deepRetinotopy](https://github.com/Puckett-Lab/deepRetinotopy).

## Table of Contents
* [Installation and requirements](#installation-and-requirements)
* [Manuscript](#manuscript)
* [Models](#models)
* [Retinotopy](#retinotopy)
* [Citation](#citation)
* [Contact](#contact)


## Installation and requirements 

Models were generated using [Pytorch Geometric](https://pytorch-geometric.readthedocs.io/en/latest/). Since this package 
is under constant updates, we highly recommend that 
you follow the following steps to run our models locally:

- Create a conda environment (or docker container)
- Install torch first:

```bash
	conda install pytorch==1.6.0 torchvision cpuonly -c pytorch
```
	
- Install torch-scatter, torch-sparse, torch-cluster, torch-spline-conv and torch-geometric:
	 
```bash
    pip install --no-index torch-scatter -f https://pytorch-geometric.com/whl/torch-1.6.0+cu102.html
    pip install --no-index torch-sparse -f https://pytorch-geometric.com/whl/torch-1.6.0+cu102.html
    pip install --no-index torch-cluster -f https://pytorch-geometric.com/whl/torch-1.6.0+cu102.html
    pip install --no-index torch-spline-conv -f https://pytorch-geometric.com/whl/torch-1.6.0+cu102.html
    pip install torch-geometric
```

- Install the remaining required packages that are available at requirements.txt: 

```bash
    pip install -r requirements.txt
```

- Install the following git repository for plots:

```bash
    pip install git+https://github.com/felenitaribeiro/nilearn.git
```   


## Manuscript

This folder contains all source code necessary to reproduce all figures and summary statistics in our manuscript.

## Models

This folder contains all source code necessary to train a new model and to generate predictions on the test dataset 
using our pre-trained models. Note, models were updated for PyTorch 1.6.0. 

## Retinotopy

This folder contains all source code necessary to replicate datasets generation, in addition to functions and labels 
used for figures and models' evaluation. 

## Citation

Please cite our paper if you used our model or if it was somewhat helpful for you :wink:

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


## Contact
Fernanda Ribeiro <[fernanda.ribeiro@uq.edu.au](fernanda.ribeiro@uq.edu.au)>
