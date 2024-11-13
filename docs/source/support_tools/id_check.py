#!/resshare/general_processing_codes/python3_venv/bin/python
# the command above ^^^ sets python 3.10.10 as the interpreter for this program

# Created by Matthew Sherwood (matt.sherwood@wright.edu, matthew.sherwood.7.ctr@us.af.mil)
# Created on 22 Jan 2024
#
# Modified on 

import os
# import pymysql
import argparse
import sys
import csv
import pandas as pd
import numpy as np


REALPATH = os.path.join('/resshare','general_processing_codes')
sys.path.append(REALPATH)

from classes.creds import *
from helper_functions.bids_commands import *

# FSLDIR = os.environ["FSLDIR"]
FSLDIR = '/usr/local/fsl'
os.environ["FSLDIR"] = '/usr/local/fsl'
os.system('FSLDIR=' + os.environ["FSLDIR"])




# ******************* MAIN ********************
def id_check(subName):
    """
    The entry point of this program.
    """
    

    #get participants.tsv file
    groupIdFile = None    

    if os.path.isfile(os.path.join(creds.dataDir,'rawdata','participants.tsv')):
        groupIdFile = os.path.join(creds.dataDir,'rawdata','participants.tsv')
    else:
        print('WARNING: no participants.tsv file, processing all subjects...')
        return True

    try:
        #read participants tsv file
        df_participants = pd.read_csv(groupIdFile, sep='\t')
   
    except FileNotFoundError as e:
        print("Error Message: {0}".format(e))
        sys.exit()

    #sort participants
    df_participants.sort_values(by=['participant_id'])

    

    try:
        if df_participants[df_participants['participant_id'] == 'sub-' + subName].discard.item():
            return False
        else:
            return True
    except:
        return False
