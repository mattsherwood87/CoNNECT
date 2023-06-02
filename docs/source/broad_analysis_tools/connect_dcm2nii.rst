.. _connect_dcm2nii_py:

connect_dcm2nii.py
==========================

    
This function converts DICOM images to NIfTI utilizing dcm2niix and :ref:`convert_dicoms_py`. Files within the identified Project's searchSourceTable, :ref:`credentials JSON file <read_credentials_py>` credentials JSON file read by :ref:`read_credentials_py`,
are queried via MySQL for DICOM images. These DICOm images are contained within the Project's sourcedata directory. Directories within sourcedata that contain DICOM images are then passed to dcm2niix for 
conversion. The NIfTI images created are then stored in the same sourcedata directory as their source DICOM directory.

.. seealso::
    The `dcm2niix <https://www.nitrc.org/plugins/mwiki/index.php/dcm2nii:MainPage>`_ is the most common tool for DICOM-to-NIfTI conversion, and is implemented on our Ubuntu 20.04 CoNNECT NPC nodes.

This function can be executed via command-line only using the following options:

-p PROJECT, --project PROJECT   **REQUIRED** project to identify the associated searchSourceTable to query DICOM images for NIfTI conversion
-h, --help  show the help message and exit
--overwrite  force conversion by skipping directory and database checking
--progress  verbose mode
-s, --submit    submit conversion to the HTCondor queue for multi-threaded CPU processing
-v, --version   display the current version


.. code-block:: shell-session

    $ connect_dcm2nii.py -p <project_identifier> --overwrite --submit --progress
