connect_rawdata_check.py
==========================

    
This function creates a table to indicate the absence (0) or presence (1) of MRI rawdata (NIfTI). Rawdata are identified via the project's
`scan ID JSON control file <https://connect-tutorial.readthedocs.io/en/latest/project-specific_JSON_control_files/index.html#scan-id>`_. An 
output table in CSV format is created in the Project's 'processing_logs' directory titled <project_identifier>_rawdata_check.csv.

This function can be executed via command-line only using the following options:

-p PROJECT, --project PROJECT   **REQUIRED** This project's `searchTable <https://connect-tutorial.readthedocs.io/en/latest/support_tools/index.html#read-credentials-py>`_ will be queried for all NIfTI images to identify images matching those scan sequences present in the scan ID JSON control file.
-h, --help  show the help message and exit
--progress  verbose mode
-v, --version   display the current version


.. code-block:: shell-session

    $ connect_rawdata_check.py -p <project_identifier> 
