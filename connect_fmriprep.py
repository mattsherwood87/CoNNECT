#!/resshare/wsuconnect/python3_venv/bin/python
# the command above ^^^ sets python 3.10.10 as the interpreter for this program

# Created by Matthew Sherwood (matt.sherwood@wright.edu, matthew.sherwood.7.ctr@us.af.mil)
# Created on 28 Dec 2020
#
# v2.0.0 on 1 April 2023
# v1.1.2  on 25 Oct 2021 Modification (1.1.2) - add inclusion of *_dcm2nii_input.json for input parameters
# v1.1.1 on 16 Sept 2021 Modification (1.1.1) - remove checking local scratch disk for output using glob: unncessary with direct s3 mount
# v1.1.0 11 Jan 2021 Modification (1.1.0)- add utilization of instance_ids.json

import os
import argparse
from pycondor import Dagman
import datetime
import sys
import json
import pandas as pd
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 


#local import
REALPATH = os.path.realpath(__file__)

sys.path.append(os.path.dirname(REALPATH))
import support_tools as st


# GLOBAL INFO
#versioning
VERSION = '2.1.0'
DATE = '14 Nov 2024'



# ******************* PARSE COMMAND LINE ARGUMENTS ********************
parser = argparse.ArgumentParser("This program is the batch wrapper command to perform DICOM to NIfTI conversion using fmriprep. The program searches the specified project's searchSourceTable for acquisition folders (acq-*) which contain DICOM images and runs wsuconnect.support_tools.convert_dicoms for each returned directory.")
parser.add_argument('-p','--project', required=True, action="store", dest="PROJECT", help="update the selected project: " + ' '.join(st.creds.projects))
parser.add_argument('--overwrite', action="store_true", dest="OVERWRITE", help="Force conversion by skipping directory and database checking", default=False)
# parser.add_argument('--docker', action="store_true", dest="DOCKER", help="Submit conversion to HTCondor and process in wsuconnect/neuro docker container [default=False]", default=False)
parser.add_argument('-s', '--submit', action="store_true", dest="SUBMIT", help="Submit conversion to condor for parallel conversion", default=False)
parser.add_argument('-v', '--version', action="store_true", dest="version", help="Display the current version")
parser.add_argument('--progress', action="store_true", dest="progress", help="Show progress (default FALSE)", default=False)


# ******************* MAIN ********************
def main():
    """
    The entry point of this program.
    """
    #read crendentials from $SCRATCH_DIR/instance_ids.json
    ls_updatedFiles = []
    ls_existingFiles = []

    #get and evaluate options
    options = parser.parse_args()
    
    if options.version:
        print('connect_dcm2nii.py version {0}.'.format(VERSION)+" DATED: "+DATE)

    
    st.creds.read(options.PROJECT)

    inputJson = os.path.join(st.creds.dataDir,'code',st.creds.project + '_fmriprep_input.json')
    with open(inputJson) as j:
        inputParams = json.load(j)

    now = datetime.datetime.today().strftime('%Y%m%d_%H%M')
    if options.SUBMIT:

        #splitDirs = source_dirsToProcess[0].split('/')
        base = os.path.join(st.creds.dataDir,'derivatives','processing_logs','connect_fmriprep')
        # base = base.replace(creds.s3_prefix + '/','')
        if not os.path.isdir(base):
            os.makedirs(base)

        #output files
        submit = os.path.join(base,'fmriprep_' + now + '.submit')
        error = os.path.join(base,'fmriprep_' + now + '.error')
        output = os.path.join(base,'fmriprep_' + now + '.output')
        log = os.path.join(base,'fmriprep_' + now + '.log')
        dagman = Dagman(name=options.PROJECT + '-fmriprep', submit=submit)

        job_fmriprep = st.create_python_venv_condor_job('fmriprep',
                                                    'fmriprep-docker',
                                                    st.creds.machineNames,
                                                    submit,
                                                    error,
                                                    output,
                                                    log,
                                                    dagman)


    # # finds all subject directories to analyze
    # raw_dirsToProcess = st.mysql_commands.sql_query_dirs(regex='sub-',source=False,inclusion=['rawdata'])
    # new_d =[]
    # for d in raw_dirsToProcess:
    #     a = d.removeprefix(st.creds.dataDir).split(os.path.sep)
    #     new_d.append(os.path.join(st.creds.dataDir,a[1],a[2]))

    # raw_dirsToProcess = list(set(new_d))

    inputTsv = os.path.join(st.creds.dataDir,'rawdata','participants.tsv')
    with open(inputTsv) as f:
        df_participants = pd.read_csv(f,delimiter='\t')


    if 'discard' in df_participants.columns:
        df_participants = df_participants[~df_participants['discard']]
 
    
    for index, row in df_participants.iterrows():
        
        #here
 

        filter_file = '/resshare19/projects/2023_UES/EPIC/rawdata/bids_filter.json'
        str_args = ' '.join([
            os.path.join(st.creds.dataDir,'rawdata'),
            os.path.join(st.creds.dataDir,'derivatives'),
            '--participant-label', row['participant_id'].split('sub-')[-1],
            '--bids-filter-file', filter_file,
            '--longitudinal',
            '--skull-strip-t1w', 'force',
            '--output-spaces', 'fsnative','MNI152NLin2009cAsym:res-2', 'T1w',
            '--nthreads','1',
            '--mem-mb','5000',
            '--fs-license-file', '/resshare/wsuconnect/.license/.license',
            '--no-tty','--skip_bids_validation',
            '-w', os.path.join(st.creds.dataDir,'fmriprep_work')
        ])

        if not options.SUBMIT:
            #do something
            os.system('fmriprep-docker ' + str_args)
        else:
            job_fmriprep.add_arg(str_args)
            if options.progress:
                print('Added job for fmriprep-docker for participant ' + row['participant_id'].split('sub-')[-1])  

        
    if options.SUBMIT:
        # job_sleep.add_child(job_dcm2nii)
        # job_dcm2nii.add_child(job_stop) - Can I force this requirement on the MASTER?
        dagman.build_submit()

        #write conversion lists to file
        print('\n\n fmriprep-docker submitted to condor')
    else:
        print('\n\n all commands are now complete, please check')
    

if __name__ == '__main__':
    main()
