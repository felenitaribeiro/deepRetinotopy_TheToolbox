======
Usage
======

``deepRetinotopy`` is a toolkit designed to generate retinotopic maps (polar angle, eccentricity, and pRF size) from FreeSurfer-based data. The exact command to run ``deepRetinotopy`` depends on the installation method and user preferences. Below, we provide detailed instructions and examples for using the toolkit.

Basic Usage
===========

The main functionality of this toolbox is to generate retinotopic maps from FreeSurfer-based data (specifically, data in the 'surf' directory).

**Required arguments:**

- **-s**: Path to the FreeSurfer directory
- **-t**: Path to the folder containing the HCP "fs_LR-deformed_to-fsaverage" surfaces
- **-d**: Dataset name (e.g., "hcp")
- **-m**: Maps to be generated (e.g., "polarAngle,eccentricity,pRFsize")

Example:

.. code-block:: bash

    deepRetinotopy -s /path/to/freesurfer -t /path/to/hcp/surfaces -d hcp -m "polarAngle,eccentricity,pRFsize"

Processing Step Control
=======================

By default, ``deepRetinotopy`` runs the complete pipeline (Steps 1-3). For greater flexibility and efficiency, you can run individual steps using the following flags:

.. list-table::
   :header-rows: 1

   * - Flag
     - Description
     - Requirements
   * - ``--step1``
     - Generate midthickness surfaces and curvature maps
     - None
   * - ``--step2``
     - Retinotopic map prediction
     - Requires Step 1 outputs
   * - ``--step3``
     - Resample predictions to native space
     - Requires Steps 1+2 outputs

Example:

.. code-block:: bash

    # Generate input data only
    deepRetinotopy -s /path/to/freesurfer -t /path/to/hcp/surfaces -d hcp -m "polarAngle,eccentricity,pRFsize" --step1

Advanced Options
=================

**Optional arguments:**

- **-g**: Fast generation of midthickness surface (`yes` or `no`, default: `yes`)
- **-j**: Number of cores for parallelization (default: auto-detected or 1 for single subject processing)
- **-i**: Subject ID for single subject processing
- **-o**: Output directory for generated files

Single Subject Processing
==========================

Process a specific subject instead of all subjects in the directory:

.. code-block:: bash

    deepRetinotopy -s /path/to/freesurfer -t /path/to/hcp/surfaces -d hcp -m "polarAngle,eccentricity" -i sub-001

Custom Output Directory
========================

Store generated files in a separate directory (useful for DataLad and version control workflows):

.. code-block:: bash

    # All outputs to custom directory
    deepRetinotopy -s /path/to/freesurfer -t /path/to/hcp/surfaces -d hcp -m "polarAngle,eccentricity" -o /path/to/output

    # Single subject with custom output
    deepRetinotopy -s /path/to/freesurfer -t /path/to/hcp/surfaces -d hcp -m "polarAngle" -i sub-001 -o /path/to/output

Field Sign Maps
===============

Generate visual field sign maps after running ``deepRetinotopy`` to help with manual delineation of visual areas:

.. code-block:: bash

    # Process all subjects
    signMaps --path /path/to/freesurfer --hemisphere lh --map fs_predicted

    # Process single subject
    signMaps --path /path/to/freesurfer --hemisphere lh --map fs_predicted --subject_id sub-001

    # Process from custom output directory
    signMaps --path /path/to/output --hemisphere lh --map fs_predicted --subject_id sub-001

**signMaps arguments:**

- **--path**: Path to the directory containing deepRetinotopy results (FreeSurfer or custom output directory)
- **--hemisphere**: Hemisphere to process (`lh` or `rh`)
- **--map**: Map type to use (default: `fs_predicted`)
- **--subject_id**: Subject ID for single subject processing (optional)

Support and Communication
==========================

All bugs, concerns, and enhancement requests for this software can be submitted here: https://github.com/felenitaribeiro/deepRetinotopy/issues.

If you have a problem or would like to ask a question about how to use ``deepRetinotopy``, please send an email to Fernanda (fernanda.ribeiro@uq.edu.au)