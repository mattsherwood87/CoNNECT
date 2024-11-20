#!/resshare/general_processing_codes/python3_venv/bin/python
# the command above ^^^ sets python 3.11.11 as the interpreter for this program

# Created by Matthew Sherwood (matt.sherwood@wright.edu, matthew.sherwood.7.ctr@us.af.mil)
# Created on 21 Jan 2021
#
# Modified on 5 Aug 2024 - modified database query - input bids labels are now split and utilized as inidividual inclusion items
# Modified on 23 May 2023 - updated to WSU implementation
# Modified on 9 Nov 2021 - added logs support in struc_flirt and asl_2d_flirt
# Modified on 21 Jan 2021 

import os
from numpy.core.numeric import convolve
import argparse
from pycondor import Job, Dagman
import datetime
import sys


#local import

REALPATH = os.path.realpath(__file__)
sys.path.append(os.path.dirname(REALPATH))
from helper_functions.bids_commands import *
from helper_functions.get_dir_identifiers import *
from helper_functions.read_credentials import *
from helper_functions.flirt_pngappend import *
from helper_functions.mysql_commands import *
from helper_functions.create_fsl_condor_job import *
from helper_functions.create_python_condor_job import *
from helper_functions.flirt import *

from classes.creds import *


# GLOBAL INFO
#versioning
VERSION = '2.0.2'
DATE = '5 Aug 2024'
FSLDIR = os.environ["FSLDIR"]
STD1MM = os.path.join(FSLDIR,'data','standard','MNI152_T1_1mm.nii.gz')
STD1MM_BRAIN = os.path.join(FSLDIR,'data','standard','MNI152_T1_1mm_brain.nii.gz')
STD2MM = os.path.join(FSLDIR,'data','standard','MNI152_T1_2mm.nii.gz')
STD2MM_BRAIN = os.path.join(FSLDIR,'data','standard','MNI152_T1_2mm_brain.nii.gz')

#input argument parser
parser = argparse.ArgumentParser()

# ******************* PARSE COMMAND LINE ARGUMENTS ********************
def parse_arguments():

    #input options for main()
    requiredNamed = parser.add_argument_group('required arguments')
    requiredNamed.add_argument('-p','--project', action="store", dest="PROJECT", help="Perform FLIRT for the selected project: " + ' '.join(creds.projects), default=None)

    parser.add_argument('--asl', action="store_true", dest="ASL", help="Perform registration between ASL and structural (and standard if structural to standard exists", default=False)
    parser.add_argument('--struc', action="store_true", dest="STRUC", help="Perform registration between structural and standard (MNI T1 2mm)", default=False)
    parser.add_argument('--apt', action="store_true", dest="APT", help="Perform registration between APT and structural (and standard if structural to standard exists", default=False)

    parser.add_argument('--overwrite', action="store_true", dest="OVERWRITE", help="Force conversion by skipping directory and database checking", default=False)
    parser.add_argument('-s', '--submit', action="store_true", dest="SUBMIT", help="Submit conversion to condor for parallel conversion", default=False)
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



