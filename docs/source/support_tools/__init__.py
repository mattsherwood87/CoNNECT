# __init__.py
import os
import sys
import json

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 


REALPATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(REALPATH)

credentialsFilePath = os.path.join(REALPATH, "credentials.json")
with open(credentialsFilePath) as j:
    fullCredentials = json.load(j)

from .get_dir_identifiers_new import get_dir_identifiers_new

from .bids_commands import *
from .convert_dicoms import convert_dicoms
from .copy_dirs import copy_dirs
from .create_bin_condor_job import create_bin_condor_job
from .create_freesurfer_condor_job import create_freesurfer_condor_job
from .create_fsl_condor_job import create_fsl_condor_job
from .create_python_condor_job import create_python_condor_job
from .dti_flirt import dti_flirt
from .dti_preprocess import dti_preprocess
from .evaluate_raw_file_transfer import evaluate_raw_file_transfer
from .feat_full_firstlevel import feat_full_firstlevel
from .flirt_pngappend import flirt_pngappend
#from .flirt import flirt
from .fsreconall_stage1 import fsreconall_stage1
from .fsreconall_stage2 import fsreconall_stage2
from .get_dir_identifiers import get_dir_identifiers
from .get_scan_id import get_scan_id
from .get_spec_base import get_spec_base
from .id_check import id_check
from .mysql_commands import *
from .prepare_examcard_html import prepare_examcard_html
from .read_credentials import read_credentials
from .remove_dirs import remove_dirs
from .RestToolbox import *



class subject:
    """
    Global Class Pattern:
    Declare globals here.
    """

    id = ""
    fullSesNum = ""
    sesNum = ""


class creds:
    """
    Global Class Pattern:
    Declare globals here.
    """

    projects = fullCredentials['projects']
    masterMachineName = fullCredentials['master_machine_name']
    database = "CoNNECT"
    dataDir = ""
    dicom_id = ""
    examCardName = ""
    gpuMachineNames = ""
    gpuTempStorage = ""
    instance_id = ""
    ipAddress = ""
    machineNames = ""
    project = ""
    searchSourceTable = ""
    searchTable = ""


class specBase:
    """
    Global Class Pattern:
    Declare globals here.
    """
    spectraName = ""
    subName = ""
    session = ""
    outBase = ""