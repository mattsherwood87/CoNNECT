

connect_flirt.py
==========================

    
This function executes registration via FSL's FLIRT using :ref:`flirt.py <flirt_python>`.

This function can be executed via command-line only:

.. code-block:: shell-session

    $ connect_flirt.py -p <project_identifier> --apt --asl --struc --overwrite --progress -s 

-p PROJECT, --project PROJECT   **REQUIRED** project to identify the associated :ref:`searchTable <read_creds_python>` to query images with filenames containing BIDS labels specified in :ref:`main_params.input_bids_labels <flirt_json>`
--apt  utilize a 3D ATPw image as input for registration. This loads a FLIRT JSON control file <project_identifier>_apt_flirt_input.json
--asl   utilize an ASL image as input for registration. This loads a FLIRT JSON control file <project_identifier>_asl_flirt_input.json
--struc  utilize a structural image as input for registration. This loads a FLIRT JSON control file <project_identifier>_struc_flirt_input.json
-h, --help  show the help message and exit
--overwrite  force registration by skipping directory and database checking
--progress  verbose mode
-s, --submit    submit conversion to the HTCondor queue for multi-threaded CPU processing
-v, --version   display the current version


.. note:: If multiple modality flags are provided (--apt, --struc, --asl), structural registration is performed first.
