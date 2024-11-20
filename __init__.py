# __init__.py
import os
import sys
import json
import re
import pandas as pd

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 


REALPATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(REALPATH)

credentialsFilePath = os.path.join(REALPATH, "credentials.json")
with open(credentialsFilePath) as j:
    fullCredentials = json.load(j)

# from .get_dir_identifiers_new import get_dir_identifiers_new

from .bids_commands import *
from .convert_dicoms import convert_dicoms
from .copy_dirs import copy_dirs
from .condor import *
from .dti_flirt import dti_flirt
from .dti_preprocess import dti_preprocess
from .evaluate_raw_file_transfer import evaluate_raw_file_transfer
from .feat_full_firstlevel import feat_full_firstlevel
from .flirt_pngappend import flirt_pngappend
#from .flirt import flirt
from .fsreconall_stage1 import fsreconall_stage1
from .fsreconall_stage2 import fsreconall_stage2
# from .get_dir_identifiers import get_dir_identifiers
from .get_scan_id import get_scan_id
# from .old_versions.get_spec_base import get_spec_base
# from .id_check import id_check
from .mysql import *
from .prepare_examcard_html import prepare_examcard_html
# from .read_credentials import read_credentials
from .remove_dirs import remove_dirs
from .RestToolbox import *



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

        self.id = re.split(os.sep + '|_',singleDir.split('sub-')[1])[0]
        self.fullSesNum = re.split(os.sep + '|_',singleDir.split('ses-')[1])[0]
        if '-' in self.fullSesNum:
            self.sesNum = self.fullSesNum.split('-')[1]
        else:
            self.sesNum = self.fullSesNum

    def check(self):
        """
        Check participants.tsv file to determine if the participant should be discarded (discard column is True). Requires support_tools.creds object to be complete (support_tools.creds.read(<project identifier>))
        """        
        
        #get participants.tsv file
        groupIdFile = None    

        if os.path.isfile(os.path.join(st.creds.dataDir,'rawdata','participants.tsv')):
            groupIdFile = os.path.join(st.creds.dataDir,'rawdata','participants.tsv')
        else:
            print('WARNING: no participants.tsv file, processing all subjects...')
            self.discard = False

        try:
            #read participants tsv file
            df_participants = pd.read_csv(groupIdFile, sep='\t')
    
        except FileNotFoundError as e:
            print("Error Message: {0}".format(e))
            sys.exit()

        #sort participants
        df_participants.sort_values(by=['participant_id'])

        try:
            if df_participants[df_participants['participant_id'] == 'sub-' + self.id].discard.item():
                self.discard = True
            else:
                self.discard = False
        except:
            self.discard = True


class creds:
    """
    Global Class Pattern:
    Declare globals here.
    """
    def __init__(self):

        self.projects = fullCredentials['projects']
        self.masterMachineName = fullCredentials['master_machine_name']
        self.database = "CoNNECT"
        self.dataDir = ""
        self.dicom_id = ""
        self.examCardName = ""
        self.gpuMachineNames = ""
        self.gpuTempStorage = ""
        self.instance_id = ""
        self.ipAddress = ""
        self.machineNames = ""
        self.project = ""
        self.searchSourceTable = ""
        self.searchTable = ""
        self.dockerMountIf = ""


    def read(self, project: str):
        """
        Read the user's credential file 'credentials.json'.
        This file should be located /resshare/wsuconnect.

        This program returns the Project credentials into the custom creds class inside of the support_tools module, which should be imported prior to calling read().

        import support_tools as st
        st.creds.read(project)

        :param project: target Project's <project identifier>, defaults to None
        :type project: str

        :raises FileNotFoundError: when credentials.json cannot be read from disk
        """

        credentialsFilePath = os.path.join(REALPATH, "credentials.json")
        try:
            with open(credentialsFilePath) as j:
                fullCredentials = json.load(j)
                setattr(self,'projects',fullCredentials['projects'])
                if project in fullCredentials.keys():
                    for k in fullCredentials[project].keys():
                        if not '__comment__' in k:
                            setattr(self,k,fullCredentials[project][k])
    
        except FileNotFoundError as e:
            print("Error Message: {0}".format(e))


class specBase:

    def __init__(self):
        self.spectraName = ""
        self.subName = ""
        self.session = ""
        self.outBase = ""

    def get(self, specFile: str):
        """
        Get metadata from a MRS file

        This program returns the MRS file information into the custom specBase class inside of the support_tools module, which should be imported prior to calling read().

        import support_tools as st
        get_spec_base(specFile)

        :param specFile: fullpath to target MRS file
        :type specFile: str
        """

        self.specBase.outBase = os.path.splitext(os.path.basename(specFile))[0]
        base = self.specBase.outBase.split('sub-').split()
        self.specBase.subName = self.specBase.outBase.split('sub-')[1].split('_')[0]
        self.specBase.session = self.specBase.outBase.split('ses-')[1].split('_')[0]
        self.specBase.spectraName = self.specBase.outBase.split('acq-')[1].split('_')[0]


def import_flirt():
    from .old_versions.flirt import flirt


st.creds = st.creds()
st.subject = st.subject()
st.specBase = st.specBase()