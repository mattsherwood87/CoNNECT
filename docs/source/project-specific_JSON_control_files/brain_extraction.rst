Brain Extraction (BET)
**********************

Brain extraction parameters FSL BET or ANTs Brain Extraction can be found in “<project_identifier>_<input-datatype>_bet_input.json” (see :numref:`BET_input_data_types` for a list of 
available input data types). This file contains the inputs described in the nipype python extension manual for `FSL BET 
<https://nipype.readthedocs.io/en/0.12.0/interfaces/generated/nipype.interfaces.fsl.preprocess.html#bet>`__ or `ANTs Brain Extraction 
<https://nipype.readthedocs.io/en/latest/api/generated/nipype.interfaces.ants.segmentation.html#brainextraction>`__. The available parameters are provided in :numref:`bet_json_table`.



.. _BET_input_data_tyes:

.. list-table:: Data types.
   :widths: 25 75
   :header-rows: 1

   * - **Data Type**
     - **Source Image Description**
   * - struc
     - T1-weighted image
   * - asl
     - arterial spin labeling or cerebral blood flow image
   * - apt
     - amide proton transfer-weighted source or MTRasym image
   * - flair
     - T2 FLAIR image
   * - T2
     - T2 or T2* image


.. _bet_json_table:

.. list-table:: Available Keys in the bet control JSON file.
   :widths: 20 20 20 40
   :header-rows: 1

   * - **Key Name**
     - **Required Level**
     - **Data Type**
     - **Description**
   * - ``__general_comment__``
     - OPTIONAL
     - string
     - free text to provide a brief description
   * - bet_params
     - REQUIRED
     - dictionary
     - brain extraction parameters as described in :numref:`fsl_bet_inputs` and :numref:`ants_bet_inputs`


BET-Specific parameters
=======================

.. _fsl_bet_inputs:

.. list-table:: Available Keys in the bet control JSON file. Input and output files doe not need specified here.
   :widths: 20 20 20 40
   :header-rows: 1

   * - **Key Name**
     - **Required Level**
     - **Data Type**
     - **Description**
   * - args
     - OPTIONAL
     - string
     - Additional parameters to the command. Maps to a command-line argument as %s
   * - center
     - OPTIONAL
     - string
     - Full path to an anatomical template
   * - environ
     - OPTIONAL
     - dictionary
     - Environment variables
   * - frac
     - OPTIONAL
     - float
     - Fractional intensity threshold.
   * - functional
     - OPTIONAL
     - boolean
     - **NOT SUPPORTED**
   * - ignore_exception
     - OPTIONAL
     - boolean
     - **UPDATE**
   * - mask
     - OPTIONAL
     - boolean
     - **UPDATE**
   * - mesh
     - OPTIONAL
     - boolean
     - **UPDATE**
   * - no_output
     - OPTIONAL
     - boolean
     - **UPDATE**
   * - outline
     - OPTIONAL
     - boolean
     - **UPDATE**
   * - output_type
     - OPTIONAL
     - string
     - **UPDATE**
   * - padding
     - OPTIONAL
     - boolean
     - **UPDATE**
   * - radius
     - OPTIONAL
     - integer
     - Head radius. Maps to command-line argument -r %d.
   * - reduce_bias
     - OPTIONAL
     - boolean
     - Bias field and neck cleanup. Maps to command-line argument -B. Mutually exclusive  functional, reduce_bias, robust, padding, remove_eyes, surfaces, t2_guided
   * - remove_eyes
     - OPTIONAL
     - boolean
     - eye & optic nerve cleanup (can be useful in SIENA). Maps to command-line argument -S. Mutually exclusive  functional, reduce_bias, robust, padding, remove_eyes, surfaces, t2_guided
   * - robust
     - OPTIONAL
     - boolean
     - Robust brain centre estimation (iterates BET several times). Maps to command-line argument -R. Mutually exclusive: functional, reduce_bias, robust, padding, remove_eyes, surfaces, t2_guided
   * - skull
     - OPTIONAL
     - boolean
     - Creates a skull image. Maps to command-line argument -s.
   * - surfaces
     - OPTIONAL
     - boolean
     - run bet2 and then betsurf to get additional skull and scalp surfaces (includes registrations). Maps to command-line arguments -A. Mutually_exclusive: functional, reduce_bias, robust, padding, remove_eyes, surfaces, t2_guided
   * - t2_guided
     - OPTIONAL
     - boolean
     - Requires a dictionary titled T2 as described in :numref:`t2_input` as with creating surfaces, when also feeding in non-brain-extracted T2 (includes registrations). Maps to command-line arguments -A2 %s. Mutually exclusive functional, reduce_bias, robust, padding, remove_eyes, surfaces, t2_guided
   * - terminal_output
     - OPTIONAL
     - string
     - Control terminal output: **stream** - displays to terminal immediately (default), **allatonce** - waits till command is finished to display output, **file** - writes output to file, **none** - output is ignored
   * - threshold
     - OPTIONAL
     - boolean
     - apply thresholding to segmented brain image and mask. Maps to a command-line arguemtn -t
   * - vertical gradient
     - OPTIONAL
     - float
     - Vertical gradient in fractional intensity threshold (-1, 1). Maps to a command-line argument -g %.2f


.. _ants_bet_inputs:

.. list-table:: Available Keys in the bet control JSON file.
   :widths: 20 20 20 40
   :header-rows: 1

   * - **Key Name**
     - **Required Level**
     - **Data Type**
     - **Description**
   * - brain_probability_template
     - REQUIRED
     - string
     - full path to an existing brain probability mask
   * - brain_template
     - REQUIRED
     - string
     - full path to an anatomical template
   * - args
     - OPTIONAL
     - string
     - additional parameters to the command. Maps to a command-line argument as %s
   * - debug
     - OPTIONAL
     - boolean
     - if True, runs a faster version of the script. Only for testing. Implies -u 0. Requires single thread computation for complete reproducibility. Mapts to a command-line argument -z 1
   * - dimension
     - OPTIONAL
     - integer
     - image dimension (2 or 3). Maps to command-line argument -d %d
   * - environ
     - OPTIONAL
     - dictionary
     - Environment variables
   * - extraction_registration_mask
     - OPTIONAL
     - string
     - full path to a mask (in template space) used during registration for brain extraction. To limit the metric computation to a specific region. Maps to a command-line argument -f %s
   * - image_suffix
     - OPTIONAL
     - string
     - Any of standard ITK formats, nii.gz is default. Maps to a command-line argument -s %s
   * - keep_temporary_files
     - OPTIONAL
     - integer
     - Keep brain extraction/segmentation warps, etc (default = 0). Maps to a command-line argument -k %d


Optional Parameters
===================

**T2** 

.. _t2_input:

.. list-table:: T2 input dictionary keys.
   :widths: 20 20 20 40
   :header-rows: 1

   * - **Key Name**
     - **Required Level**
     - **Data Type**
     - **Description**
   * - input_bids_location
     - REQUIRED
     - string
     - Location of original, non-brain extracted T2 or T2 FLAIR image: 'rawdata' or 'derivatives'
   * - input_bids_parameters
     - REQUIRED
     - dictionary
     - A bids filename dictionary as explained in **NEEDS REFERENCE**