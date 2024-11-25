# functions.py
# the command above ^^^ sets python 3.10.10 as the interpreter for this program

# Created by Matthew Sherwood (matt.sherwood@wright.edu, matthew.sherwood.7.ctr@us.af.mil)
# Created on 21 Jan 2021
#
# v3.0.0 on 1 April 2023
# Modified on 20 Oct 2021 - elimination of mysql database in supplement of list bucket from boto3
# modified on 21 Jan 2021

import sys
import os
import pymysql
import pymysql.cursors


# REALPATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
# sys.path.append(REALPATH)
REALPATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
sys.path.append(REALPATH)

# from classes.creds import */
import support_tools as st


VERSION = '4.0.0'
DATE = '5 April 2023'

# ******************* s3 bucket check ********************
def query_source_file(regex: str, returncol: str='fullpath', orderby: str='fullpath', inclusion: str|list=None, exclusion: str|list=None, progress: bool=False) -> str:
    """
    This function queries the table specified in the support_tools.creds.searchTable object for a single file. The fullpath to the single file is returned.

    query_file(regexStr,PROGRESS=False)

    :param regex: search string for query
    :type regex: str

    :param returncol: table column to return in query, defaults to 'fullpath'
    :type returncol: str, optional

    :param orderby: solumn to sort returns by, defaults to 'fullpath'
    :type orderby: str, optional

    :param inclusion: string or list of strings that are additionally required for an item be returned, defaults to None
    :type inclusion: str | list, optional

    :param exclusion: string or list of strings that will exclude items from being returned, defaults to None
    :type exclusion: str | list, optional

    :param progress: flag to display command line output providing additional details on the processing status, defaults to False
    :type progress: bool, optional

    :return: output table column from all items matching the specified search criteria
    :rtype: str
    """  


    outFileOrig = sql_query(database=st.creds.database,searchtable=st.creds.searchTable,searchcol='fullpath',regex=regex,returncol=returncol,orderby=orderby,inclusion=inclusion,exclusion=exclusion,progress=progress) #only look on s3


    if len(outFileOrig) == 1: #if 1 file on database
        outFile = outFileOrig[0]
        
    elif len(outFileOrig) == 0:
        print('WARNING: no files found matching ' + regex + ' in ' + st.creds.searchSourceTable)
        outFile = None
    else:
        print('WARNING: more than 1 file found matching ' + regex + ' in ' + st.creds.searchSourceTable)
        outFile = None
        
        
    #sys.exit()
    return outFile


# ******************* s3 bucket check ********************
def query_file(regex: str, returncol: str='fullpath', orderby: str='fullpath', inclusion: str|list=None, exclusion: str|list=None, progress: bool=False) -> str:
    """
    This function queries the table specified in the support_tools.creds.searchTable object for a single file. The fullpath to the single file is returned.

    query_file(regexStr,PROGRESS=False)

    :param regex: search string for query
    :type regex: str

    :param returncol: table column to return in query, defaults to 'fullpath'
    :type returncol: str, optional

    :param orderby: solumn to sort returns by, defaults to 'fullpath'
    :type orderby: str, optional

    :param inclusion: string or list of strings that are additionally required for an item be returned, defaults to None
    :type inclusion: str | list, optional

    :param exclusion: string or list of strings that will exclude items from being returned, defaults to None
    :type exclusion: str | list, optional

    :param progress: flag to display command line output providing additional details on the processing status, defaults to False
    :type progress: bool, optional

    :return: output table column from all items matching the specified search criteria
    :rtype: str
    """  


    outFileOrig = sql_query(database=st.creds.database,searchtable=st.creds.searchTable,searchcol='fullpath',regex=regex,returncol=returncol,orderby=orderby,inclusion=inclusion,exclusion=exclusion,progress=progress) #only look on s3


    if len(outFileOrig) == 1: #if 1 file on database
        outFile = outFileOrig[0]
        
    elif len(outFileOrig) == 0:
        print('WARNING: no files found matching ' + regex + ' in ' + st.creds.searchTable)
        outFile = None
    else:
        print('WARNING: more than 1 file found matching ' + regex + ' in ' + st.creds.searchTable)
        outFile = None
        
        
    #sys.exit()
    return outFile



