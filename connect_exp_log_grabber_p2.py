#!/resshare/wsuconnect/python3_venv/bin/python
# the command above ^^^ sets python 3.7.5 as the interpreter for this program

# Created by Matthew Sherwood (matt.sherwood@wright.edu, matthew.sherwood.7.ctr@us.af.mil)
# Created on 31 Jan 2023
#
# Last Modified on 6 Sep 2024 - incorporate changes for xdf files
# Modified on 28 Feb 2023 - slight changes to grab path of script automatically 

# ******* IMPORTS ***********
from cmath import inf
import os
import argparse
import json
import shutil
import datetime
import csv
import re
import sys
import pyxdf


# ******* LOCAL IMPORTS ******
#GLOBALS
REALPATH = os.path.dirname(os.path.realpath(__file__))

sys.path.append(REALPATH)
import support_tools as st


# ******* GLOBAL INFO *******
#versioning
VERSION = '1.0.3'
DATE = '6 Sep 2024'


# ******************* PARSE COMMAND LINE ARGUMENTS ********************
parser = argparse.ArgumentParser()
parser.add_argument('-v', '--version', action="store_true", dest="version", help="Display the current version")


def string_convert(str_to_convert):
    return str(str_to_convert)

def time_convert(time_to_convert):
    return datetime.datetime.strptime(time_to_convert, '%m/%d/%Y %H:%M:%S')

# ******************* MAIN ********************
def main():
    """
    The entry point of this program.
    """

    #get and evaluate options
    # options = parse_arguments()
    logPath = "/Export/tmp_beh_logs"

    #get start time/date of code


    # Loop over directory recursively
    ls_dirs = []
    for root, dirs, files in os.walk(logPath, topdown=True):
            # for path in Path(dcmPath).rglob('*'):
        for filename in files:
            try:
                # Create input file path and read file
                inFullpath = os.path.join(root,filename)

                # with open(inFullpath,'r',encoding='latin-1') as f:
                #     d = csv.reader(f,delimiter='\t')
                #     fileContents = list(d)
                fileContents = []

                with open(os.path.join(REALPATH,'credentials.json')) as f:
                    projectIDs = json.load(f)


                # projId = filename.split('_')[0]
                foundFlag = False
                try:
                    with open(inFullpath,'r',encoding='latin-1') as f:
                        d = csv.reader(f,delimiter='\t')
                        fileContents = list(d)

                    for p in projectIDs['projects']:
                        if len(fileContents) >= 6:
                            if p in fileContents[5]:
                                foundFlag = True
                                proj = p
                                break
                except:
                    foundFlag = False

                if not foundFlag:
                    for p in projectIDs['projects']:
                        if p in filename:
                            foundFlag = True
                            proj = p
                            break

                

                if foundFlag:
                        
                    # try:

                    #grab date
                    try:
                        if filename[-3:] == 'xdf':
                            d,h = pyxdf.load_xdf(inFullpath)
                            logDate = datetime.datetime.strptime(h['info']['datetime'][0],'%Y-%m-%dT%H:%M:%S-0400').strftime('%Y%m%d')

                        else:
                            logDate = datetime.datetime.strptime(''.join(fileContents[1]).split(' - ')[1],'%m/%d/%Y %H:%M:%S').strftime('%Y%m%d')
                        
                        
                        #get subject number and session from log-file
                        if len(fileContents) > 5:
                            if proj in fileContents[5][0]:
                                d = fileContents[5][0].split(proj)[1]
                                d_split = re.split(',| |_|-',d)
                                sub = d_split[1]
                                ses = None
                                if len(d_split) > 2:
                                    ses = d_split[2]
                            else:
                                d = fileContents[5][0]
                                d_split = re.split(',| |_|-',d)
                                sub = d_split[0]
                                ses = None
                                if len(d_split) > 1:
                                    ses = d_split[1]

                        else:
                            sub = filename.split('sub-')[1].split('_')[0]
                            ses = None
                            if 'ses' in filename:
                                ses = filename.split('ses-')[1].split('_')[0]

                    except:
                        logDate = datetime.datetime.strptime(filename[-27:-4],'%Y-%m-%d_%Hh%M.%S.%f').strftime('%Y%m%d')
                        sub = filename.split('sub-')[1].split('_')[0]
                        ses = None
                        if 'ses' in filename:
                            ses = filename.split('ses-')[1].split('_')[0]


                    #get project credentials
                    st.creds.read(proj)
                    
                    #create output directory
                    if ses:
                        destDir = os.path.join(st.creds.dataDir,'rawdata','sub-' + sub, 'ses-' + ses, 'beh')
                        srcDestDir = os.path.join(st.creds.dataDir,'sourcedata','sub-' + sub, 'ses-' + '-' + ses)
                    else:
                        destDir = os.path.join(st.creds.dataDir,'rawdata','sub-' + sub, 'ses-' + logDate, 'beh')
                        srcDestDir = os.path.join(st.creds.dataDir,'sourcedata','sub-' + sub, 'ses-' + logDate)

                    if not os.path.isdir(destDir):
                        os.makedirs(destDir)
                    if not os.path.isdir(srcDestDir):
                        os.makedirs(srcDestDir)

                    shutil.copyfile(inFullpath,os.path.join(srcDestDir,filename))
                    shutil.move(inFullpath,os.path.join(destDir,filename))

                    print('input: ' + inFullpath + '\toutput: ' + os.path.join(destDir,filename))
                    print('input: ' + inFullpath + '\tsource output: ' + os.path.join(srcDestDir,filename))

                else:
                    shutil.move(inFullpath,os.path.join('/resshare','tmp_beh_logs',filename))
                    print('WARNING: unable to determine project. input: ' + inFullpath + '\toutput: ' + os.path.join('resshare','tmp_beh_logs',filename))

                    
                    

                        
            except Exception as e:
                shutil.move(inFullpath,os.path.join('/resshare','tmp_beh_logs',filename))
                print('ERROR: processing ' + filename)
                print(e)
                    

       


if __name__ == '__main__':
    main()
