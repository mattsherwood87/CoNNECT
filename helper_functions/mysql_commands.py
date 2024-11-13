#!/resshare/general_processing_codes/python3_venv/bin/python
# the command above ^^^ sets python 3.10.10 as the interpreter for this program

# Created by Matthew Sherwood (matt.sherwood@wright.edu, matthew.sherwood.7.ctr@us.af.mil)
# Created on 21 Jan 2021
#
# v3.0.0 on 1 April 2023
# Modified on 20 Oct 2021 - elimination of mysql database in supplement of list bucket from boto3
# modified on 21 Jan 2021

import sys
import os
import re
import pymysql


# REALPATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
# sys.path.append(REALPATH)
REALPATH = os.path.join('/resshare','general_processing_codes')
sys.path.append(REALPATH)

# from classes.creds import */
import helper_functions as hf


VERSION = '4.0.0'
DATE = '5 April 2023'


# ******************* s3 bucket check ********************
def query_file(regexStr,*args,**kwargs):
    k = {}
    for key in kwargs:
        k[key] = kwargs[key]

    outFileOrig = sql_query(database=hf.creds.database,searchtable=hf.creds.searchTable,searchcol='fullpath',regex=regexStr,**k) #only look on s3


    if len(outFileOrig) == 1: #if 1 file on database
        outFile = outFileOrig[0]
        
    elif len(outFileOrig) == 0:
        print('WARNING: no files found matching ' + regexStr + ' in ' + hf.creds.searchTable)
        outFile = None
    else:
        print('WARNING: more than 1 file found matching ' + regexStr + ' in ' + hf.creds.searchTable)
        outFile = None
        
        
    #sys.exit()
    return outFile



# ******************* database check ********************
def query_source_file(regexStr,*args,**kwargs):
    k = {}
    for key in kwargs:
        k[key] = kwargs[key]

    outFileOrig = sql_query(database=hf.creds.database,searchtable=hf.creds.searchSourceTable,searchcol='fullpath',regex=regexStr,**k) #only look on s3


    if len(outFileOrig) == 1: #if 1 file on database
        outFile = outFileOrig[0]
        
    elif len(outFileOrig) == 0:
        # print('WARNING: no files found matching ' + regexStr + ' in ' + hf.creds.searchSourceTable)
        outFile = None
    else:
        print('WARNING: more than 1 file found matching ' + regexStr + ' in ' + hf.creds.searchSourceTable)
        outFile = None
        
        
    #sys.exit()
    return outFile



# ******************* QUERY FOR DIRECTORIES CONTAINING DICOMS ********************
def sql_query_files(regexStr,*args,**kwargs):
    
    #connect to sql database
    fullpath = []
    fullpath = sql_query(database=hf.creds.database,searchtable=hf.creds.searchTable,regex=regexStr,**kwargs)

    return fullpath



# ******************* QUERY OUTPUT DIRECTORIES FOR NIFTIS ********************
def sql_query_dir_check(regexStr,dirToCheck,showProgress):
    
    #connect to sql database
    fullpath = sql_query(database=hf.creds.database,searchtable=hf.creds.searchTable,returncol='fullpath',searchcol='fullpath',regex=regexStr,progress=showProgress,inclusion=dirToCheck)

    #remove directories from list (only keep files)
    for line in fullpath:
        if line[-1] == '/':
            fullpath.remove(line)


    #dont process if nifti's exist in associated processed_data directory
    if len(fullpath) > 0:
        return True
    else:
        return False

    


# ******************* QUERY FOR DIRECTORIES CONTAINING DICOMS ********************
def sql_query_dirs(regexStr,showProgress,rawFlag,*args,**kwargs):

    inclusion = kwargs.get('inclusion',None)
    exclusion = kwargs.get('exclusion',None)

    if isinstance(inclusion,str):
        inclusion = inclusion.split()
    if isinstance(exclusion,str):
        exclusion = exclusion.split()


    dirsToProcess = []
    tmp_dirsToProcess = []
    fullpath = []
    
    #connect to sql database
    if rawFlag:
        fullpath = sql_query(database=hf.creds.database,searchtable=hf.creds.searchSourceTable,prefix=hf.creds.dataDir,returncol='fullpath',searchcol='fullpath',regex=regexStr,progress=showProgress,inclusion=inclusion,exclusion=exclusion)
    else:
        fullpath = sql_query(database=hf.creds.database,searchtable=hf.creds.searchTable,prefix=hf.creds.dataDir,returncol='fullpath',searchcol='fullpath',regex=regexStr,progress=showProgress,inclusion=inclusion,exclusion=exclusion)

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
def sql_query(*args, **kwargs):
    """
    Performs a query into the provided table/column using the search criteria identified.

    sql_query(database='CoNNECT', searchtable=False, returncol='fullpath', searchcol='filename', regex=None, progress=False, orderby='fullpath', inclusion=None, exclusion=None, orinclusion=None)

    Arguments:

        project (str): target Project's <project identifier>

    Returns:
        None
    """
    db = kwargs.get('database','CoNNECT')
    st = kwargs.get('searchtable',None)
    col = kwargs.get('returncol','fullpath')
    where = kwargs.get('searchcol','filename')
    regexstr = kwargs.get('regex',None)
    progress = kwargs.get('progress',False)
    orderby = kwargs.get('orderby','fullpath')
    inclusion = kwargs.get('inclusion',None)
    exclusion = kwargs.get('exclusion',None)
    or_inclusion = kwargs.get('orinclusion',None)

    if isinstance(inclusion,str):
        inclusion = inclusion.split()
    if isinstance(exclusion,str):
        exclusion = exclusion.split()
    if isinstance(or_inclusion,str):
        or_inclusion = or_inclusion.split()

    if st == None or regexstr == None:
        print("ERROR: must define searchtable AND regex")
    
    #connect to sql database
    sqlConnection = create_mysql_connection('localhost','ubuntu','neuroscience',db,progress)
    sqlCursor = sqlConnection.cursor()


    if sql_check_table_exists(sqlCursor,st):

        #create query
        if regexstr == '':
            sqlQuery ="""SELECT %s FROM %s WHERE %s ORDER BY %s;""" % (col,st,where,orderby)
        else:
            sqlQuery ="""SELECT %s FROM %s WHERE %s REGEXP "%s" """ % (col,st,where,regexstr)
            if inclusion:
                for inc in inclusion:
                    sqlQuery += """AND %s REGEXP "%s" """ % (where,inc)
            if exclusion:
                for exc in exclusion:
                    sqlQuery += """AND %s NOT REGEXP "%s" """ % (where,exc)
            if or_inclusion:

                sqlQuery += """AND (%s REGEXP "%s" """% (where,or_inclusion[0])
                for or_inc in or_inclusion[1:]:
                    sqlQuery += """OR %s REGEXP "%s" """ % (where,or_inc)
                sqlQuery = sqlQuery[:-1]
                sqlQuery += """) """ 
            sqlQuery +="ORDER BY %s;" % (orderby)
    else:
        sqlConnection.close()
        return []
    
    # run quory
    sqlCursor.execute(sqlQuery)
    sqlConnection.close()

    #get sql returned list
    # tmp_fullpath = sqlCursor.fetchall()
    return [f[0] for f in sqlCursor.fetchall()]


