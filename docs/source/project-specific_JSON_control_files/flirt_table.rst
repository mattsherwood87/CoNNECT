:topic: Project-Specific JSON Control Files

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



