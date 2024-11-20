#!/resshare/wsuconnect/python3_venv/bin/python
# the command above ^^^ sets python 3.10.9 as the interpreter for this program

# Created by Matthew Sherwood (matt.sherwood@wright.edu, matthew.sherwood.7.ctr@us.af.mil)
# Created on 16 Sept 2021
#
# 

import os
import sys
import json
import subprocess
import argparse
from glob import glob as glob

#local import

REALPATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
# sys.path.append(REALPATH)
# REALPATH = os.path.join('/resshare','general_processing_codes')
sys.path.append(REALPATH)

import support_tools as st



# ******************* PARSE COMMAND LINE ARGUMENTS ********************
parser = argparse.ArgumentParser('evaluate_raw_file_transfer.py: checks to ensure all rawdata exists for given input directory')

parser.add_argument('-p','--project', required=True, action="store", dest="PROJECT", help='select a project from the credentials.json file', default=None)
parser.add_argument('-i','--in-dir', required=True, action="store", dest="IN_DIR", help="path to individual subject/session to search for raw nifti images", default=None)

# parser.add_argument('-m','--multiple', action="store_true", dest="MULTIPLE", help="process all directories supplied by -i|--in-dir -> path to directory containing multiple subject/session raw directories", default=False)

parser.add_argument('--progress', help="Show progress (default FALSE)", action="store_true", dest="progress", default=False)
parser.add_argument('-v', '--version', help="Display the current version", action="store_true", dest="version")


def evaluate_raw_file_transfer(project: str,inDir: str) -> bool:
    """
    This program evaluates files appearing in a single subject/session rawdata directory (inDir). Filenames expected to appear in the rawdata directory are determined from the project's scan_id.json file found in the project's code directory.

    evaluate_raw_file_transfer(project,inDir)

    :param project:  target Project's <project identifier>
    :type project: str

    :param inDir: fullpath to a single subject/session rawdata directory
    :type inDir: str

    :raises Exception: general error encountered during execution

    :return: flag if all expected files exist (True) or don't (False)
    :rtype: bool
    """

    st.read_credentials(project)

    #Point to project's sessions.tsv file
    if os.path.isfile(os.path.join(st.creds.dataDir,'code',st.creds.project + '_scan_id.json')):
        with open(os.path.join(st.creds.dataDir,'code',st.creds.project + '_scan_id.json')) as j:
            scanId = json.load(j)
    else:
        print('ERROR: project scan_id.json file not found')
        print('\tPlease create ' + os.path.join(st.creds.dataDir,'code',st.creds.project + '_scan_id.json'))
        sys.exit()



    try:

        #get subject name from filename
        print('Checking DIR - ' + inDir)
        st.get_dir_identifiers_new(inDir)
        # sessionNum = fullSessionNum.split('-')
        # if not len(sessionNum) > 0:
        #     print('Error: Must have a valid session number after date')
        #     sys.exit()
        # seriesDate = sessionNum[0]
        # seriesDateMoYr = seriesDate[0:6]
        # sessionNum = sessionNum[1]

        allFiles = True
        imgList = []
        for k in scanId:
            if not isinstance(scanId[k],dict):
                continue
            elif not 'BidsDir' in scanId[k].keys():
                continue

            
            if st.subject.sesNum in scanId[k]['sessions']:
                bidsDir = scanId[k]['BidsDir']
                scanName = st.get_bids_filename(**scanId[k]['bids_labels'])

                inTargFiles = glob(os.path.join(st.creds.dataDir,'rawdata','sub-' + st.subject.id,'ses-' + st.subject.sesNum,bidsDir,'sub-' + st.subject.id + '_' + 'ses-' + st.subject.sesNum + scanName + '.nii.gz'))
                
                if not inTargFiles:
                    allFiles = False
                    imgList.append('NOT FOUND: ' + scanName)
                else:

                    # #read associated JSON file
                    if os.path.isfile(inTargFiles[0].replace('nii.gz','json')):
                        with open(inTargFiles[0].replace('nii.gz','json')) as j:
                            jsonHeader = json.load(j)
                    imgList.append(jsonHeader['ProtocolName']) #CHANGE THIS LATER
                    if os.path.isfile(inTargFiles[0].replace('nii.gz','txt')):
                        with open(inTargFiles[0].replace('nii.gz','txt')) as t:
                            for l in t:
                                a=l.split('\t')[1:]
                        d_txt = {}
                        k = None
                        for x in a:
                            if ':' in x:
                                k = x[:-1]
                            else:
                                if not k in d_txt.keys():
                                    d_txt[k] = x
                                else:
                                    d_txt[k] = [d_txt[k],x]
                        seriesDateMoYr = d_txt['DateTime'][0:6]


        if allFiles:

            print('found all files in ' + inDir)
            if not os.path.isdir(os.path.join('/Export','data_transfer_progress')):
                 os.makedirs(os.path.join('/Export','data_transfer_progress'))
            d = ','.join([st.creds.project,st.subject.id,st.subject.sesNum,'TRUE,']) + ','.join(imgList)
            if os.path.isfile(os.path.join('/Export','data_transfer_progress',seriesDateMoYr + '_file-transfer-log.txt')):
                f = open(os.path.join('/Export','data_transfer_progress',seriesDateMoYr + '_file-transfer-log.txt'),'r+')
                l = f.readlines()
            else:
                f = open(os.path.join('/Export','data_transfer_progress',seriesDateMoYr + '_file-transfer-log.txt'),'x')
                l = []

            #see if subject/session already exists in log file, remove if it does
            for line in l:
                sp_d = d.split(',')
                if ','.join(sp_d[0:3]) in line:
                    l.remove(line)
                    
            l.insert(0,d + '\n')
            f.seek(0) #get to the first position
            f.writelines(l)
            f.close()
        else:
            print('did not find all files in ' + inDir)
            if not os.path.isdir(os.path.join('/Export','data_transfer_progress')):
                 os.makedirs(os.path.join('/Export','data_transfer_progress'))
            d = ','.join([st.creds.project,st.subject.id,st.subject.sesNum,'FALSE,']) + ','.join(imgList)
            if os.path.isfile(os.path.join('/Export','data_transfer_progress',seriesDateMoYr + '_file-transfer-log.txt')):
                f = open(os.path.join('/Export','data_transfer_progress',seriesDateMoYr + '_file-transfer-log.txt'),'r+')
                l = f.readlines()
            else:
                f = open(os.path.join('/Export','data_transfer_progress',seriesDateMoYr + '_file-transfer-log.txt'),'x')
                l = []

            for line in l:
                sp_d = d.split(',')
                if ','.join(sp_d[0:3]) in line: # and sp_d[1] in line and sp_d[2] in line:
                    l.remove(line)
            l.insert(0,d + '\n')
            f.seek(0) #get to the first position
            f.writelines(l)
            f.close()
        
        return allFiles




    except Exception as e:
        print('ERROR: ' + inDir + ' ', end='')
        print(e)

        return False


if __name__ == '__main__':
    """
    The entry point of this program for command-line utilization.
    """
    options = parser.parse_args()
    evaluate_raw_file_transfer(options.PROJECT,options.IN_DIR)
