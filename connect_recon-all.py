#!/resshare/general_processing_codes/python3_venv/bin/python
# the command above ^^^ sets python 3.10.9 as the interpreter for this program

# Created by Matthew Sherwood (matt.sherwood@wright.edu, matthew.sherwood.7.ctr@us.af.mil)
# Created on 22 July 2023
#
# Modified on

import os
import argparse
from pycondor import Job, Dagman
import datetime
import sys
from glob import glob as glob

#local import

REALPATH = os.path.realpath(__file__)
sys.path.append(os.path.dirname(REALPATH))
from helper_functions.bids_commands import *
from helper_functions.get_dir_identifiers import *
from helper_functions.read_credentials import *
from helper_functions.mysql_commands import *
from helper_functions.create_fsl_condor_job import *
from helper_functions.create_python_condor_job import *
from helper_functions.fsreconall_stage1 import fsreconall_stage1
from helper_functions.fsreconall_stage2 import fsreconall_stage2

from classes.creds import *


# GLOBAL INFO
#versioning
VERSION = '1.0.1'
DATE = '22 July 2023'
FSLDIR = os.environ["FSLDIR"]

#input argument parser
parser = argparse.ArgumentParser()

# ******************* PARSE COMMAND LINE ARGUMENTS ********************
def parse_arguments():

    #input options for main()
    requiredNamed = parser.add_argument_group('required arguments')
    requiredNamed.add_argument('-p','--project', action="store", dest="PROJECT", help="Perform FreeSurfer recon-all and/or recon-all refinement for the selected project: " + ' '.join(creds.projects), default=None)

    parser.add_argument('--stage1', action="store_true", dest="STAGE1", help="only perform recon-all without brainmask refinement", default=False)
    parser.add_argument('--stage2', action="store_true", dest="STAGE2", help="perform brainmask refinement", default=False)
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



