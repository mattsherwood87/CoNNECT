


connect_neuro_db_query.py
==========================
    
This function will query the Project's MySQL database using the provided search criteria defined below:

.. code-block:: shell-session

    $ connect_neuro_db_query.py -p <project_identifier> -r REGEXSTR --col RETURNCOL --where SEARCHCOL --orderby ORDERBY --progress --source --opt-inclusion INCLUSION1 INCLUSION2 --opt-exclusion EXCLUSION1 EXCLUSION2 --opt-or-inclusion ORINCLUSION1 ORINCLUSION2 --version


-p PROJECT, --project PROJECT   **REQUIRED** search the selected table for the indicated <project_identifier>
-r REGEXSTR, --regex REGEXSTR   **REQUIRED** Search string (no wildcards, matches if the search string appears anywhere in the field specified by -w|--where)

-h, --help  show the help message and exit
-c RETURNCOL, --col RETURNCOL   column to return (default 'fullpath')
-w SEARCHCOL, --were SEARCHCOL  column to search (default 'filename')
-o ORDERBY, --orderby ORDERBY   column to sort results (default 'fullpath')
--progress  verbose mode
--source    search searchSourceTable instead of searchTable, as defined via the `credentials.json file <https://connect-tutorial.readthedocs.io/en/latest/support_tools/index.html#read-credentials-py>`_
--opt-inclusion INCLUSION   optional additional matching search string(s) to filter results. Multiple inputs accepted through space delimiter
--opt-exclusion EXCLUSION   optional additional exclusionary search string(s) to filter results. Multiple inputs accepted through space delimiter
--opt-or-inclusion INCLUSION    optional additional OR matching search string(s) to filter results. Multiple inputs accepted through space delimiter
-v, --version   display the current version
