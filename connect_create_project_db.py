#!/resshare/general_processing_codes/python3_venv/bin/python
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
from helper_functions.mysql_commands import *
from helper_functions.read_credentials import *
from classes.creds import *

# GLOBAL INFO
#versioning
VERSION = '2.0.0'
DATE = '1 April 2023'

#input argument parser
parser = argparse.ArgumentParser(os.path.basename(REALPATH) + ' - Create MySQL Tables in CoNNECT Database')

# ******************* PARSE COMMAND LINE ARGUMENTS ********************
def parse_arguments():
    
    requiredNamed = parser.add_argument_group('required arguments')
    requiredNamed.add_argument('-p','--project', action="store", dest="PROJECT", help="update the selected table: " + ' '.join(creds.projects), default=None)
    # parser.add_argument('-r','--raw', action="store_true", dest="RAW", help="Command line argument to update the raw_data table for the selected project (default FALSE)", default=False)
    parser.add_argument('-v', '--version', help="Display the current version", action="store_true", dest="version")
    parser.add_argument('--progress', help="Show progress (default FALSE)", action="store_true", dest="progress", default=False)
    options = parser.parse_args()

    #determine the search table and search string
    if not options.PROJECT in creds.projects:
        if not options.version:
            print("ERROR: user must define a project using [-p|--project <project>]\n\n")
            parser.print_help()
        sys.exit()

    return options


# ******************* SORT REQUESTED TABLES ********************
def evaluate_args(options):

    #print version if selected
    if options.version:
        print(os.path.basename(REALPATH) + ' version {0}.'.format(VERSION)+" DATED: "+DATE)


# *******************  MAIN  ********************    
def main():
    """
    The entry point of this program.
    """
    options = parse_arguments()
    evaluate_args(options)

    print('Creating MySQL tables on ' + datetime.datetime.today().strftime('%Y%m%d @ %H:%M:%S'))


    #create tables
    read_credentials(options.PROJECT)
    sql_create_project_tables()
    print("\nSuccessfully created tables " + creds.searchTable + " & " + creds.searchSourceTable + " in database " + creds.database)        


if __name__ == '__main__':
    main()



