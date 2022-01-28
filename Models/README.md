# Models

This folder contains all source code necessary to train new models and generate predictions on the test dataset 
using our pre-trained models available at [Open Science Framework](https://osf.io/f4dez/). 

## Training new models - with intact features
Scripts for training new models are: 
- ./deepRetinotopy_updated.py;

## Generalization
Scripts for loading our pre-trained models and generating predictions on the test dataset are:

- ./Generalizability/generalize_deepRetinotopy.py;
- ./Generalizability/generalize_deepRetinotopy_cte.py;
- ./Generalizability/generalize_deepRetinotopy_cte_curv.py;
- ./Generalizability/generalize_deepRetinotopy_cte_myelin.py;
- ./Generalizability/generalize_deepRetinotopy_semiSupervised.py;

Don't forget to download tpre-trained models on OSF, and to place them in ./output).

## Explainability
Scripts for running our perturbation-based approach are:
- ./explainability/explainability_deepRetinotopy.py;
- ./explainability/explainability_deepRetinotopy_curvature.py;
- ./explainability/explainability_deepRetinotopy_myelin.py;
- ./explainability/explainability_deepRetinotopy_reverse.py;



## Validity 
Scripts for training new models for validity experiments are: 
- ./deepRetinotopy_validity_cte.py;
- ./deepRetinotopy_validity_cte_curv.py;
- ./deepRetinotopy_validity_cte_myelin.py;
- ./deepRetinotopy_validity_semiSupervised.py;


## Citation

Please cite our paper if you used our model or if it was somewhat helpful for you :wink:

    @article{Ribeiro2020,
        title = {{Predicting brain function from anatomy using geometric deep learning}},
        author = {Ribeiro, Fernanda L and Bollmann, Steffen and Puckett, Alexander M},
        doi = {10.1101/2020.02.11.934471},
        journal = {bioRxiv},
        url = {http://biorxiv.org/content/early/2020/02/12/2020.02.11.934471.abstract},
        year = {2020}
    }