# ******************* Setup Main Processing ********************
def prepare_pipeline(options,*args,**kwargs):
    submit = kwargs.get('submit',None)
    error = kwargs.get('error',None)
    output = kwargs.get('output',None)
    log = kwargs.get('log',None)
    dagman = kwargs.get('dagman',None)

    #load parameter JSON control file
    try:
        reconallInputFile = os.path.join(creds.dataDir,'code',options.PROJECT + '_freesurfer_recon-all_input.json')
        if not os.path.isfile(os.path.join(creds.dataDir,'code',options.PROJECT + '_freesurfer_recon-all_input.json')):
            return

        with open(reconallInputFile) as j:
            reconallInput = json.load(j)

            #asl sql_query inputs
            incExcDict = {}
            if 'inclusion_list' in reconallInput:
                incExcDict['inclusion'] = reconallInput.pop('inclusion_list')
            if 'exclusion_list' in reconallInput:
                incExcDict['exclusion'] = reconallInput.pop('exclusion_list')

    except FileNotFoundError as e:
        print("Error Message: {0}".format(e))
        sys.exit()

    regexStr = get_bids_filename(**reconallInput['main_image_params']['input_bids_labels'])

    if not incExcDict:
        filesToProcess = sql_query(database=creds.database,searchtable=creds.searchTable,searchcol='fullpath',regex=regexStr,progress=False)
    else:
        filesToProcess = sql_query(database=creds.database,searchtable=creds.searchTable,searchcol='fullpath',regex=regexStr,**incExcDict,progress=False)



    # loop throught files
    filesToProcess.sort()
    reconallFlag = True
    threadCount = 0
    for f in filesToProcess:

        #check for processed output
        subName, sesNum = get_dir_identifiers(os.path.dirname(f))
        mainReconallOutputDir = os.path.join(creds.dataDir,'derivatives','recon-all')
        outFile = os.path.join(mainReconallOutputDir, 'sub-' + subName + '_ses-' + sesNum, 'mri', 'T1w.a2009s.segstats.dat')
        if os.path.isfile(outFile) and not options.OVERWRITE:
            continue


        #run job on condor
        if options.SUBMIT:
            #create condor job
            if reconallFlag:
                if options.STAGE1 or (not options.STAGE1 and not options.STAGE2):
                    job_reconall1 = create_python_condor_job('reconall1','fsreconall_stage1.py',creds.machineNames,submit,error,output,log,dagman)
                if options.STAGE2:
                    job_reconall2 = create_python_condor_job('reconall2','fsreconall_stage2.py',creds.machineNames,submit,error,output,log,dagman)
                reconallFlag = False


            #create argument string
                
            if options.STAGE1 and options.STAGE2:
                argStr = (f + ' ' + 
                        creds.dataDir + ' ' +
                        reconallInputFile + ' ' + 
                        mainReconallOutputDir)
                argStr += ' --directive autorecon1'
                if options.OVERWRITE:
                    argStr += ' --overwrite'
                if options.progress:
                    argStr += ' --progress'

                #add arguments to condor job
                job_reconall1.add_arg(argStr)# + ' > ' + os.path.join(creds.s3_dir,s3_outLog))
                print('Added Stage-1 job for freesurfer reconall for file:  ' + f)

                argStr2 = (os.path.join(mainReconallOutputDir,'sub-' + subName + '_ses-' + sesNum) + ' ' + 
                        creds.dataDir + ' ' + 
                        reconallInputFile)
                if options.OVERWRITE:
                    argStr2 += ' --overwrite'
                if options.progress:
                    argStr2 += ' --progress'    


                #add arguments to condor job
                job_reconall2.add_arg(argStr2)# + ' > ' + os.path.join(creds.s3_dir,s3_outLog))
                print('Added Stage-2 job for freesurfer reconall for file:  ' + f)

            elif options.STAGE1 or (not options.STAGE1 and not options.STAGE2):
                argStr = (f + ' ' + 
                        creds.dataDir + ' ' +
                        reconallInputFile + ' ' + 
                        mainReconallOutputDir)
                if options.OVERWRITE:
                    argStr += ' --overwrite'
                if options.progress:
                    argStr += ' --progress'

                #add arguments to condor job
                job_reconall1.add_arg(argStr)# + ' > ' + os.path.join(creds.s3_dir,s3_outLog))
                print('Added Stage-1 job for freesurfer reconall for file:  ' + f)

            elif options.STAGE2:

                argStr2 = (os.path.join(mainReconallOutputDir,'sub-' + subName + '_ses-' + sesNum) + ' ' + 
                        creds.dataDir + ' ' + 
                        reconallInputFile)
                if options.OVERWRITE:
                    argStr2 += ' --overwrite'
                if options.progress:
                    argStr2 += ' --progress'    


                #add arguments to condor job
                job_reconall2.add_arg(argStr2)# + ' > ' + os.path.join(creds.s3_dir,s3_outLog))
                print('Added Stage-2 job for freesurfer reconall for file:  ' + f)

            # if threadCount == 20 or f in filesToProcess[-1]:
            if f in filesToProcess[-1]:

                #job order
                if options.STAGE1 and options.STAGE2:
                    job_reconall1.add_child(job_reconall2)
                dagman.build_submit()

                if f in filesToProcess[-1]:
                    return
            else:
                threadCount += 1

        else:
            if options.STAGE1 and options.STAGE2:
                fsreconall_stage1(f,creds.dataDir,reconallInputFile,mainReconallOutputDir,directive='autorecon1',overwrite=options.OVERWRITE,progress=options.progress)
                fsreconall_stage2(os.path.join(mainReconallOutputDir,'sub-' + subName + '_ses-' + sesNum),creds.dataDir,reconallInputFile,overwrite=options.OVERWRITE,progress=options.progress)
            
            elif options.STAGE1 or (not options.STAGE1 and not options.STAGE2):
                fsreconall_stage1(f,creds.dataDir,reconallInputFile,mainReconallOutputDir,overwrite=options.OVERWRITE,progress=options.progress)

            if options.STAGE2:
                fsreconall_stage2(os.path.join(mainReconallOutputDir,'sub-' + subName + '_ses-' + sesNum),creds.dataDir,reconallInputFile,overwrite=options.OVERWRITE,progress=options.progress)
            



# ******************* MAIN ********************
def main():
    """
    The entry point of this program.
    """

    #get and evaluate options
    options = parse_arguments()
    read_credentials(options.PROJECT)

    #do some prep for parallel processing 
    if options.SUBMIT:
        #get some precursors
        now = datetime.datetime.today().strftime('%Y%m%d_%H%M')
        base = os.path.join(creds.dataDir,'derivatives','processing_logs','connect_recon-all')
        if not os.path.isdir(base):
            os.makedirs(base)

        if not os.path.isdir(os.path.join(creds.dataDir,'derivatives','recon-all')):
            os.makedirs(os.path.join(creds.dataDir,'derivatives','recon-all'))

        #output files
        submit = os.path.join(base,'fsreconall_' + now + '.submit')
        error = os.path.join(base,'fsreconall_' + now + '.error')
        output = os.path.join(base,'fsreconall_' + now + '.output')
        log = os.path.join(base,'fsreconall_' + now + '.log')
        dagman = Dagman(name=options.PROJECT + '-fsreconall', submit=submit)


        #perform struc 2 standard registration
        prepare_pipeline(options,submit=submit,error=error,output=output,log=log,dagman=dagman)

    else:
        prepare_pipeline(options)

    

    

if __name__ == '__main__':
    main()
