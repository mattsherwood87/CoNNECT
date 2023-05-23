connect_neuro_db_update.py
==========================

    
This function only supports command-line interface with the options:

**Required Arguments:**
-p PROJECT, --project PROJECT   search the selected table for the indicated <project_identifier> can provide term 'all' to update all tables in credentials.json

**Optional Arguments:**

-h, --help  show the help message and exit
--progress  verbose mode
-s, --source    update the searchSourceTable
-m, --main  update the searchTable
-v, --version   display the current version


.. code-block:: shell-session

    $ connect_neuro_db_update.py -p <project_identifier> --main --source --progress 
