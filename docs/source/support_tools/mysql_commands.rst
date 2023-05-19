
mysql_commands.py
===============


sql_multiple_query
------------------

.. py:function:: sql_multiple_query(*args,**kwargs)
    
    test

    :param database: Optional "kind" of ingredients.
    :param searchtable: REQUIRED
    :type database: string
    :type searchtable: string
    :raise lumache.InvalidKindError: If the kind is invalid.
    :return: The ingredients list.
    :rtype: list[str]


query_file
---------

.. py:function:: query_source_file(regexStr,*args,**kwargs)
    
    Performs a query into the Project's searchTable's 'fullpath' column using the search criteria identified for a single file. Returns a single filepath.

    query_file(regexStr, database='CoNNECT', searchtable=None, returncol='fullpath', searchcol='filename', progress=False, orderby='fullpath', inclusion=None, exclusion=None, orinclusion=None)

    :param regexStr: Required initial search terms
    :param returncol: Optional table column to return (default 'fullpath')
    :param progress: Optional operate in verbose mode
    :param orderby: Optional column to sort results (default 'fullpath')
    :param inclusion: Optional inclusion criteria to refine results. These must also be contained within searchcol (AND operation)
    :param exclusion: Optional exclusion criteria to refine results. These must not be within the searchcol
    :param orinclusion: Optional inclusion criteria to refine results. These may also be contained within the search column (OR operation)
    :type regexStr: str
    :type returncol: str
    :type progress: bool
    :type orderby: str 
    :type inclusion: str or list[str]
    :type exclusion: str or list[str]
    :type orinclusion: str or list[str]
    :raise Error: Any error occurs
    :return: Fullpath to a single file if only 1 file matches the search criteria, otherwise None.
    :rtype: None or str

    
query_source_files
---------

.. py:function:: query_source_file(regexStr,*args,**kwargs)
    
    Performs a query into the Project's searchSourceTable's 'fullpath' column using the search criteria identified for a single file. Returns a single filepath.

    query_source_file(regexStr, database='CoNNECT', searchtable=None, returncol='fullpath', searchcol='filename', progress=False, orderby='fullpath', inclusion=None, exclusion=None, orinclusion=None)

    :param regexStr: Required initial search terms
    :param returncol: Optional table column to return (default 'fullpath')
    :param progress: Optional operate in verbose mode
    :param orderby: Optional column to sort results (default 'fullpath')
    :param inclusion: Optional inclusion criteria to refine results. These must also be contained within searchcol (AND operation)
    :param exclusion: Optional exclusion criteria to refine results. These must not be within the searchcol
    :param orinclusion: Optional inclusion criteria to refine results. These may also be contained within the search column (OR operation)
    :type regexStr: str
    :type returncol: str
    :type progress: bool
    :type orderby: str 
    :type inclusion: str or list[str]
    :type exclusion: str or list[str]
    :type orinclusion: str or list[str]
    :raise Error: Any error occurs
    :return: Fullpath to a single sourcedata file if only 1 file matches the search criteria, otherwise None.
    :rtype: None or str

    
sql_query_dir_check
---------

.. py:function:: sql_query_dirs(regexStr,dirToCheck,showProgress)
    
    Queries a directory for existing NIfTI images.

    sql_query_dirs(regexStr, dirToCheck, showProgress)

    :param regexStr: Required search string
    :param dirToCheck: Required directory to perform a NIfTI image search
    :param showProgress: Required verbose mode
    :type regexStr: str
    :type dirToCheck: str
    :type showProgress: bool
    :raise Error: Any error occurs
    :return: NIfTI files exist in <dirToCheck>
    :rtype: bool

    
sql_query_dirs
---------

.. py:function:: sql_query_dirs(regexStr,showProgress,rawFlag,*args,**kwargs)
    
    Performs a query into the provided table/column using the search criteria identified. Returns unique directories containing the identified files.

    sql_query_dirs(regexStr, showProgress, rawFlag, inclusion=None, exclusion=None)

    :param regexStr: Required search string
    :param showProgress: Required verbose mode
    :param rawFlag: Required true for project's searchSourceTable (default false - project's searchTable)
    :param inclusion: Optional inclusion criteria to refine results. These must also be contained within searchcol (AND operation)
    :param exclusion: Optional exclusion criteria to refine results. These must not be within the searchcol
    :type regexStr: str
    :type showProgress: bool
    :type rawFlag: bool
    :type inclusion: str or list[str]
    :type exclusion: str or list[str]
    :raise Error: Any error occurs
    :return: The list of directories containing files matching search criteria
    :rtype: list[str]


sql_query
---------

