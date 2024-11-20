#!/resshare/wsuconnect/python3_venv/bin/python
# the command above ^^^ sets python 3.10.10 as the interpreter for this program

# Created by Matthew Sherwood (matt.sherwood@wright.edu, matthew.sherwood.7.ctr@us.af.mil)
# Created on 3 Nov 2020
#
# v2.0.0 on 1 April 2023 - update to remove s3 connections
# v1.4.0 on 24 Sept 2021 - updates to adjust to direct s3 mount - remove mod date and time from table 
# v1.3.0 on 11 Feb 2021 - modify raw tables to only contain fullpath (faster to not index mod time, etc - raw data should only be touched once)
# v1.2.0 on 11 Jan 2021 - add utilization of instance_ids.json

import pandas as pd
import os
import time
import sys
from sqlalchemy import create_engine
import datetime
import argparse
from pathlib import Path


REALPATH = os.path.realpath(__file__)

sys.path.append(os.path.dirname(REALPATH))

import support_tools as st

# GLOBAL INFO
#versioning
VERSION = '2.0.0'
DATE = '1 April 2023'

# ******************* PARSE COMMAND LINE ARGUMENTS ********************

#input argument parser
parser = argparse.ArgumentParser('connect_neuro_db_update.py: Update the selected MySQL table')
parser.add_argument('-p','--project', required=True, action="store", dest="PROJECT", help="update the selected table: all " + ' '.join(st.creds.projects), default=None)
# parser.add_argument('-r','--raw', action="store_true", dest="RAW", help="Command line argument to update the raw_data table for the selected project (default FALSE)", default=False)

parser.add_argument('-s', '--source', help="update the searchSourceTable", action="store_true", dest="SOURCE")
parser.add_argument('-m', '--main', help="update the searchTable", action="store_true", dest="MAIN")
parser.add_argument('-v', '--version', help="Display the current version", action="store_true", dest="version")
parser.add_argument('--progress', help="Show progress (default FALSE)", action="store_true", dest="progress", default=False)
   


# ******************* SORT REQUESTED TABLES ********************
def evaluate_args(options):

    #print version if selected
    if options.version:
        print('kaas_neuro_db_update.py version {0}.'.format(VERSION)+" DATED: "+DATE)


