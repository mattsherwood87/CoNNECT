connect_neuro_db_update.py
==========================

.. py:function:: connect_neuro_db_update()
    
    This function only supports command-line interface described as:

    **Required Arguments:**
    -p <project_identifier>, --project=<project_identifier>
        search the selected Project Table, can provide term 'all' to update all tables in credentials.json

    **Optional Arguments:**
    -h, --help  show the help message and exit
    --progress  verbose mode
    -s, --source    update the searchSourceTable
    -m, --main  update the searchTable
    -v, --version   display the current version


connect_neuro_db_update.py supports execution via command-line only:

.. code-block:: shell-session

    $ connect_neuro_db_update.py -p <project_identifier> --main --source --progress 
