#!/resshare/general_processing_codes/python3_venv/bin/python
# the command above ^^^ sets python 3.10.10 as the interpreter for this program

# Created by Matthew Sherwood (matt.sherwood@wright.edu, matthew.sherwood.7.ctr@us.af.mil)
# Created on 31 Jan 2023
#
# Last Modified on - 

# ******* IMPORTS ***********
from cmath import inf
import math
import os
import pydicom 
import argparse
import json
import pandas as pd
import shutil
from datetime import datetime, timedelta
import numpy as np
import tkinter as tk
from tkinter import filedialog
from glob import glob
import math


# ******* LOCAL IMPORTS ******
#sys.path.append(os.path.abspath(os.path.join(os.environ['SCRATCH_DIR'],'python')))
#from helper_functions.convert_dicoms import convert_dicoms
import helper_functions as hf


# ******* GLOBAL INFO *******
#versioning
VERSION = '1.0.1'
DATE = '31 Jan 2023'

REALPATH = os.path.dirname(os.path.realpath(__file__))

#input argument parser
parser = argparse.ArgumentParser()

# ******************* PARSE COMMAND LINE ARGUMENTS ********************
def parse_arguments():

    #input options for main()
    # requiredNamed = parser.add_argument_group('required arguments')
    # requiredNamed.add_argument('-p','--path', action="store", dest="PATH", help="define search path", default=None)
    parser.add_argument('-v', '--version', action="store_true", dest="version", help="Display the current version")
    # parser.add_argument('--progress', action="store_true", dest="progress", help="Show progress (default FALSE)", default=False)
    options = parser.parse_args()

    return options

def round_dt(dt, delta):
    return datetime.min + math.ceil((dt - datetime.min) / delta) * delta

def string_convert(str_to_convert):
    return str(str_to_convert)

def time_convert(time_to_convert):
    if len(time_to_convert) > 19:
        return datetime.strptime(time_to_convert, '%Y-%m-%d %H:%M:%S.%f')
    else:
        return datetime.strptime(time_to_convert, '%Y-%m-%d %H:%M:%S')

