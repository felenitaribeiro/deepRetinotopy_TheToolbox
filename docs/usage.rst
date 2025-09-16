.. _usage:

======
Usage
======

The general usage of `deepRetinotopy` is ADD DESCRIPTION HERE.
The exact command to run `deepRetinotopy` depends on the Installation method and user. 
`deepRetinotopy` can be used as a ``command line tool``.
Please refer to the `Tutorial <https://felenitaribeiro.github.io/deepRetinotopy/walkthrough>`_ for a more detailed walkthrough.

Here's a very conceptual example of running `deepRetinotopy` via ``CLI``:

.. code-block:: bash 

        deepRetinotopy 
        -s /path/to/freesurfer 
        -t /path/to/hcp/surfaces 
        -d hcp -m "polarAngle,eccentricity,pRFsize"

More detailed information regarding the ``command-line arguments`` and process control can be found below.


Command-Line Arguments
======================


.. code-block:: bash

    deepRetinotopy [-h]
                   [-s FREESURFER DIRECTORY]
                   [-t HCP SURFACE DIRECTORY]
                   [-d DATASET NAME]
                   [-m MAPS TO BE GENERATED]
                   [-g FAST GENERATION OF MIDTHICKNESS SURFACE {yes,no}]
                   [-j NUMBER OF CORES FOR PARALLELIZATION]
                   [-i SUBJECT ID FOR SINGLE SUBJECT PROCESSING]
                   [-o OUTPUT DIRECTORY FOR GENERATED FILES]
                   [--step1 GENERATE MIDTHICKNESS SURFACES AND CURVATURE MAPS]
                   [--step2 RETINOTOPIC MAP PREDICTION]
                   [--step3 RESAMPLE PREDICTIONS TO NATIVE SPACE]
                   [-v]
                   
**Basic arguments:**  

The following arguments are **required** to run `deepRetinotopy`:


-s
    path to the FreeSurfer directory
-t
    path to the folder containing the HCP "fs_LR-deformed_to-fsaverage" surfaces
-d
    dataset name (e.g. "hcp")
-m
    maps to be generated (e.g. "polarAngle,eccentricity,pRFsize")

**Processing step control** 

The following arguments can be used to control which processing steps are executed.

--step1
    Generate midthickness surfaces and curvature maps
--step2
    Retinotopic map prediction (Requires Step 1 outputs)
--step3
    Resample predictions to native space (Requires Steps 1+2 outputs)  

**Advanced Options**

The following arguments are optional and can be used to further customize the processing.

-g
    Fast generation of midthickness surface
-j
    Number of cores for parallelization
-i
    Subject ID for single subject processing
-o
    Output directory for generated files


Example Call(s)
---------------

Below you'll find two examples calls that hopefully help
you to familiarize yourself with `deepRetinotopy` and its options.

Example 1
~~~~~~~~~

.. code-block:: bash

    deepRetinotopy \
    input
    optional_arguments

Here's what's in this call:

- The 1st positional argument is 
- The 2nd positional argument indicates that 


Example 2
~~~~~~~~~

.. code-block:: bash

    deepRetinotopy \
    input
    optional_arguments
    optional_arguments

Here's what's in this call:

- The 1st positional argument is 
- The 2nd positional argument indicates that 
- The 3rd positional argument indicates that 


Support and communication
=========================

The documentation of this project is found here: https://felenitaribeiro.github.io/deepRetinotopy.

All bugs, concerns and enhancement requests for this software can be submitted here:
https://github.com/felenitaribeiro/deepRetinotopy/issues.

If you have a problem or would like to ask a question about how to use `deepRetinotopy`,
please submit a question to `NeuroStars.org <http://neurostars.org/tags/deepRetinotopy>`_ with an `deepRetinotopy` tag.
NeuroStars.org is a platform similar to StackOverflow but dedicated to neuroinformatics.

All previous `deepRetinotopy` questions are available here:
http://neurostars.org/tags/deepRetinotopy/

Not running on a local machine? - Data transfer
===============================================

Please contact you local system administrator regarding
possible and favourable transfer options (e.g., `rsync <https://rsync.samba.org/>`_
or `FileZilla <https://filezilla-project.org/>`_).

A very comprehensive approach would be `Datalad
<http://www.datalad.org/>`_, which will handle data transfers with the
appropriate settings and commands.
Datalad also performs version control over your data.