# ******************* QUERY FOR DIRECTORIES CONTAINING DICOMS ********************
def sql_multiple_query(*args, **kwargs):
    """

    """
    db = kwargs.get('database','CoNNECT')
    st = kwargs.get('searchtable',None)
    cols = kwargs.get('returncols','fullpath')
    where = kwargs.get('searchcol','filename')
    regexstr = kwargs.get('regex',None)
    progress = kwargs.get('progress',False)
    orderby = kwargs.get('orderby','fullpath')
    inclusion = kwargs.get('inclusion',None)
    exclusion = kwargs.get('exclusion',None)

    if st == None or regexstr == None:
        print("ERROR: must define searchtable AND regex")
    
    #connect to sql database
    sqlConnection = create_mysql_connection('localhost','ubuntu','neuroscience',db,progress)
    sqlCursor = sqlConnection.cursor()

    if sql_check_table_exists(sqlCursor,st):

        #create query
        sqlQuery ="""SELECT %s FROM %s WHERE %s REGEXP "%s" ORDER BY %s""" % (cols,st,where,regexstr,orderby)
        
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
def sql_create_project_tables(*args, **kwargs):
    #check progress input flag
    progress = kwargs.get('progress',False)
    
    #connect to sql database
    sqlConnection = create_mysql_connection('localhost','ubuntu','neuroscience',hf.creds.database,progress)
    sqlCursor = sqlConnection.cursor()

    #create table
    if not sql_check_table_exists(sqlConnection.cursor(),hf.creds.searchTable):
        sqlCMD ="""CREATE TABLE %s ( fullpath char(255), filename varchar(255), basename varchar(255), extension varchar(48) );""" % (hf.creds.searchTable)

        #run command
        sqlCursor.execute(sqlCMD)
    else:
        print('WARNING: table ' + hf.creds.searchTable + ' already exists')

    #create sourcedata table
    if not sql_check_table_exists(sqlConnection.cursor(),hf.creds.searchSourceTable):
        sqlCMD ="""CREATE TABLE %s ( fullpath char(255), filename varchar(255) );""" % (hf.creds.searchSourceTable)
        sqlCursor.execute(sqlCMD)
    else:
        print('WARNING: table ' + hf.creds.searchSourceTable + ' already exists')

    sqlConnection.commit()
    sqlConnection.close()



# ******************* APPEND ITEM(S) TO TABLE ********************
def sql_table_insert(table,item,*args, **kwargs):
    progress = kwargs.get('progress',False)
    
    #connect to sql database
    sqlConnection = create_mysql_connection('localhost','ubuntu','neuroscience',hf.creds.database,progress)
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
def sql_table_remove(table,item,*args, **kwargs):
    progress = kwargs.get('progress',False)
    
    #connect to sql database
    sqlConnection = create_mysql_connection('localhost','ubuntu','neuroscience',hf.creds.database,progress)
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


def sql_check_table_exists(sqlCursor, table):
    sqlCursor.execute("""SELECT COUNT(*) FROM information_schema.tables WHERE table_name = '%s'""" % (table))
    if sqlCursor.fetchone()[0] == 1:
        return True

    return False


# ******************* CREATE CONNECTION TO MYSQL DATABASE ********************
def create_mysql_connection(host_name, user_name, user_password, db_name, progress):
    """
    This function does this...
    """
    connection = None
    try:
        connection = pymysql.connect(#_mysql.connect(
            host=host_name,
            user=user_name,
            passwd=user_password,
            db=db_name,
            unix_socket='/var/run/mysqld/mysqld.sock'
        )
        if progress:
            print("Connection to MySQL DB successful")
    except Exception as e:
        print('MySQL connection error ' + e + ' occurred')

    return connection