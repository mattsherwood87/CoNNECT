
.. _flirt_params_file:

flirt_params
------------

.. _FLIRT_params_table:

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
   * - out_matrix_file
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
     - phase encode direction of EPI - 1,2,3=x,y,z & -1,-2,-3=x,-y,-z
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



**standard_reference_image** 

.. _std_reference_inputs:

.. list-table:: Standard reference image input dictionary keys.
   :widths: 30 15 15 40
   :header-rows: 1

   * - **Key Name**
     - **Required?**
     - **Data Type**
     - **Description**
   * - in_file
     - REQUIRED
     - exisitng file name
     - name of input image
   * - ref_file
     - REQUIRED
     - existing file name
     - name of reference image
   * - affine_file
     - OPTIONAL
     - exisitng file name
     - name of file containing affine transform 
   * - 
