


connect_create_project_db.py
==========================

    
This function creates the Project's searchTable and searchSourceTable, as defined via the credentials JSON file loaded by :ref:`read_creds_python`.

This function can be executed via command-line only using the following options:

.. code-block:: shell-session

    $ connect_create_project_db.py -p <project_identifier> 

-p PROJECT, --project PROJECT   **REQUIRED** search the selected table for the indicated <project_identifier> can provide term 'all' to update all tables in credentials.json
-h, --help  show the help message and exit
--progress  verbose mode
-s, --source    update the searchSourceTable, as defined via the credentials JSON file read by :ref:`read_creds_python` 
-m, --main  update the searchTable, as defined via the credentials JSON file read by :ref:`read_creds_python` 
-v, --version   display the current version



