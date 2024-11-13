#!/resshare/general_processing_codes/python3_venv/bin/python
# the command above ^^^ sets python 3.10.10 as the interpreter for this program

# Created by Matthew Sherwood (matt.sherwood@wright.edu, matthew.sherwood.7.ctr@us.af.mil)
# Created on 23 Dec 2020
#
# Modified on 22 Nov 2021 - added new revised support of creds class

import os
import json
import sys


# REALPATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
# sys.path.append(REALPATH)
REALPATH = os.path.join('/resshare','general_processing_codes')
sys.path.append(REALPATH)

import helper_functions as hf

#versioning
VERSION = '1.0.2'
DATE = '1 April 2023'

def read_credentials(project):
    """
    Read the user's credential file 'credentials.json'.
    This file should be located /resshare/general_processing_codes.

    This program returns the Project credentials into the custom creds class, which should be imported prior to calling read_credentials

    read_credentials(project)

    Arguments:

        project (str): target Project's <project identifier>

    Returns:
        None
    """

    credentialsFilePath = os.path.join(REALPATH, "credentials.json")
    try:
        with open(credentialsFilePath) as j:
            fullCredentials = json.load(j)
            setattr(hf.creds,'projects',fullCredentials['projects'])
            if project in fullCredentials.keys():
                for k in fullCredentials[project].keys():
                    if not '__comment__' in k:
                        setattr(hf.creds,k,fullCredentials[project][k])
   
    except FileNotFoundError as e:
        print("Error Message: {0}".format(e))

