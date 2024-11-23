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


from . import bids
from . import condor
from . import mysql
from . import RestToolbox
from . import subject
from .convert_dicoms import convert_dicoms
from .copy_dirs import copy_dirs
from .creds import creds
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
from .prepare_examcard_html import prepare_examcard_html
# from .read_credentials import read_credentials
from .remove_dirs import remove_dirs


creds = creds()
creds.projects = fullCredentials['projects']
creds.masterMachineName = fullCredentials['masterMachineName']
subject=subject()


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
    from .flirt import flirt


specBase = specBase()