# ******************* QUERY OUTPUT DIRECTORIES FOR NIFTIS ********************
def sql_query_dir_check(regex: str, targetdir: str, progress: bool=False) -> bool:
    """
    This function ealuates the presence of files in a specified directory.

    :param regex: search string to find matching files
    :type regex: str

    :param targetdir: fullpath to a target directory
    :type targetdir: str

    :param progress: flag to display command line output providing additional details on the processing status, defaults to False
    :type progress: bool, optional

    :return: presencee (True) or absence (False) of files matching the search string in the specified directory
    :rtype: bool
    """
    
    #connect to sql database
    fullpath = sql_query(database=st.creds.database,searchtable=st.creds.searchTable,returncol='fullpath',searchcol='fullpath',regex=regex,progress=progress,inclusion=targetdir)

    #remove directories from list (only keep files)
    for line in fullpath:
        if line[-1] == os.path.sep:
            fullpath.remove(line)


    #dont process if nifti's exist in associated processed_data directory
    if len(fullpath) > 0:
        return True
    else:
        return False

    


# ******************* QUERY FOR DIRECTORIES CONTAINING DICOMS ********************
def sql_query_dirs(regex: str,source: bool=False,inclusion: str|list=None, exclusion: str|list=None, progress: bool=False) -> list:
    """
    Find all unique directories containing files in a MySql table that match the specified search string regex.

    :param regex: string to match in query
    :type regex: str

    :param source: Utilize searchSourceTable instead of searchTable support_tools.creds object, defaults to False
    :type source: str, optional

    :param inclusion: string or list of strings that are additionally required for an item be returned, defaults to None
    :type inclusion: str | list, optional

    :param exclusion: string or list of strings that will exclude items from being returned, defaults to None
    :type exclusion: str | list, optional

    :param progress: flag to display command line output providing additional details on the processing status, defaults to False
    :type progress: bool, optional

    :return: list of fullpath to unique directories containing files
    :rtype: list
    """     

    if isinstance(inclusion,str):
        inclusion = inclusion.split()
    if isinstance(exclusion,str):
        exclusion = exclusion.split()


    dirsToProcess = []
    tmp_dirsToProcess = []
    fullpath = []
    
    #connect to sql database
    if source:
        fullpath = sql_query(searchtable=st.creds.searchSourceTable,regex=regex,database=st.creds.database,returncol='fullpath',searchcol='fullpath',progress=progress,inclusion=inclusion,exclusion=exclusion)
    else:
        fullpath = sql_query(searchtable=st.creds.searchTable,regex=regex,database=st.creds.database,returncol='fullpath',searchcol='fullpath',progress=progress,inclusion=inclusion,exclusion=exclusion)

    fullpath.sort()
    for f in fullpath:
        if tmp_dirsToProcess:
            if not tmp_dirsToProcess[-1] in f:
                tmp_dirsToProcess.append(os.path.dirname(f))
        else:
            tmp_dirsToProcess.append(os.path.dirname(f))
    
    #remove duplicates and return
    dirsToProcess = list(set(tmp_dirsToProcess))
    return dirsToProcess



