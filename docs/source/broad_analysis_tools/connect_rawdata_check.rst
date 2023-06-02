


connect_rawdata_check.py
==========================

    
This function creates a table to indicate the absence (0) or presence (1) of MRI rawdata (NIfTI). Rawdata are identified via the project's 
:ref:`scan ID JSON control file <scan_id_json>`. An output table in CSV format is created in the Project's 'processing_logs' directory titled 
<project_identifier>_rawdata_check.csv.

This function can be executed via command-line only:

.. code-block:: shell-session

    $ connect_rawdata_check.py -p <project_identifier> 

-p PROJECT, --project PROJECT   **REQUIRED** This project's :ref:`searchTable <read_creds_python>` will be queried for all NIfTI images to identify images matching those scan sequences present in the scan ID JSON control file.
-h, --help  show the help message and exit
--progress  verbose mode
-v, --version   display the current version


