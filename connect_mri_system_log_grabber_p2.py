#!/resshare/wsuconnect/python3_venv/bin/python
# the command above ^^^ sets python 3.10.9 as the interpreter for this program

# Created by Matthew Sherwood (matt.sherwood@wright.edu, matthew.sherwood.7.ctr@us.af.mil)
# Created on 13 July 2023
#
# Last Modified on 1 Aug 2024 - added functionality to adapt to R11 software revision changes from r5.7
# 

# ******* IMPORTS ***********
import os
import argparse
import json
import pandas as pd
import shutil
import datetime
import csv
import re
# import numpy as np
# import math
import time
import sys
from pathlib import Path
from chardet import detect
import codecs


# ******* LOCAL IMPORTS ******
#GLOBALS
REALPATH = os.path.dirname(os.path.realpath(__file__))

sys.path.append(REALPATH)
import support_tools as st


# ******* GLOBAL INFO *******
#versioning
VERSION = '2.0.1'
DATE = '1 August 2024' 

#input argument parser
parser = argparse.ArgumentParser()




# ******************* PARSE COMMAND LINE ARGUMENTS ********************
def parse_arguments():

    #input options for main()
    requiredNamed = parser.add_argument_group('required arguments')
    requiredNamed.add_argument('-i','--in', action="store", dest="INLOGFILE", help="input Philips system logfile", default=None)
    parser.add_argument('-v', '--version', action="store_true", dest="version", help="Display the current version")
    # parser.add_argument('--progress', action="store_true", dest="progress", help="Show progress (default FALSE)", default=False)
    options = parser.parse_args()

    return options


def string_convert(str_to_convert):
    return str(str_to_convert)

def date_convert(time_to_convert):
    return datetime.datetime.strptime(time_to_convert, '%m/%d/%Y %H:%M:%S')

def get_encoding_type(file):
    with open(file, 'rb') as f:
        rawdata = f.read()
    return detect(rawdata)['encoding']



