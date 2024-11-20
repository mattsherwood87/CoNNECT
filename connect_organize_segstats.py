#!/resshare/general_processing_codes/python3_venv/bin/python
# the command above ^^^ sets python 3.10.10 as the interpreter for this program

# Created by Matthew Sherwood (matt.sherwood@wright.edu, matthew.sherwood.7.ctr@us.af.mil)
# Created on 28 Dec 2020
#
# Modified on 17 April 2023 - update to WSU implementatttion
# Last Modified on 11 Jan 2021 - add utilization of instance_ids.json

import os
# import pymysql
import argparse
import sys
import csv
import pandas as pd
import numpy as np


#local import
REALPATH = os.path.dirname(os.path.realpath(__file__))
sys.path.append(REALPATH)
from helper_functions.mysql_commands import *
from helper_functions.read_credentials import *
from helper_functions.create_python_condor_job import *
from helper_functions.bids_commands import *
from helper_functions.id_check import id_check

from classes.creds import *


# GLOBAL INFO
#versioning
VERSION = '2.0.0'
DATE = '17 April 2023'

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
        else:
            print('connect_rawdata_check.py version {0}.'.format(VERSION)+" DATED: "+DATE)
        sys.exit()

    return options


# ******************* EVALUATE COMMAND LINE ARGUMENTS ********************
def evaluate_args(options):
    
    #SEARCHTABLE=None
    groupIdFile = None    


    if os.path.isfile(os.path.join(creds.dataDir,'code',options.PROJECT + '_scan_id.json')):
        scanIdFile = os.path.join(creds.dataDir,'code',options.PROJECT + '_scan_id.json')

    if os.path.isfile(os.path.join(creds.dataDir,'rawdata','participants.tsv')):
        groupIdFile = os.path.join(creds.dataDir,'rawdata','participants.tsv')


    return scanIdFile, groupIdFile



# ******************* MAIN ********************
def main():
    """
    The entry point of this program.
    """
    #read crendentials from $SCRATCH_DIR/instance_ids.json

    #get and evaluate options
    options = parse_arguments()
    read_credentials(options.PROJECT)
    scanIdFile, groupIdFile = evaluate_args(options)

    try:
        #read scan ids
        with open(scanIdFile) as j:
            scanIds = json.load(j)
            if '__general_comment__' in scanIds.keys():
                scanIds.pop('__general_comment__')

        #read participants tsv file
        df_participants = pd.read_csv(groupIdFile, sep='\t')
   
    except FileNotFoundError as e:
        print("Error Message: {0}".format(e))
        sys.exit()

    #sort participants
    df_participants.sort_values(by=['participant_id'])

    #write csv header
    base_outputCsv = os.path.join(creds.dataDir,'derivatives','recon-all_ants-RJ',options.PROJECT)
    if not os.path.isdir(os.path.dirname(base_outputCsv)):
        os.makedirs(os.path.dirname(base_outputCsv))

    #search each raw directory
    segstatsCSV = os.path.join(creds.dataDir,'derivatives','recon-all_ants-RJ','CorticalMeasuresENIGMA_ThickAvg.csv')
    df_combinedCSV = pd.read_csv(segstatsCSV,sep=',',index_col=False)
    df_newCombined = pd.DataFrame()


    # df_fullDataMatrix = pd.read_csv(outputCsv)
    for subName in df_participants.participant_id:

        #return just the subject files
        if type(subName) is int:
            subName = str(subName)

        if df_participants[df_participants['participant_id'] == subName].discard.item():
            continue
        df_sub = df_combinedCSV[df_combinedCSV['SubjID'].str.contains(subName)]
        # if len(df_sub) != 3:
        #     continue

        # loop over all the rows in the subject dataframe
        count = 1
        origCols = list(df_sub.columns)[1:]

        # df_newSub = pd.DataFrame(columns=['SubjID'] + [x + '-1' for x in origCols] + [x + '-2' for x in origCols] + [x + '-3' for x in origCols])
        df_newSub = pd.DataFrame([subName], columns=['SubjID'])

        for index, row in df_sub.iterrows():
            sesDate = row.loc['SubjID'].split('ses-')[1].split('-')[0]
            sesNum = row.loc['SubjID'].split('ses-')[1].split('-')[1].split('_')[0]

            
            if 'run-' in row.loc['SubjID']:
                runNum = row.loc['SubjID'].split('run-')[1].split('-')
                if len(runNum) > 0:
                    runNum = runNum[0]
                    newCols = [x + '_ses-' + getattr(df_participants[df_participants['participant_id'] == subName], 'ses-' + str(sesNum) + '_condition').item() + '_run-' + str(runNum) for x in origCols]
                    cDict = {origCols[i]: newCols[i] for i in range(len(origCols))}
                    row.rename(cDict,inplace=True)
                    row.drop(labels='SubjID',inplace=True)
                    df_tmp = pd.DataFrame([row.values.tolist()],columns=row.keys().tolist())
                    df_newSub = df_newSub.join(df_tmp)

                else:
                    newCols = [x + '_ses-' + str(sesNum) for x in origCols]
                    cDict = {origCols[i]: newCols[i] for i in range(len(origCols))}
                    row.rename(cDict,inplace=True)
                    row.drop(labels='SubjID',inplace=True)
                    df_tmp = pd.DataFrame([row.values.tolist()],columns=row.keys().tolist())
                    df_newSub = df_newSub.join(df_tmp)

            else:
                newCols = [x + '_ses-' + str(sesNum) for x in origCols]
                cDict = {origCols[i]: newCols[i] for i in range(len(origCols))}
                row.rename(cDict,inplace=True)
                row.drop(labels='SubjID',inplace=True)
                df_tmp = pd.DataFrame([row.values.tolist()],columns=row.keys().tolist())
                df_newSub = df_newSub.join(df_tmp)

            count = count + 1


        #combine complete subject dataframe with output dataframe
        if df_newCombined.empty:
            df_newCombined = df_newSub
        else:
            df_newCombined = pd.concat([df_newCombined,df_newSub],ignore_index=True)

    #prepare output CSV files
    for k in origCols:
        regionCols = [col for col in df_newCombined.columns if k in col]
        df_tmp = df_newCombined[['SubjID'] + regionCols].copy()
        df_tmp.to_csv(base_outputCsv + '_' + k + '.csv',mode='w', index=False, header=True)
            
            


            # df_dataMatrix = pd.DataFrame(d_dataMatrix, index=[0])
            # #write dataframe to csv
            # if os.path.isfile(outputCsv):
            #     df_dataMatrix.to_csv(outputCsv, mode='a', index=False, header=False)
            # else:
            #     df_dataMatrix.to_csv(outputCsv, mode='a', index=False)

    print('SUCCESS: output saved to ' + base_outputCsv)

        

    
    

if __name__ == '__main__':
    main()
