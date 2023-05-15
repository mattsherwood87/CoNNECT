FMRIB's Linear Image Registration Tool (FLIRT)
==============================================

FLIRT parameters can be found in “<project_identifier>_<input-datatype>_bet_input.json” (see :numref:`BET_input_data_types` for a list of 
available input data types). This file contains the inputs described in the nipype python extension manual for `FSL BET 
<https://nipype.readthedocs.io/en/0.12.1/interfaces/generated/nipype.interfaces.fsl.preprocess.html#flirt>`__. The available parameters are provided in :numref:`flirt_json_table`.




.. _flirt_json_table:

.. list-table:: Available Keys in the bet control JSON file.
   :widths: 30 15 15 40
   :header-rows: 1

   * - **Key Name**
     - **Required?**
     - **Data Type**
     - **Description**
   * - ``__general_comment__``
     - OPTIONAL
     - string
     - free text to provide a brief description
   * - flirt_params
     - REQUIRED
     - dictionary
     - brain extraction parameters as described in :numref:`fsl_flirt_inputs`.


FLIRT-Specific parameters
-------------------------

.. _fsl_bet_inputs:

.. list-table:: Available Keys in the bet control JSON file. Input and output files doe not need specified here.
   :widths: 30 15 15 40
   :header-rows: 1

   * - **Key Name**
     - **Required?**
     - **Data Type**
     - **Description**
   * - args
     - OPTIONAL
     - string
     - Additional parameters to the command
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
     - Bias field and neck cleanup
   * - remove_eyes
     - OPTIONAL
     - boolean
     - eye & optic nerve cleanup (can be useful in SIENA)
   * - robust
     - OPTIONAL
     - boolean
     - Robust brain centre estimation (iterates BET several times)
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




Optional Parameters
-------------------

**standard_reference_image** 

.. _std_reference_input:

.. list-table:: T2 input dictionary keys.
   :widths: 30 15 15 40
   :header-rows: 1

   * - **Key Name**
     - **Required?**
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