.. py:function:: sql_query(*args,**kwargs)
    
    Performs a query into the provided table/column using the search criteria identified.

    sql_query(database='CoNNECT', searchtable=None, returncol='fullpath', searchcol='filename', regex=None, progress=False, orderby='fullpath', inclusion=None, exclusion=None, orinclusion=None)

    :param database: Optional MySQL database containing the project's searchtable (default 'CoNNECT')
    :param searchtable: Required MySQL table to query
    :param returncol: Optional table column to return (default 'fullpath')
    :param searchcol: Optional table column to query (default 'filepath')
    :param regex: Required initial search terms
    :param progress: Optional operate in verbose mode
    :param orderby: Optional column to sort results (default 'fullpath')
    :param inclusion: Optional inclusion criteria to refine results. These must also be contained within searchcol (AND operation)
    :param exclusion: Optional exclusion criteria to refine results. These must not be within the searchcol
    :param orinclusion: Optional inclusion criteria to refine results. These may also be contained within the search column (OR operation)
    :type database: str
    :type searchtable: str
    :type returncol: str
    :type searchcol: str
    :type regex: str
    :type progress: bool
    :type orderby: str 
    :type inclusion: str or list[str]
    :type exclusion: str or list[str]
    :type orinclusion: str or list[str]
    :raise Error: Any error occurs
    :return: The list of columns matching search criteria
    :rtype: list[str]


sql_multiple_query
---------

.. py:function:: sql_multiple_query(*args,**kwargs)
    
    Performs a query into the provided table/column using the search criteria identified.

    sql_multiple_query(database='CoNNECT', searchtable=None, returncol='fullpath', searchcol='filename', regex=None, progress=False, orderby='fullpath')

    :param database: Optional MySQL database containing the project's searchtable (default 'CoNNECT')
    :param searchtable: Required MySQL table to query
    :param returncol: Optional table column to return (default 'fullpath')
    :param searchcol: Optional table column to query (default 'filepath')
    :param regex: Required initial search terms
    :param progress: Optional operate in verbose mode
    :param orderby: Optional column to sort results (default 'fullpath')
    :type database: str
    :type searchtable: str
    :type returncol: str
    :type searchcol: str
    :type regex: str
    :type progress: bool
    :type orderby: str 
    :raise Error: Any error occurs
    :return: All the columns elements from each row where the input column matches the search criteria
    :rtype: list[list[str]]


sql_create_project_tables
---------

.. py:function:: sql_create_project_tables(*args,**kwargs)
    
    Creates the tables for a project whose credentials have been loaded into custom creds class via read_credentials().

    sql_create_project_tables(progress=False)

    :param progress: Optional operate in verbose mode
    :type progress: bool
    :raise Error: Any error occurs
    :return: None
    :rtype: None


sql_table_insert
---------

.. py:function:: sql_table_insert(table,item,*args,**kwargs)
    
    Inserts items into a Project's table. The project's credentials must have been loaded into customcreds class via read_credentials().

    sql_table_insert(table,item,progress=False)

    :param table: Required MySQL table name
    :param item: Required elements to insert into the table
    :param progress: Optional operate in verbose mode
    :type table: str
    :type item: dict or list
    :type progress: bool
    :raise Error: Any error occurs
    :return: None
    :rtype: None


sql_table_remove
---------

.. py:function:: sql_table_insert(table,item,*args,**kwargs)
    
    Removes items into a Project's table. The project's credentials must have been loaded into customcreds class via read_credentials().

    sql_table_remove(table,item,progress=False)

    :param table: Required MySQL table name
    :param item: Required elements to remove from the table
    :param progress: Optional operate in verbose mode
    :type table: str
    :type item: dict or list
    :type progress: bool
    :raise Error: Any error occurs
    :return: None
    :rtype: None


sql_check_table_exists
---------

.. py:function:: sql_check_table_exists(sqlCursor,table)
    
    Checks if a table exists

    sql_table_remove(sqlCursor, table)

    :param sqlCursor: Required pymysql connect cursor object
    :param table: Required MySQL table name
    :type sqlCursor: pymysql.connect.cursor
    :type table: str
    :raise Error: Any error occurs
    :return: None
    :rtype: None


sql_create_mysql_connection
---------

.. py:function:: sql_create_mysql_connection(host_name,user_name,user_password,db_name,progress)
    
    Creates a connection to the MySQL database.

    sql_create_mysql_connection(host_name, user_name, user_password, db_name, progress)

    :param host_name: Required MySQL master hostname
    :param user_name: Required MySQL username
    :param user_password: Required MySQL user password
    :param db_name: Required MySQL database
    :param progress: Required operate in verbose mode
    :type host_name: str
    :type user_name: str
    :type user_password: str
    :type db_name: str
    :type progress: bool
    :raise Error: Any error occurs
    :return: Pymysql connect object
    :rtype: pymysql.connect

