FMRIB's Linear Image Registration Tool (FLIRT)
==============================================

FLIRT parameters can be found in “<project_identifier>_<input-datatype>_bet_input.json” (see :numref:`BET_input_data_types` for a list of 
available input data types). This file contains the inputs described in the nipype python extension manual for `FSL BET 
<https://nipype.readthedocs.io/en/0.12.1/interfaces/generated/nipype.interfaces.fsl.preprocess.html#flirt>`__. The available parameters are 
provided in :numref:`flirt_json_table`.


**Sample FLIRT JSON control files**

* :download:`T1w <../_sample_docs/sample_T1w_flirt_input.json>`
* :download:`ASL <../_sample_docs/sample_asl_flirt_input.json>`
* :download:`3D APTw <../_sample_docs/sample_apt_flirt_input.json>`

.. _flirt_json_table:

.. list-table:: Available Keys in the FLIRT JSON control file.
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
   * - fslroi
     - OPTIONAL
     - boolean
     - perform fslroi to extract a single volume from input 4D image. Extracts the center volume unless the 'volume' key of the main_image_params
   * - bet
     - OPTIONAL
     - string
     - filename for :doc:`BET JSON control file <brain_extraction>`
   * - inclusion_list
     - OPTIONAL
     - list[string]
     - list of strings for option search inclusion criteria
   * - exclusion_list
     - OPTIONAL
     - list[string]
     - list of strings for option search exclusion criteria
   * - main_image_params
     - OPTIONAL
     - dictionary
     - parameters as described in :numref:`main_image_inputs`
   * - reference_image_params
     - OPTIONAL
     - dictionary
     - parameters as described in :numref:`ref_image_inputs`
   * - flirt_params
     - REQUIRED
     - dictionary
     - FLIRT parameters as described in :numref:`fsl_flirt_inputs`
   * - secondary_image_params
     - OPTIONAL
     - dictionary
     - parameters as described in :numref:`sec_image_inputs`
   * - standard_reference_params
     - OPTIONAL
     - dictionary
     - parameters as described in :numref:`std_ref_inputs`

FLIRT-Specific parameters
-------------------------

**main_image_params** 

These keys are used to identify the main input image for registration.

.. _main_image_inputs:

.. list-table:: Main image input dictionary keys. 
   :widths: 30 15 15 40
   :header-rows: 1

   * - **Key Name**
     - **Required?**
     - **Data Type**
     - **Description**
   * - input_bids_labels
     - REQUIRED
     - dictionary
     - A bids filename dictionary as explained in **NEEDS REFERENCE**
   * - output_bids_location
     - REQUIRED
     - string
     - bids derivatives sub-folder (derivatives -> sub-XXX -> ses-YYY - > output_bids_location)
   * - output_matrix_base
     - REQUIRED
     - string
     - base element for the output registration matrix (highres in highres2standard.mat)
   * - output_bids_labels
     - REQUIRED
     - dictionary
     - A bids filename dictionary as explained in **NEEDS REFERENCE**
   * - output_json_values
     - REQUIRED
     - dictionary
     - Key-value pairs to additionally insert into the JSON sidecar accompanying input-to-reference transformed image
   * - volume
     - OPTIONAL
     - integer
     - volume to extract using fslroi. Must specify 'fslroi' as true.
     
     
\n
**reference_image_params** 

These keys must be defined.

.. _ref_image_inputs:

