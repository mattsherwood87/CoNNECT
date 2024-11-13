#!/resshare/general_processing_codes/python3_venv/bin/python
# the command above ^^^ sets python 3.10.9 as the interpreter for this program

# Created by Matthew Sherwood (matt.sherwood@wright.edu, matthew.sherwood.7.ctr@us.af.mil)
# Created on 19 July 2023
#
# Modified on 17 May 2024 - slight tweak to change recon-all to autorecon1 when running stage2

import sys
import os
import argparse
import json
from nipype.interfaces import freesurfer
from glob import glob as glob
import datetime

#local import
# REALPATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
# sys.path.append(REALPATH)
REALPATH = os.path.join('/resshare','general_processing_codes')
sys.path.append(REALPATH)
from helper_functions.flirt_pngappend import *
from helper_functions.get_dir_identifiers import *
from helper_functions.bids_commands import *
from helper_functions.fsreconall_stage2 import fsreconall_stage2


VERSION = '1.0.1'
DATE = '17 May 2023'


parser = argparse.ArgumentParser('fsreconall_stage1.py: perform recon-all - either all stages or autorecon1 if also running stage2')
FSLDIR = os.environ["FSLDIR"]

# s3 = boto3.resource('s3')

def parse_arguments():

    #input options for main()
    parser.add_argument('IN_FILE')
    parser.add_argument('DATA_DIR')
    parser.add_argument('RECONALL_PARAMS')
    parser.add_argument('MAINRECONALLOUTPUTDIR')
    parser.add_argument('--directive',action='store',dest='DIRECTIVE',default=None)
    parser.add_argument('--overwrite',action='store_true',dest='OVERWRITE',default=False)
    parser.add_argument('--progress',action='store_true',dest='progress',default=False)
    options = parser.parse_args()
    return options


class InvalidJsonInput(Exception):
    "Raised when the input JSON control file does not contain the appropriate mandatory definitions"
    pass


