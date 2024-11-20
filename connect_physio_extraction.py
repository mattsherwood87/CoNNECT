#!/resshare/general_processing_codes/python3_venv/bin/python
# the command above ^^^ sets python 3.11.11 as the interpreter for this program

# Created by Matthew Sherwood (matt.sherwood@wright.edu, matthew.sherwood.7.ctr@us.af.mil)
# Created on 23 September 2024
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
from helper_functions.dti_preprocess import dti_preprocess
from helper_functions.id_check import id_check
from helper_functions.test_exp_log_parser import *

from classes.creds import *


# GLOBAL INFO
#versioning
VERSION = '1.0.1'
DATE = '23 September 2024'
FSLDIR = os.environ["FSLDIR"]

#input argument parser
parser = argparse.ArgumentParser()

# ******************* PARSE COMMAND LINE ARGUMENTS ********************
def parse_arguments():

    #input options for main()
    requiredNamed = parser.add_argument_group('required arguments')
    requiredNamed.add_argument('-p','--project', action="store", dest="PROJECT", help="Perform DTI preprocessing for the selected project: " + ' '.join(creds.projects), default=None)

    parser.add_argument('--overwrite', action="store_true", dest="OVERWRITE", help="Force conversion by skipping directory and database checking", default=False)
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



# ******************* Setup Main Processing ********************
def physio_extraction(options,*args,**kwargs):
    submit = kwargs.get('submit',None)
    error = kwargs.get('error',None)
    output = kwargs.get('output',None)
    log = kwargs.get('log',None)
    dagman = kwargs.get('dagman',None)

    #load parameter JSON control file
    try:
        physInputFile = os.path.join(creds.dataDir,'code',options.PROJECT + '_physio_preprocess_input.json')
        if not os.path.isfile(physInputFile):
            return

        with open(physInputFile) as j:
            physInput = json.load(j)

            #asl sql_query inputs
            incExcDict = {}
            if 'inclusion_list' in physInput:
                incExcDict['inclusion'] = physInput.pop('inclusion_list')
            if 'exclusion_list' in physInput:
                incExcDict['exclusion'] = physInput.pop('exclusion_list')

    except FileNotFoundError as e:
        print("Error Message: {0}".format(e))
        sys.exit()

    # regexStr = get_bids_filename(**dtiInput['main_image_params']['input_bids_labels'])

    if not incExcDict:
        filesToProcess = sql_query(database=creds.database,searchtable=creds.searchTable,searchcol='fullpath',regex=physInput['regexstr'],progress=False)
    else:
        filesToProcess = sql_query(database=creds.database,searchtable=creds.searchTable,searchcol='fullpath',regex=physInput['regexstr'],**incExcDict,progress=False)




    # loop throught files
    filesToProcess.sort()
    for f in filesToProcess:

        #get subject name and see if they should be discarded
        subName, sesNum = get_dir_identifiers(os.path.dirname(f))
        if id_check(subName):

            #check for processed output
            outFilepath = os.path.join(creds.dataDir, 'derivatives', 'sub-' + subName, 'ses-' + sesNum, 'beh')
            outFile = glob(os.path.join(outFilepath, '*physio-data.csv'))
            if len(outFile) > 0 and not options.OVERWRITE:
                print('WARNING: Output files found in ' + outFilepath)
                print('\toverwrite not specified, skipping')
                continue


            outFilepath = os.path.join(outFilepath,'_'.join(['sub-' + subName,'ses-' + sesNum,'physio-data.csv']))
            if not os.path.isdir(os.path.dirname(outFilepath)):
                os.makedirs(os.path.dirname(outFilepath))
            l = parse_presentation_logfile(f,outFilepath,['test','test2'],['test','test2'],'fMRI base',['200','200'])

        


    return


# ******************* MAIN ********************
def main():
    """
    The entry point of this program.
    """

    #get and evaluate options
    options = parse_arguments()
    read_credentials(options.PROJECT)

   
    physio_extraction(options)

    

    

if __name__ == '__main__':
    main()