# ******************* MAIN ********************
def connect_mri_system_log_grabber_p2(inLogFile):
    """
    The entry point of this program.
    """

    #get and evaluate options

    #get start time/date of code


    # Loop over directory recursively
    # ls_dirs = []
    # for root, dirs, files in os.walk(inLogPath, topdown=True):
    #         # for path in Path(dcmPath).rglob('*'):
    #     for filename in files:
    try:
        # Create input file path and read file
        # inFullpath = os.path.join(root,filename)

        # with open(inFullpath) as f:
        #     d = csv.reader(f,delimiter='\t')
        #     fileContents = list(d)

        with open(os.path.join(REALPATH,'credentials.json')) as f:
            projectIDs = json.load(f)


        #read raw logfile encoding type (long)
        # from_codec = get_encoding_type('/resshare/Philips_system_logs/2023/log202305150000.log')

        # #convert to UTF-8 (default is MacRoman)
        # try: 
        #     with open('/resshare/Philips_system_logs/2023/log202305150000.log', 'r', encoding=from_codec) as f, open('/resshare/Philips_system_logs/2023/log202305150000_utf8.log', 'w', encoding='utf-8') as e:
        #         text = f.read() # for small files, for big use chunks
        #         e.write(text)

        #     # os.remove(srcfile) # remove old encoding file
        #     # os.rename(trgfile, srcfile) # rename new encoding
        # except UnicodeDecodeError:
        #     print('Decode Error')
        # except UnicodeEncodeError:
        #     print('Encode Error')

        #read default mac-roman format
        cols = ['c1','date','time','c4','c5','c6','c7','c8','logger','event','c11','c12','c13','c14']
        df = pd.read_csv(inLogFile,sep='\t',skiprows=1,on_bad_lines='warn',encoding='mac-roman',names=cols,header=None)
        # df = pd.read_csv('/resshare/Philips_system_logs/2023/log202306120000.log',sep='\t',skiprows=1,on_bad_lines='warn',encoding='mac-roman',names=cols,header=None)

        #Find all new exam notifications
        #df_exams=df[df['event'].str.contains(r'(?=.*ExamCardName)(?=.*ScheduledProcedureStep)',na=False,regex=True)]
        df_exams=df[df['event'].str.contains(r'(?=.*ExamOverview)(?=.*MRExamCardModel)(?=.*\(ExamOverview\))(?=.*Updating Examcard name to)',na=False,regex=True)]
        l_examIdx = df_exams.index.to_list()

        #loop through all exams
        for e, examIdx in enumerate(l_examIdx):
            #create reduced dataframe template
            df_out = pd.DataFrame(columns = ['date','time','project','marker','event'])
            proj = None

            if examIdx == l_examIdx[-1]:
                df_redExam = df.iloc[examIdx:]
            else:
                df_redExam = df.iloc[examIdx:l_examIdx[e+1]-1]


            #save single exam input to output dataframe
            print('\nExam:' + df_exams['date'].iloc[e] + '\t' + df_exams['time'].iloc[e] + '\t' + df_exams['event'].iloc[e])
            df_out = df_out.T.join(df_exams[['date','time','event']].iloc[e].T).T.sort_index()

            #get project
            #examEvent = df_exams['event'].iloc[e].split(': ')[1].split(', ')[0]
            examEvent = df_exams['event'].iloc[e].split('ExamOverview(MRExamCardModel): (ExamOverview) Updating Examcard name to ')[-1]
            for k in projectIDs.keys():
                if type(projectIDs[k]) is dict:
                    if 'examCardName' in projectIDs[k].keys():
                        #if examEvent in projectIDs[k]['examCardName']:
                        if projectIDs[k]['examCardName'] in examEvent:
                            proj = k
                            break

            df_out.at[examIdx,'project'] = proj
            df_out.at[examIdx,'marker'] = 'New Exam'


            #find all manual scan starts (do these coordinate to auto scan starts? if not what does?)
            df_startButtons = df_redExam[df_redExam['event'].str.contains(r'(?=.*OnScanEngineStart\(\))(?=.*startScanButtonPressed)',na=False,regex=True)]
            l_startButtonIdx = df_startButtons.index.to_list()
            # print('\nStart Buttons')
            for sb, sbIdx in enumerate(l_startButtonIdx) :
                if sbIdx == l_startButtonIdx[-1]:
                    df_redStart = df.iloc[sbIdx:]
                else:
                    df_redStart = df.iloc[sbIdx:l_startButtonIdx[sb+1]-1]
                
                # print('\nStart Buttons')
                # print(df_startButtons['date'].iloc[sb] + '\t' + df_startButtons['time'].iloc[sb] + '\t' + df_startButtons['event'].iloc[sb])
                df_out = df_out.T.join(df_startButtons[['date','time','event']].iloc[sb].T).T.sort_index()

                df_out.at[sbIdx,'project'] = proj
                df_out.at[sbIdx,'marker'] = 'Start Button'
                
            #approximate scan start time for computation of time deltas
            if not df_startButtons.empty:
                dt_startT = datetime.datetime.strptime(df_startButtons['time'].iloc[0], '%H:%M:%S.%f')


            #find all unique scan starts that follow button press
            df_scanPreps = df_redExam[df_redExam['event'].str.contains(r'(?=.*ScanSet\(SingleScan\):)(?=.*AwaitPreScan,)(?=.*to AwaitPreScan)(?=.*ReadyToRun)(?!.*B0_PreScan)(?!.*B1_Calibration)(?!.*PreScanCompleted,)',na=False,regex=True)]
            l_scanPrepIdx = df_scanPreps.index.to_list()
            for sp, spIdx in enumerate(l_scanPrepIdx):
                if spIdx == l_scanPrepIdx[-1]:
                    df_redScan = df_redExam.loc[spIdx:]
                else:
                    df_redScan = df.loc[spIdx:l_scanPrepIdx[sp+1]-1]
                

                #output to reduced dataframe
                # print('\nScan Preps')
                # print(df_scanPreps['date'].iloc[sp] + '\t' + df_scanPreps['time'].iloc[sp] + '\t' + df_scanPreps['event'].iloc[sp])
                df_out = df_out.T.join(df_scanPreps[['date','time','event']].iloc[sp].T).T.sort_index()

                scanName = df_scanPreps['event'].iloc[sp].split(',AwaitPreScan,')[1].split(',')[0]
                df_out.at[spIdx,'marker'] = scanName
                df_out.at[spIdx,'project'] = proj


                #look for scan start
                df_startScans = df_redScan[df_redScan['event'].isin([' Scan starts'])]
                l_startIdx = df_startScans.index.to_list()
                if l_startIdx:
                    for ss, ssIdx in enumerate(l_startIdx):
                
                        # print('\ndynamics')
                        # print(df_startScans['date'].iloc[ss] + '\t' + df_startScans['time'].iloc[ss] + '\t' + df_startScans['event'].iloc[ss])
                        df_out = df_out.T.join(df_startScans[['date','time','event']].iloc[ss].T).T.sort_index()
                        df_out.at[ssIdx,'marker'] = 'CDAS Scan Starts'
                        df_out.at[ssIdx,'project'] = proj


                #look for dynamics
                df_dynamicScans = df_redScan[df_redScan['event'].str.contains('Performing dynamic scan 1\.',na=False,regex=True)]
                l_dynamicIdx = df_dynamicScans.index.to_list()
                if l_dynamicIdx:
                    for dy, dyIdx in enumerate(l_dynamicIdx):
                
                        # print('\ndynamics')
                        # print(df_dynamicScans['date'].iloc[dy] + '\t' + df_dynamicScans['time'].iloc[dy] + '\t' + df_dynamicScans['event'].iloc[dy])
                        df_out = df_out.T.join(df_dynamicScans[['date','time','event']].iloc[dy].T).T.sort_index()
                        df_out.at[dyIdx,'marker'] = 'Dynamic 1'
                        df_out.at[dyIdx,'project'] = proj


                df_completedScans = df_redScan[df_redScan['event'].str.contains(r'(?=.*ScanSet\(SingleScan\):)(?=.*,AcqCompleted,' + scanName + ')',na=False,regex=True)]
                l_completedIdx = df_completedScans.index.to_list()
                if l_completedIdx:
                    for c, cIdx in enumerate(l_completedIdx):
                
                        # print('\nScan Complete')
                        # print(df_completedScans['date'].iloc[c] + '\t' + df_completedScans['time'].iloc[c] + '\t' + df_completedScans['event'].iloc[c])
                        if not cIdx in df_out.index:
                            df_out = df_out.T.join(df_completedScans[['date','time','event']].iloc[c].T).T.sort_index()
                            df_out.at[cIdx,'marker'] = 'Scan Complete'
                            df_out.at[cIdx,'project'] = proj



            #get project credentials
            if proj:
                st.read_credentials(proj)

                a = datetime.datetime.strptime(df_out['date'].iloc[0], '%Y-%m-%d')
                # ls_dirs = st.mysql_commands.sql_query_dirs(a.strftime('%Y%m%d'),False,False,inclusion='rawdata')
                if os.path.isfile(os.path.join(REALPATH,'processing_logs',a.strftime('%Y'),a.strftime('%Y%m') + '_scan_dates.json')):
                    with open(os.path.join(REALPATH,'processing_logs',a.strftime('%Y'),a.strftime('%Y%m') + '_scan_dates.json')) as f:
                        scanDates = json.load(f)
                
                ls_dirs = []
                if a.strftime('%Y%m%d') in scanDates.keys():
                    for k in scanDates[a.strftime('%Y%m%d')]:
                        k_split = k.split('_')
                        ls_dirs.append(os.path.join(st.creds.dataDir,'rawdata',k_split[0],k_split[1]))

                ls_newDirs = []
                for d in ls_dirs:
                    if os.path.isdir(d):
                        ls_newDirs.append(d)
                if not ls_newDirs:
                    continue

                #only 1 subject on this day
                if len(ls_newDirs) == 1:
                    if not os.path.isdir(os.path.join(ls_newDirs[0],'beh')):
                        os.makedirs(os.path.join(ls_newDirs[0],'beh'))
                    st.subject.get_id(ls_newDirs[0])
                    df_out.to_csv(os.path.join(ls_newDirs[0],'beh','sub-' + st.subject.id + '_ses-' + st.subject.fullSesNum + '_philips-scan-log.csv'))
                    print('\tSUB: ' + st.subject.id + ' SESSION: ' + st.subject.fullSesNum)

                else:
                    for d in ls_newDirs:
                        dt_t = None
                        jsonFiles = st.mysql_commands.sql_query(regex=d,searchtable=st.creds.searchTable,inclusion='json',searchcol='fullpath')
                        for j in jsonFiles:
                            with open(j) as f:
                                jsonData = json.load(f)
                            if 'PROJECTION' in jsonData['ImageType']:
                                continue
                            if 'AcquisitionTime' in jsonData.keys():
                                t = jsonData['AcquisitionTime']
                            if not dt_t:
                                dt_t = datetime.datetime.strptime(t, '%H:%M:%S.%f')
                            else:
                                dt_newt = datetime.datetime.strptime(t, '%H:%M:%S.%f')
                                diff = dt_newt - dt_t
                                if diff.days < 0:
                                    dt_t = dt_newt

                        #dt_t is the earliest scan
                        diff = dt_t - dt_startT
                        if diff.days < 0:
                            diff = dt_startT - dt_t
                        if diff.seconds < 60*15:
                            if not os.path.isdir(os.path.join(d,'beh')):
                                os.makedirs(os.path.join(d,'beh'))
                            st.subject.get_id(d)
                            df_out.to_csv(os.path.join(d,'beh','sub-' + st.subject.id + '_ses-' + st.subject.fullSesNum + '_philips-scan-log.csv'))
                            print('\tSUB: ' + st.subject.id + ' SESSION: ' + st.subject.fullSesNum)
                            break

    except OSError as e:
        print(e)
                    

       


if __name__ == '__main__':
    options = parse_arguments()
    connect_mri_system_log_grabber_p2(options.INLOGFILE)
