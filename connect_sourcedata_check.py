#!/resshare/general_processing_codes/python3_venv/bin/python
# the command above ^^^ sets python 3.10.10 as the interpreter for this program

# Created by Matthew Sherwood (matt.sherwood@wright.edu, matthew.sherwood.7.ctr@us.af.mil)
# Created on 28 Dec 2020
#
# Modified on 17 April 2023 - update to WSU implementation
# Last Modified on 11 Jan 2021 - add utilization of instance_ids.json

import os
import pymysql
import argparse
import sys
import csv
import pandas as pd


#local import
REALPATH = os.path.dirname(os.path.realpath(__file__))
sys.path.append(REALPATH)
from helper_functions.convert_dicoms import convert_dicoms
from helper_functions.mysql_commands import *
from helper_functions.get_dir_identifiers import *
from helper_functions.read_credentials import *
from helper_functions.create_python_condor_job import *

from classes.creds import *


# GLOBAL INFO
#versioning
VERSION = '2.0.0'
DATE = '17 Apr 2023'

#input argument parser
parser = argparse.ArgumentParser()

# ******************* PARSE COMMAND LINE ARGUMENTS ********************
def parse_arguments():

    #input options for main()
    requiredNamed = parser.add_argument_group('required arguments')
    requiredNamed.add_argument('-p','--project', action="store", dest="PROJECT", help="update the selected project: " + ' '.join(creds.projects), default=None)
    #parser.add_argument('--overwrite', action="store_true", dest="OVERWRITE", help="Force conversion by skipping directory and database checking", default=False)
    #parser.add_argument('-l', '--load', action="store_true", dest="DOWNLOAD", help="Download files to local disk if they do not exist", default=False)
    #parser.add_argument('-s', '--submit', action="store_true", dest="SUBMIT", help="Submit conversion to condor for parallel conversion", default=False)
    parser.add_argument('-v', '--version', action="store_true", dest="version", help="Display the current version")
    parser.add_argument('--progress', action="store_true", dest="progress", help="Show progress (default FALSE)", default=False)
    options = parser.parse_args()

    #determine the search table and search string
    if not options.PROJECT in creds.projects:
        if not options.version:
            print("ERROR: user must define a project using [-p|--project <project>]\n\n")
            parser.print_help()
        sys.exit()

    return options


# ******************* EVALUATE COMMAND LINE ARGUMENTS ********************
def evaluate_args(options):
    
    #SEARCHTABLE=None
    groupIdFile = None

    #print version if requested
    if options.version:
        print('connect_sourcedata_check.py version {0}.'.format(VERSION)+" DATED: "+DATE)

    #get participants.tsv file
    if os.path.isfile(os.path.join(creds.dataDir,'rawdata','participants.tsv')):
        groupIdFile = os.path.join(creds.dataDir,'rawdata','participants.tsv')

    return groupIdFile



# ******************* MAIN ********************
def main():
    """
    The entry point of this program.
    """

    #get and evaluate options
    options = parse_arguments()
    read_credentials(options.PROJECT)
    groupIdFile = evaluate_args(options)

    try:
        df_participants = pd.read_csv(groupIdFile,sep='\t')
   
    except FileNotFoundError as e:
        print("Error Message: {0}".format(e))
        sys.exit()


    #query mysql sourcedata table and return a list of directories which contain files with creds.dicom_id in the filename
    dirsToProcess = sql_query_dirs(creds.dicom_id,creds,True)
    dirsToProcess.sort()


    #write csv header
    outputCsv = os.path.join(creds.dataDir,'processing_logs',options.PROJECT + '_sourcedata_check.csv')
    if not os.path.isdir(os.path.dirname(outputCsv)):
        os.makedirs(os.path.dirname(outputCsv))
    with open(outputCsv,'w') as csvFile:
        csvWriter = csv.writer(csvFile,delimiter=',')
        csvWriter.writerow(['SUBJECT','SESSION','GROUP'])

    #search each source directory
    for singleDir in dirsToProcess:

        #check output_dir for niftis on both sql db (processed_data) and local dir (optional override flag)
        subjectName,sessionNum = get_dir_identifiers(singleDir) #get subject name from filename

        #write csv table


        d = {}
        d['SUBJECT'] = subjectName
        d['SESSION'] = sessionNum
        df_sub = df_participants[df_participants['participant_id'] == subjectName]
        if not df_sub.empty:
            d['GROUP'] = df_sub.group.values[0]
        else:
            d['GROUP'] = 'NONE'




        outputCsv = os.path.join(creds.dataDir,'processing_logs',options.PROJECT + '_sourcedata_check.csv')
        with open(outputCsv,'a') as csvFile:
            csvWriter = csv.writer(csvFile,delimiter=',')
            df_sub = df_participants[df_participants['participant_id'] == subjectName]
            if not df_sub.empty:
                csvWriter.writerow([subjectName,sessionNum,df_sub.group.values[0]])
            else:
                csvWriter.writerow([singleDir,sessionNum," "])
    

if __name__ == '__main__':
    main()
