#!/resshare/wsuconnect/python3_venv/bin/python
# the command above ^^^ sets python 3.10.10 as the interpreter for this program

# Created by Matthew Sherwood (matt.sherwood@wright.edu, matthew.sherwood.7.ctr@us.af.mil)
# Created on 27 July 2023
#
# Modified on 7 Feb 2024 - added condor job support

import os
# import pymysql
import argparse
import sys
import pandas as pd
import numpy as np
from glob import glob as glob
import datetime
from pycondor import Job, Dagman
import json
import re


#local import
REALPATH = os.path.dirname(os.path.realpath(__file__))
sys.path.append(REALPATH)
import support_tools as st


# GLOBAL INFO
#versioning
VERSION = '1.0.0'
DATE = '15 July 2024'

# ******************* PARSE COMMAND LINE ARGUMENTS ********************

#input argument parser
parser = argparse.ArgumentParser()

    #input options for main()
parser.add_argument('-p','--project', required=True, action="store", dest="PROJECT", help="update the selected project: " + ' '.join(st.creds.projects), default=None)
parser.add_argument('--cbf', action="store_true", dest="cbf", help="Compute segstats for CBF")
parser.add_argument('--apt', action="store_true", dest="apt", help="Compute segstats for APT")
parser.add_argument('--dti', action="store_true", dest="dti", help="Compute segstats for DTI")
parser.add_argument('--t1w', action="store_true", dest="T1w", help="Compute segstats for T1W")
parser.add_argument('-s', '--submit', action="store_true", dest="SUBMIT", help="Submit conversion to condor for parallel conversion", default=False)
parser.add_argument('-v', '--version', action="store_true", dest="version", help="Display the current version")
parser.add_argument('--overwrite', action="store_true", dest="OVERWRITE", help="Force segstats computation", default=False)
parser.add_argument('--progress', action="store_true", dest="progress", help="Show progress (default FALSE)", default=False)


# ******************* EVALUATE COMMAND LINE ARGUMENTS ********************
def evaluate_args(options):
    
    #SEARCHTABLE=None
    groupIdFile = None    

    if os.path.isfile(os.path.join(st.creds.dataDir,'rawdata','participants.tsv')):
        groupIdFile = os.path.join(st.creds.dataDir,'rawdata','participants.tsv')

    segstatsInputFile = os.path.join(st.creds.dataDir,'code',options.PROJECT + '_extract_segstats_input.json')
    if not os.path.isfile(segstatsInputFile):
        return

    with open(segstatsInputFile) as j:
        segstatsInput = json.load(j)


    return groupIdFile, segstatsInput



# ******************* MAIN ********************
def main():
    """
    The entry point of this program.
    """
    #read crendentials from $SCRATCH_DIR/instance_ids.json

    #get and evaluate options
    options = parser.parse_args()
    st.creds.read(options.PROJECT)
    groupIdFile, segstatsInput = evaluate_args(options)

    ls_inputType = []
    for k in options.keys():
        if k in ['cbf','apt','dti','T1w'] and k in segstatsInput.keys():
            ls_inputType.append(k)
    if not ls_inputType:
        parser.print_help()
        sys.exit()


    #do some prep for parallel processing 
    if options.SUBMIT:
        #get some precursors
        now = datetime.datetime.today().strftime('%Y%m%d_%H%M')
        base = os.path.join(st.creds.dataDir,'derivatives','processing_logs','connect_segstats')
        if not os.path.isdir(base):
            os.makedirs(base)

        #output files
        submit = os.path.join(base,'segstats_' + now + '.submit')
        error = os.path.join(base,'segstats_' + now + '.error')
        output = os.path.join(base,'segstats_' + now + '.output')
        log = os.path.join(base,'segstats_' + now + '.log')
        dagman = Dagman(name=options.PROJECT + '-segstats', submit=submit)

        job_segstats = st.create_freesurfer_condor_job('mri_segstats','mri_segstats',st.creds.machineNames,submit,error,output,log,dagman)
        segstats_flag = False

    try:
        #read participants tsv file
        df_participants = pd.read_csv(groupIdFile, sep='\t')
   
    except FileNotFoundError as e:
        print("Error Message: {0}".format(e))
        sys.exit()

    #sort participants
    df_participants.sort_values(by=['participant_id'])

    if 'discard' in df_participants.columns:
        df_participants = df_participants[~df_participants['discard']]


    for inputType in ls_inputType:
        ls_outData = ['SubjID,Session,' + ','.join(segstatsInput[inputType]['regions'])]

        #search each raw directory
        allSegsToProcess = st.mysql_commands.sql_query(regex=segstatsInput[inputType]['regex'],searchcol='filename',progress=False,inclusion='a2009s')

        for idx, df_participant in df_participants.iterrows():
            if df_participant.discard in ['YES','Yes','yes','true','True']:
                continue

            #return just the subject files
            subName = str(df_participant.participant_id)
            subFilesToProcess = [x for x in allSegsToProcess if subName in x]

            #get unique session names for this particular subject
            tmp_ls = [i.split('ses-')[1] for i in subFilesToProcess]
            tmp_ls = ['ses-' + re.split(os.sep + '|_',i)[0] for i in tmp_ls]
            tmp_np = np.array(tmp_ls)
            tmp_np = np.unique(tmp_np)
            tmp_np = np.sort(tmp_np)

            #loop over sorted sessions
            for tmp_sesNum in tmp_np:
                sesNum = tmp_sesNum.replace('ses-','')
                filesToProcess = [x for x in subFilesToProcess if sesNum in x]

                #should only be 1 file to process
                for f in filesToProcess:

                    #loop over any files found using specified search criteria
                    data = np.loadtxt(f, comments='#', delimiter="\t") #Index SegId NVoxels Volume_mm3 StructName Mean StdDev Min Max Range 
                    subOutData_mean = subName + ',' + sesNum

                    for region in segstatsInput[inputType]['regions']:
                        for row in data:
                            if row[5] is region:
                                subOutData_mean = subOutData_mean + ',' + row[6]
                                
                            

            

       
    

if __name__ == '__main__':
    main()
