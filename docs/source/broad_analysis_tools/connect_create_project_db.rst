


connect_create_project_db.py
==========================

    
This function creates the Project's searchTable and searchSourceTable, as defined via the credentials JSON file loaded by :ref:`read_creds_python`.

This function can be executed via command-line only using the following options:

.. code-block:: shell-session

    $ connect_create_project_db.py -p <project_identifier> 

-p PROJECT, --project PROJECT   **REQUIRED** create MySQL tables named from the searchTable and searchSourceTable keys associated with the defined project
-h, --help  show the help message and exit
--progress  verbose mode
-v, --version   display the current version



