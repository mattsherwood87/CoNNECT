#!/resshare/wsuconnect/python3_venv/bin/python
# the command above ^^^ sets python 3.10.10 as the interpreter for this program

# Created by Matthew Sherwood (matt.sherwood@wright.edu, matthew.sherwood.7.ctr@us.af.mil)
# Created on 16 Sept 2021
#
# 

import os
import sys
import json
import subprocess
from typing import Tuple

#local import

REALPATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
# sys.path.append(REALPATH)
# REALPATH = os.path.join('/resshare','general_processing_codes')
sys.path.append(REALPATH)

import support_tools as st
# from classes.creds import *
# from helper_functions.bids_commands import *

# FSLDIR = os.environ["FSLDIR"]
FSLDIR = os.environ["FSLDIR"]
os.system('FSLDIR=' + os.environ["FSLDIR"])
# os.system('source /etc/profile.d/fsl.sh')

def get_scan_id(inDir: str,basename: str) -> Tuple[str, str, dict]:
    """
    Get metadata from a source NIfTI file

    This program determines the key specified in the projects scan_id JSON control file associated with NIfTI images. A JSON sidecar must exist in the same directory as the NIfTI.

    :param inDir: fullpath to directory containing NIfTI file
    :type inDir: str

    :param basename: basename of input NIfTi file
    :type basename: str

    :raises Exception: general error encountered during execution

    :return: scan name as identified in the Project's scan_id JSON file within the Project's 'code' directory, bids directory as identified in the Project's scan_id JSON file within the Project's 'code' directory, scan identifier keys from the scan_id.json control file
    :rtype: Tuple[str, str, dict]
    """

    #DETERMINE SCAN TYPE
    bidsDir = '0'
    scanName = '0'

    #Point to project's sessions.tsv file
    if os.path.isfile(os.path.join(st.creds.dataDir,'code',st.creds.project + '_scan_id.json')):
        with open(os.path.join(st.creds.dataDir,'code',st.creds.project + '_scan_id.json')) as j:
            scanId = json.load(j)
    else:
        print('ERROR: project scan_id.json file not found')
        print('\tPlease create ' + os.path.join(st.creds.dataDir,'code',st.creds.project + '_scan_id.json'))
        sys.exit()



    try:
        #read input image dimensions
        dims = []
        scanKeys = {}
        for d in ['dim1','dim2','dim3','dim4']:
            proc = subprocess.check_output(os.path.join(FSLDIR,'bin','fslval') + ' ' + os.path.join(inDir,basename + '.nii.gz') + ' ' + d,shell=True,encoding='utf-8')
            dims.append(int(proc.split(' ')[0]))

        #read associated JSON file
        if os.path.isfile(os.path.join(inDir,basename + '.json')):
            with open(os.path.join(inDir,basename + '.json')) as j:
                jsonHeader = json.load(j)

            # Loop over image types in project's scan_id JSON file
            for imageType in scanId.keys():
                stopFlag = True

                if not isinstance(scanId[imageType],dict):
                    continue
                if not 'json_header' in scanId[imageType].keys():
                    continue

                #loop over all of the json header keys
                for headerKey in scanId[imageType]['json_header'].keys():
                    tmp_stopFlag = False

                    #split items that should not be in the associated header key 
                    if 'Not' in headerKey:
                        #only proceed if values are not present
                        if headerKey.replace('Not','') in jsonHeader.keys():
                            if all([k not in str(jsonHeader[headerKey.replace('Not','')]) for k in scanId[imageType]['json_header'][headerKey]]):  
                                tmp_stopFlag = True

                    else:
                        #only proceed if values are present
                        if headerKey in jsonHeader.keys():
                            if type(scanId[imageType]['json_header'][headerKey]) is int:
                                if jsonHeader[headerKey] == scanId[imageType]['json_header'][headerKey] and dims == scanId[imageType]['dims']:
                                    tmp_stopFlag = True
                            elif type(scanId[imageType]['json_header'][headerKey]) is list:
                                if all([k in str(jsonHeader[headerKey]) for k in scanId[imageType]['json_header'][headerKey]]) and dims == scanId[imageType]['dims']:
                                    tmp_stopFlag = True
                            elif type(scanId[imageType]['json_header'][headerKey]) is str:
                                if scanId[imageType]['json_header'][headerKey] in str(jsonHeader[headerKey]) and dims == scanId[imageType]['dims']:
                                    tmp_stopFlag = True
                    
                    if not tmp_stopFlag and stopFlag:
                        stopFlag = False
                        continue

                if stopFlag:
                    bidsDir = scanId[imageType]['BidsDir']
                    scanName = st.bids.get_bids_filename(**scanId[imageType]['bids_labels'])
                    # scanName = scanId[imageType]['ScanName']
                    scanKeys = scanId[imageType]
                    break




    except Exception as e:
        print('ERROR: ' + basename + ' ', end='')
        print(e)
        outputTxt = os.path.join(st.creds.dataDir,'derivatives','processing_logs',st.creds.project + '_scan_id.error')
        with open(outputTxt,'a+') as txtFile:
            txtFile.write('ERROR: ' + basename + ' \n\t')
            txtFile.write(str(e))
            txtFile.write('\n')
            r = {}
        
        return '0','0',r

    return scanName, bidsDir, scanKeys