# ******************* QUERY FOR DIRECTORIES CONTAINING DICOMS ********************
def sql_query(searchtable: str, regex: str, database: str='CoNNECT', returncol: str='fullpath', searchcol: str='filename', orderby: str='fullpath', inclusion: str|list=None, exclusion: str|list=None, orinclusion: str|list=None, progress: bool=False) -> str:
    """
    Find all items in a MySql table that match the specified search string regex.

    :param searchtable: MySql table inside of the specified database
    :type searchtable: str

    :param regex: string to match in query
    :type regex: str

    :param database: MySql database containing table, defaults to 'CoNNECT'
    :type database: str, optional

    :param returncol: table column to return in query, defaults to 'fullpath'
    :type returncol: str, optional

    :param searchcol: table column to perform query, defaults to 'filename'
    :type searchcol: str, optional

    :param orderby: solumn to sort returns by, defaults to 'fullpath'
    :type orderby: str, optional

    :param inclusion: string or list of strings that are additionally required for an item be returned, defaults to None
    :type inclusion: str | list, optional

    :param exclusion: string or list of strings that will exclude items from being returned, defaults to None
    :type exclusion: str | list, optional

    :param progress: flag to display command line output providing additional details on the processing status, defaults to False
    :type progress: bool, optional

    :return: output table column from all items matching the specified search criteria
    :rtype: list
    """    

    if isinstance(inclusion,str):
        inclusion = inclusion.split()
    if isinstance(exclusion,str):
        exclusion = exclusion.split()
    if isinstance(orinclusion,str):
        orinclusion = orinclusion.split()

    # if st == None or regex == None:
    #     print("ERROR: must define searchtable AND regex")
    
    #connect to sql database
    sqlConnection = create_mysql_connection('localhost','ubuntu','neuroscience',database,progress)
    sqlCursor = sqlConnection.cursor()


    if sql_check_table_exists(sqlCursor,searchtable):

        #create query
        if regex == '':
            sqlQuery ="""SELECT %s FROM %s WHERE %s ORDER BY %s;""" % (returncol,searchtable,searchcol,orderby)
        else:
            sqlQuery ="""SELECT %s FROM %s WHERE %s REGEXP "%s" """ % (returncol,searchtable,searchcol,regex)
            if inclusion:
                for inc in inclusion:
                    sqlQuery += """AND %s REGEXP "%s" """ % (searchcol,inc)
            if exclusion:
                for exc in exclusion:
                    sqlQuery += """AND %s NOT REGEXP "%s" """ % (searchcol,exc)
            if orinclusion:

                sqlQuery += """AND (%s REGEXP "%s" """% (searchcol,orinclusion[0])
                for or_inc in orinclusion[1:]:
                    sqlQuery += """OR %s REGEXP "%s" """ % (searchcol,or_inc)
                sqlQuery = sqlQuery[:-1]
                sqlQuery += """) """ 
            sqlQuery +="ORDER BY %s;" % (orderby)
    else:
        sqlConnection.close()
        return []
    
    # run quory
    # print(sqlQuery)
    sqlCursor.execute(sqlQuery)
    sqlConnection.close()

    #get sql returned list
    # tmp_fullpath = sqlCursor.fetchall()
    return [f[0] for f in sqlCursor.fetchall()]


# ******************* QUERY FOR DIRECTORIES CONTAINING DICOMS ********************
def sql_multiple_query(searchtable: str, regex: str, database: str='CoNNECT', returncol: str='fullpath', searchcol: str='filename', orderby: str='fullpath', progress: bool=False) -> str:
    """
    Find all items in a MySql table that match the specified search string regex.

    :param searchtable: MySql table inside of the specified database
    :type searchtable: str

    :param regex: string to match in query
    :type regex: str

    :param database: MySql database containing table, defaults to 'CoNNECT'
    :type database: str, optional

    :param returncol: table column to return in query, defaults to 'fullpath'
    :type returncol: str, optional

    :param searchcol: table column to perform query, defaults to 'filename'
    :type searchcol: str, optional

    :param orderby: solumn to sort returns by, defaults to 'fullpath'
    :type orderby: str, optional

    :param progress: flag to display command line output providing additional details on the processing status, defaults to False
    :type progress: bool, optional

    :return: output table column from all items matching the specified search criteria
    :rtype: list
    """    

    if searchtable == None or regex == None:
        print("ERROR: must define searchtable AND regex")
    
    #connect to sql database
    sqlConnection = create_mysql_connection('localhost','ubuntu','neuroscience',database,progress)
    sqlCursor = sqlConnection.cursor()

    if sql_check_table_exists(sqlCursor,searchtable):

        #create query
        sqlQuery ="""SELECT %s FROM %s WHERE %s REGEXP "%s" ORDER BY %s""" % (returncol,searchtable,searchcol,regex,orderby)
        
        #sqlConnection.query(sqlQuery)
        sqlCursor.execute(sqlQuery)    

    else:
        sqlConnection.close()
        return None

    #get sql returned list
    fullpath = sqlCursor.fetchall()

    #sqlConnection.cursor.close()
    sqlConnection.close()

    return fullpath



