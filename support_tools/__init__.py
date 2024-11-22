# __init__.py
import os as _os
import sys as _sys
import json as _json
import re as _re
import pandas as _pd

_os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 


_REALPATH = _os.path.dirname(_os.path.dirname(_os.path.realpath(__file__)))
_sys.path.append(_REALPATH)

_credentialsFilePath = _os.path.join(_REALPATH, "credentials.json")
with open(_credentialsFilePath) as _j:
    _fullCredentials = _json.load(_j)

# from .get_dir_identifiers_new import get_dir_identifiers_new

from . import bids
from . import condor
# from . import creds
from . import RestToolbox

from .creds import creds
from .convert_dicoms import convert_dicoms
from .copy_dirs import copy_dirs
from .dti_flirt import dti_flirt
from .dti_preprocess import dti_preprocess
from .evaluate_raw_file_transfer import evaluate_raw_file_transfer
from .feat_full_firstlevel import feat_full_firstlevel
from .flirt_pngappend import flirt_pngappend
from .fsreconall_stage1 import fsreconall_stage1
from .fsreconall_stage2 import fsreconall_stage2
from .get_scan_id import get_scan_id
from . import mysql
from .prepare_examcard_html import prepare_examcard_html
from .remove_dirs import remove_dirs
from .subject import subject


creds = creds()
subject = subject()
creds.projects = _fullCredentials['projects']
creds.masterMachineName = _fullCredentials['master_machine_name']


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

        self.outBase = _os.path.splitext(_os.path.basename(specFile))[0]
        base = self.outBase.split('sub-').split()
        self.subName = self.outBase.split('sub-')[1].split('_')[0]
        self.session = self.outBase.split('ses-')[1].split('_')[0]
        self.spectraName = self.outBase.split('acq-')[1].split('_')[0]


def import_flirt():
    from .flirt import flirt


# st.creds = st.creds()
specBase = specBase()


__all__ = ['bids','convert_dicoms','copy_dirs','condor','dti_flirt','dti_preprocess','evaluate_raw_file_transfer','feat_full_firstlevel','flirt_pngappend','fsreconall_stage1','fsreconall_stage2','get_scan_id','mysql','prepare_examcard_html','remove_dirs','RestToolbox','creds','subject','specBase','import_flirt']