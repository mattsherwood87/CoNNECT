connect_neuro_db_query.py
==========================

.. py:function:: connect_neuro_db_query()
    
    This function only supports command-line interface described as:

    Required Arguments:

    -p <project_identifier>, --project <project_identifier>
        search the selected Project Table
    -r REGEXSTR, --regex REGEXSTR
        Search string (no wildcards, matches if the search string appears anywhere in the field specified by -w|--where)

    Optional Arguments:

    -h, --help 
        show the help message and exit
    -c RETURNCOL, --col RETURNCOL
        column to return (default 'fullpath')
    -w SEARCHCOL, --were SEARCHCOL
        column to search (default 'filename')
    -o ORDERBY, --orderby ORDERBY
        column to sort results (default 'fullpath')
    --progress
        verbose mode
    --source 
        search searchSourceTable instead of searchTable
    --opt-inclusion INCLUSION [INCLUSION ...]
        optional additional matching search string(s) to filter results. Multiple inputs accepted through space delimiter
    --opt-exclusion EXCLUSION [EXCLUSION ...]
        optional additional exclusionary search string(s) to filter results. Multiple inputs accepted through space delimiter
    --opt-or-inclusion INCLUSION [INCLUSION ...]
        optional additional OR matching search string(s) to filter results. Multiple inputs accepted through space delimiter
    -v, --version
        display the current version


connect_neuro_db_query.py supports execution via command-line only:

.. code-block:: shell-session

    $ connect_neuro_db_query.py -p <project_identifier> -r REGEXSTR --col RETURNCOL --where SEARCHCOL --orderby ORDERBY --progress --source --opt-inclusion INCLUSION1 INCLUSION2 --opt-exclusion EXCLUSION1 EXCLUSION2 --opt-or-inclusion ORINCLUSION1 ORINCLUSION2 --version
