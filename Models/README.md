# Models

This folder contains all source code necessary to train new models and generate predictions on the test dataset 
using our pre-trained models available at [Open Science Framework](https://osf.io/f4dez/). 

## Training new models - with intact features
Scripts for training new models are: 
- ./deepRetinotopy_updated.py;


## Validity 
Scripts for training new models for validity experiments are: 
- ./deepRetinotopy_validity_cte.py;
- ./deepRetinotopy_validity_cte_curv.py;
- ./deepRetinotopy_validity_cte_myelin.py;
- ./deepRetinotopy_validity_semiSupervised.py;

## Generalization
Scripts for loading our pre-trained models and generating predictions on the test dataset are:

- ./Generalizability/generalize_deepRetinotopy.py;
- ./Generalizability/generalize_deepRetinotopy_cte.py;
- ./Generalizability/generalize_deepRetinotopy_cte_curv.py;
- ./Generalizability/generalize_deepRetinotopy_cte_myelin.py;
- ./Generalizability/generalize_deepRetinotopy_semiSupervised.py;

Don't forget to download the pre-trained models on OSF, and to place them in ./output).

## Explainability
Scripts for running our perturbation-based approach are:
- ./explainability/explainability_deepRetinotopy.py;
- ./explainability/explainability_deepRetinotopy_curvature.py;
- ./explainability/explainability_deepRetinotopy_myelin.py;
- ./explainability/explainability_deepRetinotopy_reverse.py;


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