# *******************  TABLE UPDATE  ********************
def update_table(options):
    t = time.time()
    now = datetime.datetime.now()

    if options.progress:
        print("Updating tables " + st.creds.searchTable + " & " + st.creds.searchSourceTable + " in database " + st.creds.database + " @" + now.strftime("%m-%d-%Y %H:%M:%S"))
    # roots = []
    # dirs = []
    files = []
    source_files = []
    #filetype = []
    fullpath = []
    source_fullpath = []
    extension = []
    baseFilename = []
    # modDate = []
    # modTime =[]
    # df = pd.DataFrame(columns=['fullpath','filename','basename','extension'])




    # update mysql
    engine = create_engine('mysql+pymysql://ubuntu:neuroscience@localhost/' + st.creds.database + '?unix_socket=/var/run/mysqld/mysqld.sock')

    # Step through directories
    try:

        #not updating raw files table
        # if not rawFlag:

        # df = pd.DataFrame(columns=['fullpath','filename','basename','extension','modDate','modTime'])
        df = pd.DataFrame(columns=['fullpath','filename','basename','extension'])
        source_df = pd.DataFrame(columns=['fullpath','filename'])


        projectDirs = os.listdir(st.creds.dataDir)
        exclude = 'sourcedata'

        if options.MAIN or (not options.MAIN and not options.SOURCE):
            for projectDir in [d for d in projectDirs if exclude not in d]:
                for f in list(Path(os.path.join(st.creds.dataDir,projectDir)).rglob('*')):

                    #sk`ip directories
                    fullFilename = str(f)
                    if not os.path.isdir(fullFilename):
                        # full filename and path
                        filename = os.path.basename(fullFilename)
                        files.append(filename)
                        fullpath.append(fullFilename)

                        # get basename and extensions (funky due to no filename/extension or multiple '.')
                        idx = filename.find('.')
                        if idx != -1:
                            if idx == 0:
                                baseFilename.append('NULL')
                                extension.append(filename[1:])
                            else:
                                baseFilename.append(filename[:idx])
                                extension.append(filename[idx+1:])
                        else:
                            baseFilename.append(filename)
                            extension.append('NULL')

                        # display file info if quiet is FALSE
                        if options.progress:
                            print(fullpath[-1],files[-1],baseFilename[-1],extension[-1]) #,modDate[-1],modTime[-1])

            # form dataframe for table entry
            df['fullpath'] = fullpath
            df['filename'] = files
            df['basename'] = baseFilename
            df['extension'] = extension

            # update mysql
            # engine = create_engine('mysql+pymysql://ubuntu:neuroscience@localhost/' + st.creds.database + '?unix_socket=/var/run/mysqld/mysqld.sock')
            df.to_sql(st.creds.searchTable, con=engine, if_exists='replace', index=False, chunksize=1000)


        if options.SOURCE or (not options.MAIN and not options.SOURCE): #just store nifti images
            for projectDir in [d for d in projectDirs if exclude in d]:
                # for filename in list(Path(os.path.join(st.creds.dataDir,projectDir)).rglob('*.nii*')):
                for filename in sorted([x[0] for x in os.walk(os.path.join(st.creds.dataDir,projectDir)) if 'acq-' in os.path.basename(x[0])]):
                    #skip directories
                    fullFilename = str(filename)
                    if os.path.isdir(fullFilename):
                        # base = os.path.basename(fullFilename)
                        # if not base.startswith('IM_'):
                        source_fullpath.append(fullFilename)
                        source_files.append(os.path.basename(fullFilename))

                        # display file info if desired
                        if options.progress:
                            print(source_fullpath[-1])


            # form dataframe for table entry
            source_df['fullpath'] = source_fullpath
            source_df['filename'] = source_files

            # update mysql
            source_df.to_sql(st.creds.searchSourceTable, con=engine, if_exists='replace', index=False, chunksize=1000)

        # Return elapsed time
        elapsed_t = time.time() - t
        return elapsed_t
    
    #catch any errors
    except Exception as e:
        print(e)
        elapsed_t = time.time() - t
        return elapsed_t

# *******************  MAIN  ********************    
def main():
    """
    The entry point of this program.
    """
    options = parser.parse_args()
    evaluate_args(options)

    print('updating MySQL tables on ' + datetime.datetime.today().strftime('%Y%m%d @ %H:%M:%S'))


    #loop over all tables
    if options.PROJECT == 'all':
        for p in st.creds.projects:
            st.read_credentials(p)

            elapsed_t = update_table(options)
            
            if (options.MAIN and options.SOURCE) or (not options.MAIN and not options.SOURCE):
                print("Successfully updated " + st.creds.searchTable + " & " + st.creds.searchSourceTable + " in database " + st.creds.database + "\n\tTotal time: " + str(elapsed_t) + " seconds\n\n")
            elif options.MAIN:
                print("Successfully updated " + st.creds.searchTable + " in database " + st.creds.database + "\n\tTotal time: " + str(elapsed_t) + " seconds\n\n")
            elif options.SOURCE:
                print("Successfully updated " + st.creds.searchSourceTable + " in database " + st.creds.database + "\n\tTotal time: " + str(elapsed_t) + " seconds\n\n")

    else:
        st.read_credentials(options.PROJECT)
        elapsed_t = update_table(options)
        if (options.MAIN and options.SOURCE) or (not options.MAIN and not options.SOURCE):
            print("Successfully updated " + st.creds.searchTable + " & " + st.creds.searchSourceTable + " in database " + st.creds.database + "\n\tTotal time: " + str(elapsed_t) + " seconds\n\n")
        elif options.MAIN:
            print("Successfully updated " + st.creds.searchTable + " in database " + st.creds.database + "\n\tTotal time: " + str(elapsed_t) + " seconds\n\n")
        elif options.SOURCE:
            print("Successfully updated " + st.creds.searchSourceTable + " in database " + st.creds.database + "\n\tTotal time: " + str(elapsed_t) + " seconds\n\n")
        


if __name__ == '__main__':
    main()