# ******************* MAIN ********************
def main():
    """
    The entry point of this program.
    """

    #get and evaluate options
    # options = parse_arguments()
    # basePath = "/"
    # r = tk.Tk()
    # r.withdraw()

    # #select and read file
    # inFile = filedialog.askopenfilename(initialdir=REALPATH)

    #need to put cancellation check in place
    baseDir = '/resshare19/projects/2023_UES/EPIC/rawdata'

    inDirs = sorted([x[0] for x in os.walk(baseDir) if 'ses' in os.path.basename(x[0])])

    df_Out = pd.DataFrame(columns=['project','subject','session','start_time','end_time','scan_duration_mins','mri_usage_mins'])
    lastSesNum = 'B'
    b_concat = False
    lastSub = None

    for inDir in inDirs:
        files = glob(os.path.join(inDir,'**','*.json'),recursive=True)
        hf.get_dir_identifiers_new(inDir)

        if 'A' in hf.subject.sesNum or '5' in hf.subject.sesNum:
            b_concat = False
            initLoop = True
            if 'A' in lastSesNum:
                endTime = endTime + timedelta(seconds=lastDur)
                tdelta = endTime - startTime

                tdelta_mins = math.ceil(tdelta.seconds/60)
                totalDur = math.ceil((tdelta_mins + 5)/15) * 15

                df_tmp = pd.DataFrame.from_dict({'project':['20230093H'],'subject':lastSub,'session':lastSesNum[0],'start_time':[startTime.strftime('%H:%M:%S.%f')],'end_time':[endTime.strftime('%H:%M:%S.%f')],'scan_duration_mins':[tdelta_mins],'mri_usage_mins':[totalDur]})

                df_Out = pd.concat([df_Out,df_tmp],ignore_index=True)

        if 'B' in hf.subject.sesNum or '5' in hf.subject.sesNum:
            b_concat = True

        for fi in files:

            with open(fi) as f:
                data = json.load(f)
            
            if not 'AcquisitionTime' in data.keys():
                print(fi)
                continue
            acqTime = datetime.strptime(data['AcquisitionTime'],'%H:%M:%S.%f')
            if initLoop:
                initLoop = False
                startTime = acqTime
                endTime = acqTime
                if not 'AcquisitionDuration' in data.keys():
                    lastDur = 150
                else:
                    lastDur = data['AcquisitionDuration']
            else:
                if acqTime < startTime:
                    startTime = acqTime
                if acqTime > endTime:
                    endTime = acqTime
                if not 'AcquisitionDuration' in data.keys():
                    lastDur = 150
                else:
                    if '10min' in data['ProtocolName']:
                        lastDur = 600
                    elif 'ASL' in data['ProtocolName']:
                        lastDur = 180
                    else:
                        lastDur = data['AcquisitionDuration']

        if b_concat:
            endTime = endTime + timedelta(seconds=lastDur)
            tdelta = endTime - startTime

            tdelta_mins = math.ceil(tdelta.seconds/60)
            totalDur = math.ceil((tdelta_mins + 10)/15) * 15

            df_tmp = pd.DataFrame.from_dict({'project':['20230093H'],'subject':[hf.subject.id],'session':[hf.subject.sesNum[0]],'start_time':[startTime.strftime('%H:%M:%S.%f')],'end_time':[endTime.strftime('%H:%M:%S.%f')],'scan_duration_mins':[tdelta_mins],'mri_usage_mins':[totalDur]})

            df_Out = pd.concat([df_Out,df_tmp],ignore_index=True)

        lastSesNum = hf.subject.sesNum
        lastSub = hf.subject.id

    df_Out.to_csv(os.path.join(os.path.dirname(baseDir),'scan_durations.csv'))





    # inFileBasename = os.path.basename(inFile).split('.')[0]
    # if os.path.isfile(os.path.join(os.path.dirname(inFile),inFileBasename + '_usage_by_scan.csv')):
    #     os.remove(os.path.join(os.path.dirname(inFile),inFileBasename + '_usage_by_scan.csv'))


    # dfIn = pd.read_csv(inFile)

    # #drop unncessary columns, remove duplicates
    # dfIn.sort_values(['acquisition_date','acquisition_start','protocol_name','instance_number'], inplace=True)
    # dfIn.drop(['input_filename','output_filename','processed_date','processed_time','instance_number'], axis=1, inplace=True)
    

    # #remove duplicates
    # dfIn.drop_duplicates(keep='first', inplace=True, ignore_index=True)

    # #extract series number to remove excess scans
    # a=dfIn.loc[:,['subject','series_number','protocol_name','acquisition_date','series_start','series_end']]
    # a = a[a['protocol_name'].str.contains("SOURCE") == False]
    # a = a[a['protocol_name'].str.contains("mpr") == False]
    # a = a[a['protocol_name'].str.contains("MPR") == False]
    # a.drop(['protocol_name'], axis=1, inplace=True)
    # a.drop_duplicates(keep='first',inplace=True)
    # dfIn = dfIn.loc[a.index]
    # dfIn = dfIn.reset_index()

    # #convert acquisition start time to a datetime object
    # dfIn['acquisition_start'] = dfIn['series_start']
    # #dfIn['acquisition_start_time'] = dfIn['acquisition_start_time'].apply(time_convert)
    # # dfIn.drop(['acquisition_start_str'])
    # acq_start=0
    # acq_end=0

    # #get "Head Plan" scan indicies and loop 
    # startFlag = True
    # d = dfIn.loc[dfIn['protocol_name'].isin(['Head Plan','WIP Head Plan','Quick Plan','WIP Quick Plan'])]
    # for idx, r in d.iterrows():
    #     if startFlag:
    #         startFlag = False
    #         #grab starting parameters
    #         acq_start = r['acquisition_start']
    #         acq_start = time_convert(acq_start)
    #         proj = r['project']
    #         sub = r['subject']
    #         acq_date = r['acquisition_date']

    #     else:
    #         #get end time and calculate total scan duration from last scan
    #         acq_end = dfIn.loc[idx-1,'series_end']
    #         acq_end = time_convert(acq_end)
    #         #dur = dfIn.loc[idx-1,'acquisition_duration']
    #         #acq_end = acq_end + datetime.timedelta(0,dur)

    #         diff = acq_end - acq_start
    #         hr_diff = (diff.days * (24*60*60) + diff.seconds) / (60*60)

    #         usageTime_hrDiff = math.ceil(hr_diff*4)/4
    #         if abs(usageTime_hrDiff - hr_diff) < 5/60:
    #             usageTime_hrDiff = usageTime_hrDiff + 0.25

    #         df_tmp = {'project':proj, 'subject':sub, 'acquisition_date':acq_date, 'acq_start':acq_start.strftime('%H%M%S.%f'), 'acquisition_end':acq_end.strftime('%H%M%S.%f'), 'total_scan_time_hrs':hr_diff, 'usage_time_hrs':usageTime_hrDiff}
    #         df_tmp = pd.DataFrame(df_tmp, index=[0])

    #         #write dataframe to csv
    #         if os.path.isfile(os.path.join(os.path.dirname(inFile),inFileBasename + '_usage_by_scan.csv')):
    #             df_tmp.to_csv(os.path.join(os.path.dirname(inFile),inFileBasename + '_usage_by_scan.csv'), index=False, mode='a', header=False)
    #         else:
    #             df_tmp.to_csv(os.path.join(os.path.dirname(inFile),inFileBasename + '_usage_by_scan.csv'), index=False)

    #         #grab new starting parameters
    #         acq_start = r['acquisition_start']
    #         acq_start = time_convert(acq_start)
    #         proj = r['project']
    #         sub = r['subject']
    #         acq_date = r['acquisition_date']

    # #get end time and calculate total scan duration from last scan
    # acq_end = dfIn['series_end'].tail(1).tolist()[0]#dfIn.loc[len(dfIn)-1,'acquisition_duration']
    # acq_end = time_convert(acq_end)
    # #dur = dfIn['acquisition_duration'].tail(1).tolist()[0]
    # #acq_end = acq_end + datetime.timedelta(0,dur)

    # diff = acq_end - acq_start
    # hr_diff = (diff.days * (24*60*60) + diff.seconds) / (60*60)

    # usageTime_hrDiff = math.ceil(hr_diff*4)/4
    # if abs(usageTime_hrDiff - hr_diff) < 5/60:
    #     usageTime_hrDiff = usageTime_hrDiff + 0.25

    # df_tmp = {'project':proj, 'subject':sub, 'acquisition_date':acq_date, 'acq_start':acq_start.strftime('%H%M%S.%f'), 'acquisition_end':acq_end.strftime('%H%M%S.%f'), 'total_scan_time_hrs':hr_diff, 'usage_time_hrs':usageTime_hrDiff}
    # df_tmp = pd.DataFrame(df_tmp, index=[0])

    # #write dataframe to csv
    # inFileBasename = os.path.basename(inFile).split('.')[0]
    # if os.path.isfile(os.path.join(os.path.dirname(inFile),inFileBasename + '_usage_by_scan.csv')):
    #     df_tmp.to_csv(os.path.join(os.path.dirname(inFile),inFileBasename + '_usage_by_scan.csv'), index=False, mode='a', header=False)
    # else:
    #     df_tmp.to_csv(os.path.join(os.path.dirname(inFile),inFileBasename + '_usage_by_scan.csv'), index=False)



    # #write to a file
    # inFileBasename = os.path.basename(inFile).split('.')[0]
    # dfIn.to_csv(os.path.join(os.path.dirname(inFile),inFileBasename + '_modified.csv'), index=False)


    


if __name__ == '__main__':
    main()
