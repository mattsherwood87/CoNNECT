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
VERSION = '3.0.0'
DATE = '15 July 2024'


# ******************* PARSE COMMAND LINE ARGUMENTS ********************
#input argument parser
parser = argparse.ArgumentParser()

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

    segstatsInputFile = os.path.join(st.creds.dataDir,'code',options.PROJECT + '_compute_segstats_input.json')
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
    for k, v in vars(options).items():
        if k in ['cbf','apt','dti','T1w'] and k in segstatsInput.keys() and v:
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

    #search each raw directory
    allSegsToProcess = st.mysql_commands.sql_query(regex='aseg.mgz',searchcol='filename',progress=False,inclusion=["aparc"],exclusion=['DKTatlas','a2009s'])
    # df_fullDataMatrix = pd.read_csv(outputCsv)
    segstats_flag = False
    for idx, df_participant in df_participants.iterrows():

        #return just the subject file
        st.subject.id = str(df_participant.participant_id)
        subFilesToProcess = [x for x in allSegsToProcess if  st.subject.id in x]

        #get unique session names for this particular subject
        tmp_ls = [i.split('ses-')[1] for i in subFilesToProcess]
        tmp_ls = ['ses-' + re.split(os.sep + '|_',i)[0] for i in tmp_ls]
        tmp_np = np.array(tmp_ls)
        tmp_np = np.unique(tmp_np)
        tmp_np = np.sort(tmp_np)

        #loop over sorted sessions
        for tmp_sesNum in tmp_np:
            st.subject.sesNum = tmp_sesNum.replace('ses-','')
            filesToProcess = [x for x in subFilesToProcess if st.subject.sesNum in x]

            #should only be 1 file to process
            for f in filesToProcess:

                #loop over all provided imaging types
                for inputType in ls_inputType:

                    #loop over any files found using specified search criteria
                    inTargFiles = glob(os.path.join(st.creds.dataDir,'derivatives',st.subject.id,'ses-' + st.subject.sesNum,*segstatsInput[inputType]['regex']))
                    for inTargFile in inTargFiles:
                        outDir = os.path.join(st.creds.dataDir,'derivatives',st.subject.id, 'ses-' + st.subject.sesNum,'segstats',segstatsInput[inputType]['type'])
                        if not os.path.isdir(outDir):
                            os.makedirs(outDir)

                        outFile = inTargFile.split('.')[0] + '_fs.nii.gz'
                        if not os.path.isfile(outFile):
                            vol2volCmd = 'mri_vol2vol --mov ' + inTargFile + ' --targ ' + os.path.join(os.path.dirname(f),'T1.mgz') + ' --regheader --o ' + outFile + ' --no-save-reg'
                            os.system(vol2volCmd)
                            print('SUCCESS: moved input file to ' + os.path.join(os.path.dirname(f),'T1.mgz'))



                        if not os.path.isfile(os.path.join(outDir,os.path.basename(inTargFile).replace('.nii.gz','.dat')))or options.OVERWRITE:
                            if not options.SUBMIT:
                                os.system('mri_segstats --seg ' + f + ' --nonempty --ctab-default --in ' + outFile + ' --sum ' + os.path.join(outDir,os.path.basename(inTargFile).replace('.nii.gz','.dat')))
                            else:
                                job_segstats.add_arg('--seg ' + f + ' --nonempty --ctab-default --in ' + outFile + ' --sum ' + os.path.join(outDir,os.path.basename(inTargFile).replace('.nii.gz','.dat')))
                                segstats_flag = True
                                if options.progress:
                                    print('Added job for mri_segstats for ' + inTargFile)

        

    if segstats_flag:
        dagman.build_submit()
    

if __name__ == '__main__':
    main()
