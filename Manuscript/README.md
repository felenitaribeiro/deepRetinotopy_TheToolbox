# Manuscript


This folder contains all source code necessary to reproduce all figures and summary statistics in our recent work entitled "An explainability framework 
for cortical surface-based deep learning" available on [arXiv](https://arxiv.org/abs/2203.08312).

## Figures

Figures were generated using the scripts in `./plots/left_hemi`.

## Descriptive statistics

Saliency maps were generated using the following scripts:
- ./stats/left_hemi/MeanDeltaTheta_vertices_PA_neighbor.py
- ./stats/left_hemi/MeanDeltaTheta_vertices_PA_neighbor_feat.py


## Citation

Please cite our papers if you used our model or if it was somewhat helpful for you :wink:

	@article{Ribeiro2022,
		author = {Ribeiro, Fernanda L and Bollmann, Steffen and Cunnington, Ross and Puckett, Alexander M},
		arxivId = {2203.08312},
		journal = {arXiv},
		keywords = {Geometric deep learning, high-resolution fMRI, vision, retinotopy, explainable AI},
		title = {{An explainability framework for cortical surface-based deep learning}},
		url = {https://arxiv.org/abs/2203.08312},
		year = {2022}
	}
	

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