.. list-table:: Standard reference image input dictionary keys.
   :widths: 30 15 15 40
   :header-rows: 1

   * - **Key Name**
     - **Required?**
     - **Data Type**
     - **Description**
   * - type
     - REQUIRED
     - string
     - Type of reference: std or bids
   * - input_bids_location
     - OPTIONAL
     - string
     - Input bids location: rawdata or derivatives (required if type bids)
   * - input_bids_labels
     - OPTIONAL
     - dictionary
     - A bids filename dictionary as explained in **NEEDS REFERENCE** (required if type bids)
   * - output_bids_labels
     - OPTIONAL
     - dictionary
     - Supplemental bids filename dictionary as explained in **NEEDS REFERENCE** (required if type bids)
   * - output_matrix_base
     - OPTIONAL
     - string
     - base element for the output registration matrix (highres in highres2standard.mat) (required if type bids)
   * - output_json_values
     - OPTIONAL
     - dictionary
     - Supplemental key-value pairs to additionally insert into the JSON sidecar accompanying input-to-reference transformed image (required if type bids)
   

     

.. _fsl_flirt_inputs:

.. list-table:: Available Keys for the flirt_params in the flirt control JSON file. Input and output files do not need specified here.
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
   * - angle_rep
     - OPTIONAL
     - string
     - representation of rotation angles: quaternion, euler
   * - apply_isoxfm
     - OPTIONAL
     - float
     - as applyxfm but forces isotropic resampling (NOT SUPPORTED)
   * - apply_xfm
     - OPTIONAL
     - boolean
     - apply transformation supplied by in_matrix_file (NOT SUPPORTED)
   * - bbrslope
     - OPTIONAL
     - float
     - value of bbrslope
   * - bbrtype
     - OPTIONAL
     - string
     - type of bbr cost function: signed [default], global_abs, local_abs
   * - bgvalue
     - OPTIONAL
     - float
     - use specified background value for points outside FOV
   * - bins
     - OPTIONAL
     - integer
     - number of histogram bins
   * - coarse_search
     - OPTIONAL
     - integer
     - coarse search delta angle
   * - cost
     - OPTIONAL
     - string
     - cost function: mutualinfo, corratio, normcorr, normmi, leastsq, labeldiff, bbr
   * - cost_func
     - OPTIONAL
     - string
     - cost function: mutualinfo, corratio, normcorr, normmi, leastsq, labeldiff, bbr
   * - datatype
     - OPTIONAL
     - string
     - force output data type: char, short, int, float, double
   * - display_init
     - OPTIONAL
     - boolean
     - display initial matrix
   * - dof
     - OPTIONAL
     - integer
     - number of transform degrees of freedom
   * - echospacing
     - OPTIONAL
     - float
     - value of EPI echo spacing - units of seconds
   * - environ
     - OPTIONAL
     - dictionary
     - environment variables
   * - fieldmap
     - OPTIONAL
     - file name 
     - reference image
   * - fieldmapmask
     - OPTIONAL
     - file name
     - mask for fieldmap image
   * - fine_search
     - OPTIONAL
     - integer
     - fine search delta angle
   * - force_scaling
     - OPTIONAL
     - boolean
     - force rescaling even for low-res images
   * - ignore_exception
     - OPTIONAL
     - boolean
     - print an error message instead of throwing an exception in case that interface fails to run
   * - in_matrix_file
     - OPTIONAL
     - file name
     - input 4x4 affine matrix
   * - in_weight  
     - OPTIONAL
     - existing file name
     - file for input weighting volume
   * - interp
     - OPTIONAL
     - string
     - final interpolation method used in reslicing: trilinear, nearestneighbor, sinc, spline
   * - min_sampling
     - OPTIONAL
     - float
     - set minimum voxel dimension for sampling
   * - no_clamp
     - OPTIONAL
     - boolean 
     - do not use intensity clamping
   * - no_resample
     - OPTIONAL
     - boolean
     - do not change input sampling
   * - no_resample_blur
     - OPTIONAL
     - boolean
     - do not use blurring on downsampling
   * - no_search
     - OPTIONAL
     - boolean
     - set all angular searches to ranges 0 to 0
   * - out_file
     - OPTIONAL
     - file name
     - registered output file
   * - out_log
     - OPTIONAL
     - file name
     - output log
   * -out_matrix_file
     - OPTIONAL
     - file name
     - output affine matrix in 4x4 asciii format
   * - output_type
     - OPTIONAL
     - string
     - FSL output type: NIFTI_PAIR, NIFTI_PAIR_GZ, NIFTI_GZ, NIFTI
   * - padding_size
     - OPTIONAL
     - integer
     - for applyxfm: interpolates outside image by size
   * - pedir  
     - OPTIONAL
     - integer
     - phase encode direction of EPI - 1/2/3=x/y/z & -1/-2/-3=x/-y/-z
   * - ref_weight
     - OPTIONAL
     - existing file name
     - file for reference weighting volume
   * - rigid2D
     - OPTIONAL
     - boolean
     - use 2D rigid body mode - ignores dof
   * - save_log
     - OPTIONAL
     - boolean 
     - save to log file
   * - Schedule
     - OPTIONAL
     - existing file name
     - replaces default schedule
   * - searchr_x
     - OPTIONAL
     - integer
     - search angles along x-axis, in degrees
   * - searchr_y
     - OPTIONAL
     - integer
     - search angles along y-axis, in degrees
   * - searchr_z
     - OPTIONAL
     - integer
     - search angles along z-axis, in degrees
   * - sinc_width
     - OPTIONAL
     - integer
     - full-width in voxels
   * - sinc_window
     - OPTIONAL
     - string
     - sinc window: rectangular, hanning, blackman
   * - terminal_output
     - OPTIONAL
     - string
     - control terminal output: stream, allatonce, file, none
   * - uses_qform
     - OPTIONAL
     - boolean
     - initialize using sform or qform
   * - verbose
     - OPTIONAL
     - integer
     - verbose mode, 0 is least
   * - wm_seg
     - OPTIONAL
     - file name
     - white matter segmentation volume needed by BBR cost function
   * - wmcoords
     - OPTIONAL
     - file name
     - white matter boundary coordinates for BBR cost function
   * - wmnorms
     - OPTIONAL
     - file name
     - white matter boundary normals for BBR cost function
   * - out_file
     - OUTPUTS
     - exisitng file name
     - path/name of registered file
   * - out_log
     - OUTPUTS
     - file name
     - path/name of output log
   * - out_matrix_file
     - OUTPUT
     - existing file name
     - path/name of calculated affine transform


