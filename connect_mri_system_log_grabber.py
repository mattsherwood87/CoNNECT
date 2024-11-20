#!/resshare/wsuconnect/python3_venv/bin/python
# the command above ^^^ sets python 3.10.10 as the interpreter for this program

# Created by Matthew Sherwood (matt.sherwood@wright.edu, matthew.sherwood.7.ctr@us.af.mil)
# Created on 30 Mar 2023
#
# Last Modified on 17 July 2023 - added system_log_grabber_p2

# ******* IMPORTS ***********
from cmath import inf
import os
import argparse
import shutil
import datetime
# import numpy as np
# import math
import time
from glob import glob
# from pathlib import Path


# ******* LOCAL IMPORTS ******
#sys.path.append(os.path.abspath(os.path.join(os.environ['SCRATCH_DIR'],'python')))
#from helper_functions.convert_dicoms import convert_dicoms


# ******* GLOBAL INFO *******
#versioning
VERSION = '1.1.0'
DATE = '17 July 2023'


#GLOBALS
REALPATH = os.path.dirname(os.path.realpath(__file__))
from connect_mri_system_log_grabber_p2 import connect_mri_system_log_grabber_p2

# ******************* PARSE COMMAND LINE ARGUMENTS ********************
parser = argparse.ArgumentParser()
parser.add_argument('-v', '--version', action="store_true", dest="version", help="Display the current version")



# ******************* MAIN ********************
def main():
    """
    The entry point of this program.
    """

    #get and evaluate options
    logPath = "/Log"
    if not os.path.ismount(logPath):
        os.system('mount -a')

    #get today's date
    currentDateTime = datetime.datetime.now()

    #convert to yesterday
    currentDateTime = currentDateTime.replace(day=currentDateTime.day - 1)
    prevDay = currentDateTime.strftime('%Y%m%d')
    prevDayYear = currentDateTime.strftime('%Y')

    try:
        #Check for input file
        if os.path.isfile(os.path.join(logPath, 'log' + prevDay + '0000.log')):
            destPath = os.path.join(os.path.dirname(REALPATH),'Philips_system_logs',prevDayYear)
            if not os.path.isdir(destPath):
                 os.makedirs(destPath)

            if os.path.isfile(os.path.join(logPath,'log' + prevDay + '0001.log')):
                os.system(' '.join(['cat',
                                   os.path.join(logPath, 'log' + prevDay + '0000.log'),
                                   os.path.join(logPath, 'log' + prevDay + '0001.log'),
                                   '>',
                                   os.path.join(destPath, 'log' + prevDay + '0000.log')
                                   ]))
            else:
                shutil.copy2(os.path.join(logPath, 'log' + prevDay + '0000.log'),os.path.join(destPath,'log' + prevDay + '0000.log'))
            print('connect_mri_system_log_grabber.py:\n\tINPUT: ' + os.path.join(logPath, 'log' + prevDay + '0000.log') + '\n\tOUTPUT: ' + os.path.join(destPath,'log' + prevDay + '0000.log'))
            print('\tON: ' + str(currentDateTime))

            connect_mri_system_log_grabber_p2(os.path.join(destPath,'log' + prevDay + '0000.log'))

                        
    except OSError as e:
        print(e)
                


if __name__ == '__main__':
    main()
