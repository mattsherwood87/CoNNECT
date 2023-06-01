connect_dcm2nii.py
==========================

    
This function converts DICOM images in a Project's `searchSourceTable <https://connect-tutorial.readthedocs.io/en/latest/support_tools/index.html#read-credentials-py>`_ MySQL table 
for DICOM images contained in the sourcedata directory. These DICOM images are then converted to NIfTI images via dcm2niix and stored within the same sourcedata directory.

.. seealso::
    NEED TO WRITE This

This function can be executed via command-line only using the following options:

-p PROJECT, --project PROJECT   **REQUIRED** project to identify the associated `searchSourceTable <https://connect-tutorial.readthedocs.io/en/latest/support_tools/index.html#read-credentials-py>`_ to query DICOM images for NIfTI conversion
-h, --help  show the help message and exit
--overwrite  force conversion by skipping directory and database checking
--progress  verbose mode
-s, --submit    submit conversion to the HTCondor queue for multi-threaded CPU processing
-v, --version   display the current version


.. code-block:: shell-session

    $ connect_dcm2nii.py -p <project_identifier> --overwrite --submit --progress