# ******************* CREATE TABLES FOR A NEW PROJECT ********************
def sql_create_project_tables(progress: bool=False):
    """
    This function creates the searchTable and searchSourceTable tables in the database for a given project, all specified in support_tools.creds object.

    :param progress: flag to display command line output providing additional details on the processing status, defaults to False
    :type progress: bool, optional
    """    
    
    #connect to sql database
    sqlConnection = create_mysql_connection('localhost','ubuntu','neuroscience',st.creds.database,progress)
    sqlCursor = sqlConnection.cursor()

    #create table
    if not sql_check_table_exists(sqlConnection.cursor(),st.creds.searchTable):
        sqlCMD ="""CREATE TABLE %s ( fullpath char(255), filename varchar(255), basename varchar(255), extension varchar(48) );""" % (st.creds.searchTable)

        #run command
        sqlCursor.execute(sqlCMD)
    else:
        print('WARNING: table ' + st.creds.searchTable + ' already exists')

    #create sourcedata table
    if not sql_check_table_exists(sqlConnection.cursor(),st.creds.searchSourceTable):
        sqlCMD ="""CREATE TABLE %s ( fullpath char(255), filename varchar(255) );""" % (st.creds.searchSourceTable)
        sqlCursor.execute(sqlCMD)
    else:
        print('WARNING: table ' + st.creds.searchSourceTable + ' already exists')

    sqlConnection.commit()
    sqlConnection.close()



# ******************* APPEND ITEM(S) TO TABLE ********************
def sql_table_insert(table: str,item: dict,progress: bool=False):
    """
    This function inserts entry(ies) from item into table from the database specified in support_tools.creds object. 

    sql_table_remove(table,item,progress=True)

    :param table: target table in the database
    :type table: str

    :param item: dictionary containing the table elements of the item(s) to remove
    :type item: dict

    :param progress: flag to display command line output providing additional details on the processing status, defaults to False
    :type progress: bool, optional
    """
    
    #connect to sql database
    sqlConnection = create_mysql_connection('localhost','ubuntu','neuroscience',st.creds.database,progress)
    sqlCursor = sqlConnection.cursor()

    if sql_check_table_exists(sqlCursor,table):

        #create query
        if 'sourcedata' in table:
            if type(item['fullpath']) == list:
                for r in range(len(item['fullpath'])):
                    f = query_source_file(item['fullpath'][r])
                    if f is None:
                        sqlCMD ="""INSERT INTO %s (fullpath, filename) VALUES ('%s', '%s')""" % (table, item['fullpath'][r], item['filename'][r])
                        sqlCursor.execute(sqlCMD)

            else:
                f = query_source_file(item['fullpath'])
                if f is None:
                    sqlCMD ="""INSERT INTO %s (fullpath, filename) VALUES ('%s', '%s')""" % (table, item['fullpath'], item['filename'])
                    sqlCursor.execute(sqlCMD)

        else:
            if type(item['fullpath']) == list:
                for r in range(len(item['fullpath'])):
                    f = query_file(item['fullpath'][r])
                    if f is None:
                        sqlCMD ="""INSERT INTO %s (fullpath, filename, basename, extension) VALUES ('%s', '%s', '%s', '%s')""" % (table, item['fullpath'][r], item['filename'][r], item['basename'][r], item['extension'][r])
                        sqlCursor.execute(sqlCMD)

            else:
                f = query_file(item['fullpath'])
                if f is None:
                    sqlCMD ="""INSERT INTO %s (fullpath, filename, basename, extension) VALUES ('%s', '%s', '%s', '%s')""" % (table, item['fullpath'], item['filename'], item['basename'], item['extension'])
                    sqlCursor.execute(sqlCMD)
    
    # commit changes and close connection
    sqlConnection.commit()
    sqlConnection.close()