def modality_process(modality,options,*args,**kwargs):
    flirt_flag = kwargs.get('flag',False)
    job_flirt = kwargs.get('job',None)
    threadCount = kwargs.get('count',0)
    submit = kwargs.get('submit',None)
    error = kwargs.get('error',None)
    output = kwargs.get('output',None)
    log = kwargs.get('log',None)
    dagman = kwargs.get('dagman',None)

    #load parameter JSON control file
    try:
        flirtInputFile = os.path.join(creds.dataDir,'code',options.PROJECT + '_' + modality + '_flirt_input.json')
        if not os.path.isfile(os.path.join(creds.dataDir,'code',options.PROJECT + '_' + modality + '_flirt_input.json')):
            return

        with open(flirtInputFile) as j:
            flirtInput = json.load(j)

            #asl sql_query inputs
            incExcDict = {}
            if 'inclusion_list' in flirtInput:
                incExcDict['inclusion'] = flirtInput.pop('inclusion_list')
            if 'exclusion_list' in flirtInput:
                incExcDict['exclusion'] = flirtInput.pop('exclusion_list')

            #identifier for bet
            betInputFile = None
            if 'bet' in flirtInput:
                if os.path.isfile(os.path.join(creds.dataDir,'code',options.PROJECT + '_' + modality + '_bet_input.json')):
                    betInputFile = os.path.join(creds.dataDir,'code',options.PROJECT + '_' + modality + '_bet_input.json')

    except FileNotFoundError as e:
        print("Error Message: {0}".format(e))
        sys.exit()

    regexStr = get_bids_filename(**flirtInput['main_image_params']['input_bids_labels']).split('_')
    incExcDict['inclusion'] += regexStr[2:]

    if not incExcDict:
        filesToProcess = sql_query(database=creds.database,searchtable=creds.searchTable,searchcol='fullpath',regex=regexStr[1],progress=False)
    else:
        filesToProcess = sql_query(database=creds.database,searchtable=creds.searchTable,searchcol='fullpath',regex=regexStr[1],**incExcDict,progress=False)

    # loop throught files
    filesToProcess.sort()
    job_flag = True
    for f in filesToProcess:

        #run job on condor
        if options.SUBMIT:
            #create condor job
            if not job_flirt:
                job_flirt = create_python_condor_job(modality + '_flirt','flirt.py',creds.machineNames,submit,error,output,log,dagman)

            subName, sesNum = get_dir_identifiers(os.path.dirname(f))
            # if glob(os.path.join(creds.dataDir, 'derivatives', 'sub-' + subName, 'ses-' + sesNum, 'flirt', modality,'*.mat')) and not options.OVERWRITE:
            #     if options.progress:
            #         print('WARNING: Output files found in ' + os.path.join(creds.dataDir, 'derivatives', 'sub-' + subName, 'ses-' + sesNum, 'flirt', modality))
            #         print('\toverwrite not specified, skipping')
            
            #     if f in filesToProcess[-1]:
            #         return threadCount, flirt_flag, job_flirt, dagman
            #     else:
            #         continue
            # else:
            # if options.progress:
            #     print('Preparing Job: Output files not found in ' + os.path.join(creds.dataDir, 'derivatives', 'sub-' + subName, 'ses-' + sesNum, 'flirt', modality))


            #create argument string
            argStr = (f + ' ' + 
                    creds.dataDir + ' ' +
                    flirtInputFile)
            if options.OVERWRITE:
                argStr += ' --overwrite'
            if options.progress:
                argStr += ' --progress'
            if betInputFile:
                argStr += ' --bet-params ' + betInputFile

            #add arguments to condor job
            job_flirt.add_arg(argStr)# + ' > ' + os.path.join(creds.s3_dir,s3_outLog))
            print('Added job for ' + modality + ' registration for ' + f)
            flirt_flag = True

            # if threadCount == 20:

            #     dagman.build_submit()
            #     threadCount = 0
            #     job_flag = True
                
            #     #get some precursors
            #     now = datetime.datetime.today().strftime('%Y%m%d_%H%M')
            #     base = os.path.join(creds.dataDir,'derivatives','processing_logs','connect_flirt')
            #     if not os.path.isdir(base):
            #         os.makedirs(base)

            #     #output files
            #     submit = os.path.join(base,'flirt_' + now + '.submit')
            #     error = os.path.join(base,'flirt_' + now + '.error')
            #     output = os.path.join(base,'flirt_' + now + '.output')
            #     log = os.path.join(base,'flirt_' + now + '.log')
            #     dagman = Dagman(name=options.PROJECT + '-flirt', submit=submit)
            # else:
            threadCount += 1
            
            if f in filesToProcess[-1]:
                return threadCount, flirt_flag, job_flirt, dagman

        else:
            flirt(f,creds.dataDir,flirtInputFile,overwrite=options.OVERWRITE,bet_params=betInputFile,progress=options.progress)



# ******************* MAIN ********************
def main():
    """
    The entry point of this program.
    """
    #read credentials from $SCRATCH_DIR/instance_ids.json

    #get and evaluate options
    options = parse_arguments()
    read_credentials(options.PROJECT)
    flirt_flag_struc = False
    flirt_flag_asl = False
    flirt_flag_apt = False
    job_flirt_struc = None
    job_flirt_asl = None
    job_flirt_apt = None

    #do some prep for parallel processing 
    if options.SUBMIT:
        #get some precursors
        now = datetime.datetime.today().strftime('%Y%m%d_%H%M')
        base = os.path.join(creds.dataDir,'derivatives','processing_logs','connect_flirt')
        if not os.path.isdir(base):
            os.makedirs(base)

        #output files
        submit = os.path.join(base,'flirt_' + now + '.submit')
        error = os.path.join(base,'flirt_' + now + '.error')
        output = os.path.join(base,'flirt_' + now + '.output')
        log = os.path.join(base,'flirt_' + now + '.log')
        dagman = Dagman(name=options.PROJECT + '-flirt', submit=submit)


        #perform struc 2 standard registration
        threadCount = 0
        if options.STRUC:
            threadCount,flirt_flag_struc,job_flirt_struc,dagman = modality_process('struc',options,flag=flirt_flag_struc,job=job_flirt_struc,count=threadCount,submit=submit,error=error,output=output,log=log,dagman=dagman)
        if options.ASL:
            threadCount,flirt_flag_asl,job_flirt_asl,dagman = modality_process('asl',options,flag=flirt_flag_asl,job=job_flirt_asl,count=threadCount,submit=submit,error=error,output=output,log=log,dagman=dagman)
        if options.APT:
            threadCount,flirt_flag_apt,job_flirt_apt,dagman = modality_process('apt',options,flag=flirt_flag_apt,job=job_flirt_apt,count=threadCount,submit=submit,error=error,output=output,log=log,dagman=dagman)
    else:

        if options.STRUC:
            modality_process('struc',options)
        if options.ASL:
            modality_process('asl',options)
        if options.APT:
            modality_process('apt',options)

    


    if options.SUBMIT and dagman:
        if flirt_flag_struc and flirt_flag_asl:
            job_flirt_struc.add_child(job_flirt_asl)
        if flirt_flag_struc and flirt_flag_apt:
            job_flirt_struc.add_child(job_flirt_apt)

        if flirt_flag_struc or flirt_flag_asl or flirt_flag_apt:
            dagman.build_submit()
    

if __name__ == '__main__':
    main()
