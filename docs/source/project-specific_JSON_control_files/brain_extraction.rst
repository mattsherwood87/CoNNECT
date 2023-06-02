
.. _bet_json:

Brain Extraction JSON Control File
======================

Brain extraction parameters (:numref:`bet_json_table`) for FSL BET or ANTs Brain Extraction can be found in “<project_identifier>_<input-datatype>_bet_input.json". 

.. seealso:: 
  This file contains the inputs described in the nipype python extension manual for `FSL BET <https://nipype.readthedocs.io/en/0.12.0/interfaces/generated/nipype.interfaces.fsl.preprocess.html#bet>`__ 
  or `ANTs Brain Extraction <https://nipype.readthedocs.io/en/latest/api/generated/nipype.interfaces.ants.segmentation.html#brainextraction>`__. 

**Sample Brain Extraction JSON control files**

* :download:`T1w <../_sample_docs/sample_struc_bet_input.json>` (or available `here <https://connect-tutorial.readthedocs.io/en/latest/_downloads/be7dfdc20af8e227afbdca86d697c380/sample_struc_bet_input.json>`__)
* :download:`ASL <../_sample_docs/sample_asl_bet_input.json>` (or available `here <https://connect-tutorial.readthedocs.io/en/latest/_downloads/84e3a18a8ba1dafbf4259a386c529265/sample_asl_bet_input.json>`__)
* :download:`3D APTw <../_sample_docs/sample_apt_bet_input.json>` (or available `here <https://connect-tutorial.readthedocs.io/en/latest/_downloads/21e00d656530cceabc6b9f2d6f030552/sample_apt_bet_input.json>`__)


.. _bet_json_table:

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
    * - type
      - REQUIRED
      - string
      - brain extraction program: FSL or ANTs
    * - bet_params
      - REQUIRED
      - dictionary
      - brain extraction parameters as described in :numref:`fsl_bet_inputs` and :numref:`ants_bet_inputs`


BET-Specific parameters
-----------------------

FSL BET
^^^^^^^

.. _fsl_bet_inputs:

.. list-table:: Available Keys in the bet control JSON file. Input and output files do not need specified here.
    :widths: 30 15 15 40
    :header-rows: 1

    * - **Key Name**
      - **Required Level**
      - **Data Type**
      - **Description**
    * - args
      - OPTIONAL
      - string
      - Additional parameters to the command
    * - center
      - OPTIONAL
      - list
      - 3 integer items specifying the center of gravity in voxels
    * - environ
      - OPTIONAL
      - dictionary
      - Environment variables
    * - frac
      - OPTIONAL
      - float
      - Fractional intensity threshold
    * - functional
      - OPTIONAL
      - boolean
      - **NOT SUPPORTED**
    * - ignore_exception
      - OPTIONAL
      - boolean
      - print an error instead of throwing an exception in case the interface fails to run
    * - mask
      - OPTIONAL
      - boolean
      - create binary mask image
    * - mesh
      - OPTIONAL
      - boolean
      - generate a vtk mesh brain surface
    * - no_output
      - OPTIONAL
      - boolean
      - don't generate segmented output
    * - outline
      - OPTIONAL
      - boolean
      - create surface outline image
    * - output_type
      - OPTIONAL
      - string
      - FSL output type ('NIFTI_PAIR', 'NIFTI_PARI_GZ', 'NIFTI_GZ', 'NIFTI')
    * - padding
      - OPTIONAL
      - boolean
      - improve BET if FOV is very small in Z
    * - radius
      - OPTIONAL
      - integer
      - Head radius
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
      - Creates a skull image
    * - surfaces
      - OPTIONAL
      - boolean
      - run bet2 and then betsurf to get additional skull and scalp surfaces (includes registrations)
    * - t2_guided
      - OPTIONAL
      - boolean
      - Requires a dictionary titled T2 as described in :numref:`t2_input` as with creating surfaces, when also feeding in non-brain-extracted T2 (includes registrations)
    * - terminal_output
      - OPTIONAL
      - string
      - Control terminal output (stream, allatonce, file, none)
    * - threshold
      - OPTIONAL
      - boolean
      - apply thresholding to segmented brain image and mask
    * - vertical gradient
      - OPTIONAL
      - float
      - Vertical gradient in fractional intensity threshold (-1, 1)


ANTs Brain Extraction
^^^^^^^^^^^^^^^^^^^^^

.. _ants_bet_inputs:

.. list-table:: Available Keys in the bet control JSON file.
    :widths: 30 15 15 40
    :header-rows: 1

    * - **Key Name**
      - **Required?**
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
      - additional parameters to the command
    * - debug
      - OPTIONAL
      - boolean
      - if True, runs a faster version of the script. Only for testing. Implies -u 0
    * - dimension
      - OPTIONAL
      - integer
      - image dimension (2 or 3)
    * - environ
      - OPTIONAL
      - dictionary
      - Environment variables
    * - extraction_registration_mask
      - OPTIONAL
      - string
      - full path to a mask (in template space) used during registration for brain extraction
    * - image_suffix
      - OPTIONAL
      - string
      - Any of standard ITK formats, nii.gz is default
    * - keep_temporary_files
      - OPTIONAL
      - integer
      - Keep brain extraction/segmentation warps, etc (default = 0)


Optional Parameters
-------------------

**T2/T2 FLAIR** 

.. note:: 
    T2 functionality has not been implemented or evaluated.

.. _t2_input:

.. list-table:: T2/T2 FLAIR input dictionary keys.
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

