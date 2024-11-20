#!/resshare/wsuconnect/python3_venv/bin/python
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
import json


#local import
REALPATH = os.path.dirname(os.path.realpath(__file__))
sys.path.append(REALPATH)

import support_tools as st


# GLOBAL INFO
#versioning
VERSION = '2.0.0'
DATE = '17 April 2023'


# ******************* PARSE COMMAND LINE ARGUMENTS ********************
#input argument parser
parser = argparse.ArgumentParser()
parser.add_argument('-p','--project', required=True, action="store", dest="PROJECT", help="update the selected project: " + ' '.join(st.creds.projects), default=None)
#parser.add_argument('--overwrite', action="store_true", dest="OVERWRITE", help="Force conversion by skipping directory and database checking", default=False)
#parser.add_argument('-l', '--load', action="store_true", dest="DOWNLOAD", help="Download files to local disk if they do not exist", default=False)
#parser.add_argument('-s', '--submit', action="store_true", dest="SUBMIT", help="Submit conversion to condor for parallel conversion", default=False)
parser.add_argument('-v', '--version', action="store_true", dest="version", help="Display the current version")
parser.add_argument('--progress', action="store_true", dest="progress", help="Show progress (default FALSE)", default=False)
 


# ******************* EVALUATE COMMAND LINE ARGUMENTS ********************
def evaluate_args(options):
    
    #SEARCHTABLE=None
    groupIdFile = None    


    if os.path.isfile(os.path.join(st.creds.dataDir,'code',options.PROJECT + '_derivatives_input.json')):
        scanIdFile = os.path.join(st.creds.dataDir,'code',options.PROJECT + '_derivatives_input.json')

    if os.path.isfile(os.path.join(st.creds.dataDir,'rawdata','participants.tsv')):
        groupIdFile = os.path.join(st.creds.dataDir,'rawdata','participants.tsv')


    return scanIdFile, groupIdFile



# ******************* MAIN ********************
def main():
    """
    The entry point of this program.
    """
    #read crendentials from $SCRATCH_DIR/instance_ids.json

    #get and evaluate options
    options = parser.parse_args()
    st.creds.read(options.PROJECT)
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

    if 'discard' in df_participants.columns:
        df_participants = df_participants[~df_participants['discard']]

    #write csv header
    outputCsv = os.path.join(st.creds.dataDir,'derivatives','processing_logs',options.PROJECT + '_derivatives_check.csv')
    if not os.path.isdir(os.path.dirname(outputCsv)):
        os.makedirs(os.path.dirname(outputCsv))
    else:
        if os.path.isfile(outputCsv):
            os.remove(outputCsv)

    #search each raw directory
    allFilesToProcess = st.mysql_commands.sql_query(regex='derivatives',searchtable=st.creds.searchTable,searchcol='fullpath',progress=False,exclusion=['hr\.tif','lr\.tif'])
    # df_fullDataMatrix = pd.read_csv(outputCsv)
    for subName in df_participants.participant_id:

        #return just the subject files
        if type(subName) is int:
            subName = str(subName)

        subFilesToProcess = [x for x in allFilesToProcess if subName in x]

        #get unique session names for this particular subject
        tmp_ls = [i.split('ses-')[1] for i in subFilesToProcess]
        tmp_ls = ['ses-' + i.split(os.sep)[0] for i in tmp_ls]
        tmp_np = np.array(tmp_ls)
        tmp_np = np.unique(tmp_np)
        tmp_np = np.sort(tmp_np)

        #loop over sorted sessions
        for sesNum in tmp_np:
            filesToProcess = [x for x in subFilesToProcess if sesNum in x]
            d_dataMatrix = {}
            d_dataMatrix['participant_id'] = subName
            d_dataMatrix['session'] = sesNum
            # d_dataMatrix['group'] = 

            #look for raw nifti's
            for k in scanIds:
                if 'sessions' in scanIds[k].keys():
                    if sesNum.split('-')[-1] not in scanIds[k]['sessions']:
                        d_dataMatrix[k] = np.NaN
                        continue
                scanNames = scanIds[k]['files']

                match = False
                for scanName in scanNames:
                    
                    if 'inclusion_list' in scanIds[k].keys():
                        tmp_match = [x for x in filesToProcess if scanName in x and [y for y in scanIds[k]['inclusion_list'] if y in x]]
                    else:
                        tmp_match = [x for x in filesToProcess if scanName in x]

                    if len(tmp_match) > 0:
                        match = True
                    else:
                        match = False
                        break

                
                if match:
                    d_dataMatrix[k] = 1
                else:
                    d_dataMatrix[k] = 0

            
            df_dataMatrix = pd.DataFrame(d_dataMatrix, index=[0])
            #write dataframe to csv
            if os.path.isfile(outputCsv):
                df_dataMatrix.to_csv(outputCsv, mode='a', index=False, header=False)
            else:
                df_dataMatrix.to_csv(outputCsv, mode='a', index=False)

    print('SUCCESS: output saved to ' + outputCsv)

        

    
    

if __name__ == '__main__':
    main()
