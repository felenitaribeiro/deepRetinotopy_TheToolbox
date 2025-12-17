============
Requirements
============

To use ``deepRetinotopy``, ensure the following dependencies are available:

- Docker / Singularity container / Neurodesk
- FreeSurfer directory
- HCP "fs_LR-deformed_to-fsaverage" surfaces (available at: https://github.com/Washington-University/HCPpipelines/tree/master/global/templates/standard_mesh_atlases/resample_fsaverage)

============
Installation
============

In general, there are two distinct ways to install and use ``deepRetinotopy``:
either through virtualization/container technology, that is `Docker`_ or
`Singularity`_, or via Neurodesk.
Once you are ready to run ``deepRetinotopy``, see `Usage <https://felenitaribeiro.github.io/deepRetinotopy/usage>`_ for details.

Docker
======

If you prefer running ``deepRetinotopy`` locally via Docker, you can pull our container from Dockerhub and run it using the following commands:

.. code-block:: bash

    docker pull vnmd/deepretinotopy_1.0.18
    docker run -it -v ~:/tmp/ --name deepret -u $(id -u):$(id -g) vnmd/deepretinotopy_1.0.18

If you would like Python scripts to print output to the terminal in real-time, you can set the appropriate environment variable when running the container:

.. code-block:: bash

    docker run -e PYTHONUNBUFFERED=1 -it -v ~:/tmp/ --name deepret -u $(id -u):$(id -g) vnmd/deepretinotopy_1.0.18

Once in the container (the working directory is ``deepRetinotopy_TheToolbox``), you can run ``deepRetinotopy``:

.. code-block:: bash

    deepRetinotopy -s $path_freesurfer_dir -t $path_hcp_template_surfaces -d $dataset_name -m $maps

Singularity
===========

Alternatively, you can also download the Singularity/Apptainer container using the following command to run it locally or on your HPC:

.. code-block:: bash

    date_tag=20250902
    export container=deepretinotopy_1.0.18_$date_tag
    curl -X GET https://neurocontainers.neurodesk.org/${container}.simg -O

Then, you can execute the container (so long as Singularity/Apptainer is already available on your computing environment) using the following command:

.. code-block:: bash

    apptainer exec ./deepretinotopy_1.0.18_$date_tag.simg deepRetinotopy -s $path_freesurfer_dir -t $path_hcp_template_surfaces -d $dataset_name -m $maps

GPU inference
=============

You can use the same container for CPU-based inference pipeline as well as GPU-based inference.

To run our tool using a GPU, you need to pass the ``--nv`` flag:

.. code-block:: bash

    apptainer exec --nv ./deepretinotopy_1.0.18_$date_tag.simg deepRetinotopy -s $path_freesurfer_dir -t $path_hcp_template_surfaces -d $dataset_name -m $maps

Neurodesk
========

You can run ``deepRetinotopy`` on `Neurodesktop <https://neurodesk.org>`_ or using `Neurocommand <https://www.neurodesk.org/docs/getting-started/neurocommand/linux-and-hpc/>`_ through the following commands:

.. code-block:: bash

    ml deepretinotopy/1.0.18
    deepRetinotopy -s $path_freesurfer_dir -t $path_hcp_template_surfaces -d $dataset_name -m $maps

This method allows you to leverage the pre-configured environment provided by Neurodesk, ensuring compatibility and ease of use.

