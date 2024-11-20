#!/resshare/general_processing_codes/python3_venv/bin/python
# the command above ^^^ sets python 3.10.10 as the interpreter for this program

# Created by Matthew Sherwood (matt.sherwood@wright.edu, matthew.sherwood.7.ctr@us.af.mil)
# Created on 23 Dec 2020
#
# Modified on 25 October 2024 - update to new session formats and use of helper_functions
# Modified on 17 April 2023 - update to WSU format
# Modified on 24 Nov 2021 - improve efficiency based on processed_data_check output
# Modified on 5 Nov 2021 - implement BIDS formatting
# Modified on 11 Jan 2021 - add utilization of instance_ids.json

import os
import time
import sys
import argparse
import json


#local import
REALPATH = os.path.realpath(__file__)
sys.path.append(os.path.dirname(REALPATH))
import support_tools as st
# from helper_functions.get_scan_id import *
# from helper_functions.get_dir_identifiers import *
# from helper_functions.read_credentials import *
# from helper_functions.get_spec_base import *
# from helper_functions.mysql_commands import *


# GLOBAL INFO
#versioning
VERSION = '1.0.0'
DATE = '29 October 2024'

#input argument parser
parser = argparse.ArgumentParser('connect_add_sidecar_key.py: adds JSON sidecar keys from scan_id.json (Units or TaskName) to each appropriate NIfTI sidecar (json)')


# ******************* PARSE COMMAND LINE ARGUMENTS ********************
parser.add_argument('-p','--project', action="store", dest="PROJECT", help="select a project: " + ' '.join(st.creds.projects), default=None, required=True)
parser.add_argument('--progress', help="Show progress (default FALSE)", action="store_true", dest="progress", default=False)
parser.add_argument('-v', '--version', help="Display the current version", action="store_true", dest="version")
  


# ******************* EVALUATE INPUT ARGUMENTS ********************
def evaluate_args(options):

    dataCheckFile = None
    
    #print version if selected
    if options.version:
        print('connect_add_sidecar_key.py version {0}.'.format(VERSION)+" DATED: "+DATE)

    

    return 



# ******************* EVALUATE INPUT ARGUMENTS ********************
def add_json_sidecar_key(inFile):
    #get time info for verbose option


    try:
        # splitFilename = os.path.splitext(os.path.join(inDir,filename))

        #only progress if nifti
        sourceDir = os.path.dirname(inFile)
        filename = os.path.basename(inFile)
        filename_split = os.path.splitext(filename)

        #file has an extension
        if filename_split[1] == '.json':

            #get scan identifier
            scanName, bidsDir, scanKeys = st.get_scan_id(sourceDir,filename_split[0])
            

            b_updated  = False
            baseOutput = os.path.join(sourceDir,filename)
            if 'TaskName' in scanKeys.keys() or 'Units' in scanKeys.keys():
                with open(baseOutput, 'r') as j:
                    imgHeader = json.load(j)
                for k in ['TaskName','Units']:
                    if k in scanKeys.keys() and not k in imgHeader.keys():
                        imgHeader[k] = scanKeys[k]
                        b_updated = True
                
                if b_updated:
                    with open(os.path.join(sourceDir,filename), 'w') as j:
                        json.dump(imgHeader, j,indent='\t', sort_keys=True)
                    print('Updated ' + baseOutput)

    #catch any errors
    except Exception as e:
        print('ERROR: ' + filename_split[0] + ' ', end='')
        print(e)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)

    return 




if __name__ == '__main__':
    """
    The entry point of this program.
    """
    options = parser.parse_args()
    evaluate_args(options)
    st.creds.read(options.PROJECT)



    
    jsonFileList = st.mysql_commands.sql_query(database=st.creds.database,searchtable=st.creds.searchTable,searchcol='fullpath',regex='json',exclusion=['bak'],inclusion=['rawdata','sub-','ses-'])#orinclusion=['.nii','.7','.log','.txt','.rda','.json'])

    #loop over all tables
    for fileName in jsonFileList:
        add_json_sidecar_key(fileName)


    if options.progress:
        print('\n\tCompleted processing project ' + st.creds.project)