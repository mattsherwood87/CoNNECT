#!/resshare/general_processing_codes/python3_venv/bin/python
# the command above ^^^ sets python 3.10.10 as the interpreter for this program

# Created by Matthew Sherwood (matt.sherwood@wright.edu, matthew.sherwood.7.ctr@us.af.mil)
# Created on 16 Sept 2021
#
# v2.0.0 on 1 April 2023 - simplify code

import os
import re

def get_dir_identifiers(singleDir):
    """
    Get subject and session identifiers from a BIDS filepath

    Arguments:
        singleDir (str): BIDS-compliant filepath

    Returns:
        str: subject identifier, returns XXX in sub-XXX

        str: session identifier, returns YYY in ses-YYY
    """

    subjectName = re.split(os.sep + '|_',singleDir.split('sub-')[1])[0]
    sessionNum = re.split(os.sep + '|_',singleDir.split('ses-')[1])[0]

    return subjectName,sessionNum