Optional Parameters
-------------------

**secondary_image_params** 

These keys should be defined if the user would like to apply the registered output to a secondary image.

.. _sec_image_inputs:

.. list-table:: Secondary image input dictionary keys. 
   :widths: 30 15 15 40
   :header-rows: 1

   * - **Key Name**
     - **Required?**
     - **Data Type**
     - **Description**
   * - input_bids_labels
     - REQUIRED
     - dictionary
     - A bids filename dictionary as explained in **NEEDS REFERENCE**
   * - output_matrix_base
     - REQUIRED
     - string
     - base element for the output registration matrix
   * - output_bids_labels
     - REQUIRED
     - dictionary
     - Supplemental bids filename dictionary as explained in **NEEDS REFERENCE**

\n
**standard_reference_params** 

These keys should be defined if the user would like to register input to a standard reference image (either )

.. _std_ref_inputs:

.. list-table:: Standard reference image input dictionary keys.
   :widths: 30 15 15 40
   :header-rows: 1

   * - **Key Name**
     - **Required?**
     - **Data Type**
     - **Description**
   * - file
     - REQUIRED
     - string
     - Standard reference filename located within the FSL standard data directory
   * - type
     - REQUIRED
     - string
     - type of input file: FSL **CURRENTLY UNUSED**
   * - output_matrix_suffix
     - REQUIRED
     - string
     - suffix for the output registration matrix (standard in highres2standard.mat)
   * - output_bids_labels
     - REQUIRED
     - dictionary
     - Supplemental bids filename dictionary as explained in **NEEDS REFERENCE**
   * - output_json_values
     - REQUIRED
     - dictionary
     - Supplemental key-value pairs to additionally insert into the JSON sidecar accompanying input-to-standard transformed image

     