# ******************* s3 bucket check ********************
def fsreconall_stage1(IN_FILE,DATA_DIR,RECONALL_PARAMS,MAINRECONALLOUTPUTDIR,*args,**kwargs):
    """
    This function performs FLIRT registration between IN_FILE and structural/standard brain images. Brain extraction will be performed on IN_FILE prior to registration if bet_params is specified.

    flirt(IN_FILE,DATA_DIR,FLIRT_PARAMS,overwrite=False,bet_params=None,progress=False)

    Arguments:

        IN_FILE (str): fullpath to a NIfTI file

        DATA_DIR (str): fullpath to the project's data directory (project's 'dataDir' credential)

        RECONALL_PARAMS (str): fullpath to project's FS RECON-ALL parameter file

        args (str): a sequence of program arguments
            
        overwrite (BOOL): OPTIONAL flag to overwrite existing files (True) or not (False) 
            
        progress (BOOL): OPTIONAL flag to display command line output providing additional details on the processing status

    Returns:
        None
    """
    directive = kwargs.get('directive',None)
    overwriteFlag = kwargs.get('overwrite',False)
    progress = kwargs.get('progress',False)
    outputFileList = []

    try:
        now = datetime.datetime.now()

        if progress:
            print('\n\nfsreconall_preprocess.py version ' + VERSION + ' dated ' + DATE + '\n')
            print('running @ ' + now.strftime("%m-%d-%Y %H:%M:%S") + '\n')
            print('Reading JSON Control File')

        #read parameter file
        with open(RECONALL_PARAMS) as j:
            reconallFullParams = json.load(j)

            # Organize parameter inputs
                
            #get main FLIRT parameters
            if 'reconall_params' in reconallFullParams:
                reconallParams = reconallFullParams.pop('reconall_params')
            else:
                raise InvalidJsonInput

            if 'main_image_params' in reconallFullParams:
                mainParams = reconallFullParams.pop('main_image_params')
            else:
                raise InvalidJsonInput


        #check if file exists on local disk
        mainFile = IN_FILE
        if not os.path.isfile(mainFile):
            if progress:
                print('ERROR: Main Image File Not Found')
            raise OSError
        elif progress:
            print('Main Image File Found: ' + mainFile)
        
        # create file inputs and outputs
        mainFileDir = os.path.dirname(mainFile)
        subName, sesNum = get_dir_identifiers(mainFileDir)
        # mainReconallOutputDir = os.path.join(DATA_DIR,'derivatives','recon-all-new')#create base path and filename for move

        if not os.path.isdir(MAINRECONALLOUTPUTDIR):
            os.makedirs(MAINRECONALLOUTPUTDIR)

        # move subjects dir to reconall output directory
        # os.system('export SUBJECTS_DIR=' + mainReconallOutputDir)
        # if progress:
        #     print('SUBJECTS_DIR redirected to output directory: ' + mainReconallOutputDir)
            
        newRegexStr = reconallFullParams['brainmask_regex'].split('.')
        in_brainmaskFile = glob(os.path.join(DATA_DIR,'derivatives','sub-' + subName,'ses-' + sesNum,'bet','anat','*' + newRegexStr[0] + '_manual.' + '.'.join(newRegexStr[1:]) + '*'))
        if len(in_brainmaskFile) == 1:
            MAINRECONALLOUTPUTDIR = MAINRECONALLOUTPUTDIR + '_manual'

        #setup and freesurfer
        fsrecon = freesurfer.ReconAll(**reconallParams)
        fsrecon.inputs.subject_id = 'sub-' + subName + '_ses-' + sesNum
        fsrecon.inputs.subjects_dir = MAINRECONALLOUTPUTDIR
        fsrecon.inputs.T1_files = mainFile
        stage1_dir = os.path.join(MAINRECONALLOUTPUTDIR, 'sub-' + subName + '_ses-' + sesNum)
        if directive:
            fsrecon.inputs.directive = directive
        skip = False
        if os.path.isdir(stage1_dir):
            if overwriteFlag:
                if progress:
                    print('Output directory exists, removing and running freesurfer recon-all')
                os.system('rm -rf ' + stage1_dir)
                fsrecon.run()
            else:
                if progress:
                    print('WARNING: Output folder exists, overwrite was not specified skipping freesurfer recon-all')
        else:
            if progress:
                print('Output folder does not exist, running freesurfer recon-all')
            fsrecon.run()

        # #run stage 2 if all inputs exist
        # if not os.path.isfile(os.path.join(stage1_dir,'mri','T1w.segstats.dat')) or overwriteFlag and not skip:  
        #     brainMask = glob(os.path.join(DATA_DIR,'derivatives','sub-' + subName,'ses-' + sesNum,'bet','anat','*' + reconallFullParams['brainmask_regex'] + '*')) 
        #     if len(brainMask) == 1:
        #         if progress:
        #             print('Initiating Stage 2')
                
        #         fsreconall_stage2(stage1_dir, DATA_DIR, RECONALL_PARAMS, progress=progress, overwrite=overwriteFlag)
        #     else:
        #         fsrecon.inputs.directive = 'autorecon1'
        #         fsrecon.run()
        #         if progress:
        #             print('WARNING: skipping stage 2, either none or more than 1 brainmask file found in ' + os.path.join(DATA_DIR,'derivatives','sub-' + subName,'ses-' + sesNum,'bet','anat','*' + reconallFullParams['brainmask_regex'] + '*'))
        # else:
        #     fsrecon.run()
        #     if progress:
        #         print('WARNING: skipping stage 2 - output exists and overwrite was not specified')

    except OSError as e:
        print("Error Message: {0}".format(e))
        return
    except InvalidJsonInput:
        print("Invalid JSON Input: {0}".format(e))
        return
    except Exception as e:
        print("Error Message: {0}".format(e))
        return
        

if __name__ == '__main__':
    options = parse_arguments()
    argsDict = {}
    if options.DIRECTIVE:
        argsDict['directive'] = options.DIRECTIVE
    if options.OVERWRITE:
        argsDict['overwrite'] = options.OVERWRITE
    if options.progress:
        argsDict['progress'] = options.progress
    fsreconall_stage1(options.IN_FILE,options.DATA_DIR,options.RECONALL_PARAMS,options.MAINRECONALLOUTPUTDIR,**argsDict)

    