# ******************* APPEND ITEM(S) TO TABLE ********************
def sql_table_remove(table: str,item: dict,progress: bool=False):
    """
    This function deletes an entry table from the database specified in support_tools.creds object. 

    sql_table_remove(table,item,progress=True)

    :param table: target table in the database
    :type table: str

    :param item: dictionary containing the table elements of the item(s) to remove
    :type item: dict

    :param progress: flag to display command line output providing additional details on the processing status, defaults to False
    :type progress: bool, optional
    """
    
    #connect to sql database
    sqlConnection = create_mysql_connection('localhost','ubuntu','neuroscience',st.creds.database,progress)
    sqlCursor = sqlConnection.cursor()

    if sql_check_table_exists(sqlCursor,table):

        # create query
        if 'sourcedata' in table:
            if type(item['fullpath']) == list:
                for r in range(len(item['fullpath'])):
                    f = query_source_file(item['fullpath'][r])
                    if f is not None:
                        sqlCMD ="""DELETE FROM %s WHERE fullpath REGEXP '%s'""" % (table, item['fullpath'][r])
                        sqlCursor.execute(sqlCMD)

            else:
                f = query_source_file(item['fullpath'])
                if f is not None:
                    sqlCMD ="""DELETE FROM %s WHERE fullpath REGEXP '%s'""" % (table, item['fullpath'])
                    sqlCursor.execute(sqlCMD)

        else:
            if type(item['fullpath']) == list:
                for r in range(len(item['fullpath'])):
                    f = query_source_file(item['fullpath'][r])
                    if f is not None:
                        sqlCMD ="""DELETE FROM %s WHERE fullpath REGEXP '%s'""" % (table, item['fullpath'][r])
                        sqlCursor.execute(sqlCMD)

            else:
                f = query_source_file(item['fullpath'])
                if f is not None:
                    sqlCMD ="""DELETE FROM %s WHERE fullpath REGEXP '%s'""" % (table, item['fullpath'])
                    sqlCursor.execute(sqlCMD)
    
    # commit changes and close connection
    sqlConnection.commit()
    sqlConnection.close()


def sql_check_table_exists(sqlCursor: pymysql.cursors.Cursor, table: str) -> bool:
    """
    This function checks the database pointed to by the pymysql.cursors.Cursor object for the requested table.

    sql_check_table_exists(sqlCursor, table)

    :param sqlCursor: open cursor opbject to the database
    :type sqlCursor: pymysql.cursor.Cursors

    :param table: target table in the database
    :type table: str

    :return: flag to identify the precense (True) or absence (False) of the specified table in the databaase
    :rtype: bool
    """

    sqlCursor.execute("""SELECT COUNT(*) FROM information_schema.tables WHERE table_name = '%s'""" % (table))
    if sqlCursor.fetchone()[0] == 1:
        return True

    return False


# ******************* CREATE CONNECTION TO MYSQL DATABASE ********************
def create_mysql_connection(host_name: str, user_name:str , user_password: str, db_name: str, progress, unix_socket: str='/var/run/mysqld/mysqld.sock') -> pymysql.connections.Connection:
    """
    This function creates a MySql connection via pymysql. 

    :param host_name: _description_
    :type host_name: str

    :param user_name: _description_
    :type user_name: str

    :param user_password: _description_
    :type user_password: str

    :param db_name: 
    :type db_name: str

    :param progress: flag to display command line output providing additional details on the processing status
    :type progress: bool

    :param unix_socket: path to pysqld.sock, defaults to '/var/run/mysqld/mysqldsock'
    :type unix_socket: str, optional

    :raises Exception: general error encountered during execution

    :return: _description_
    :rtype: pymysql.connecttion.Connection
    """

    connection = None
    try:
        connection = pymysql.connect(
            host=host_name,
            user=user_name,
            passwd=user_password,
            db=db_name,
            unix_socket=unix_socket
        )
        if progress:
            print("Connection to MySQL DB successful")
    except Exception as e:
        print('MySQL connection error ' + e + ' occurred')

    return connection