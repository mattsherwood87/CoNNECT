# functions.py
# the command above ^^^ sets python 3.10.10 as the interpreter for this program

# Created by Matthew Sherwood (matt.sherwood@wright.edu, matthew.sherwood.7.ctr@us.af.mil)
# Created on 21 Jan 2021
#
# v3.0.0 on 1 April 2023
# Modified on 20 Oct 2021 - elimination of mysql database in supplement of list bucket from boto3
# modified on 21 Jan 2021

import sys as _sys
import os as _os
import re as _re
import pandas as _pd


# REALPATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
# sys.path.append(REALPATH)
_REALPATH = _os.path.dirname(_os.path.dirname(_os.path.realpath(__file__)))
_sys.path.append(_REALPATH)





class subject:
    """
    Global Class Pattern for subject identifiers:
    Declare globals here.
    """
    def __init__(self):

        id = ""
        fullSesNum = ""
        sesNum = ""
        discard = False


    def get_id(self, singleDir: str):
        """
        Get subject and session identifiers from a BIDS filepath, and updates the helper_functions 'subject' class

        :param singleDir: BIDS-compliant filepath
        :type singleDir: str
        """

        self.id = _re.split(_os.sep + '|_',singleDir.split('sub-')[1])[0]
        self.fullSesNum = _re.split(_os.sep + '|_',singleDir.split('ses-')[1])[0]
        if '-' in self.fullSesNum:
            self.sesNum = self.fullSesNum.split('-')[1]
        else:
            self.sesNum = self.fullSesNum

    def check(self,dataDir: str):
        """        
        Check participants.tsv file to determine if the participant should be discarded (discard column is True). Requires support_tools.creds object to be complete (support_tools.creds.read(<project identifier>))

        :param dataDir: fullpath to a Project's data directory (support_tools.creds.dataDir)
        :type dataDir: str
        """        
        
        #get participants.tsv file
        groupIdFile = None    

        if _os.path.isfile(_os.path.join(dataDir,'rawdata','participants.tsv')):
            groupIdFile = _os.path.join(dataDir,'rawdata','participants.tsv')
        else:
            print('WARNING: no participants.tsv file, processing all subjects...')
            self.discard = False

        try:
            #read participants tsv file
            df_participants = _pd.read_csv(groupIdFile, sep='\t')
    
        except FileNotFoundError as e:
            print("Error Message: {0}".format(e))
            _sys.exit()

        #sort participants
        df_participants.sort_values(by=['participant_id'])

        try:
            if df_participants[df_participants['participant_id'] == 'sub-' + self.id].discard.item():
                self.discard = True
            else:
                self.discard = False
        except:
            self.discard = True