.. image:: _static/logo_v1.png
   :align: center
   :width: 400px

.. centered:: A deep learning-based toolkit for retinotopic mapping

``DeepRetinotopy`` is a toolkit that leverages a geometric deep learning model to predict retinotopic maps from brain shape. It integrates:

1. Standard neuroimaging software (FreeSurfer 7.3.2 and Connectome Workbench 1.5.0) for anatomical MRI data preprocessing.
2. A deep-learning model for predicting retinotopic maps at the individual level.
3. An efficient implementation of the visual field sign analysis for aiding early visual areas parcellation.

These components are packaged into Docker and Singularity software containers, which can be easily downloaded and are available on `NeuroDesk <https://www.neurodesk.org/>`_.

This documentation showcases the respective functionality and provides details concerning its application and modules. If you still have questions after going through the provided documentation, you can ask a question on `GitHub <https://github.com/felenitaribeiro/deepRetinotopy/issues>`_.

Contents
========
.. toctree::
   :maxdepth: 1

   installation
   usage
   walkthrough
   release-history
