


connect_create_project_db.py
==========================

    
This function creates the Project's searchTable and searchSourceTable, as defined via the `credentials.json file <https://connect-tutorial.readthedocs.io/en/latest/support_tools/index.html#read-credentials-py>`_.
This function can be executed via command-line only using the following options:

-p PROJECT, --project PROJECT   **REQUIRED** search the selected table for the indicated <project_identifier> can provide term 'all' to update all tables in credentials.json
-h, --help  show the help message and exit
--progress  verbose mode
-s, --source    update the searchSourceTable, as defined via the `credentials.json file <https://connect-tutorial.readthedocs.io/en/latest/support_tools/index.html#read-credentials-py>`_
-m, --main  update the searchTable, as defined via the `credentials.json file <https://connect-tutorial.readthedocs.io/en/latest/support_tools/index.html#read-credentials-py>`_
-v, --version   display the current version


.. code-block:: shell-session

    $ connect_create_project_db.py -p <project_identifier> 
