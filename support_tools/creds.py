#!/usr/bin/env python3
# the command above ^^^ sets python 3.10.10 as the interpreter for this program

# Copywrite: Matthew Sherwood (matt.sherwood@wright.edu, matthew.sherwood.7.ctr@us.af.mil)
# Created on 23 Dec 2020

#versioning
_VERSION = '2.0.1'
_DATE = '21 Nov 2024'
import os as _os
import json as _json

_REALPATH = _os.path.dirname(_os.path.dirname(_os.path.realpath(__file__)))


class creds:
    """
    Global Class Pattern:
    Declare globals here.
    """
    def __init__(self):

        self.projects = ""
        self.masterMachineName = ""
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
        # self.read()

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

        credentialsFilePath = _os.path.join(_REALPATH, "credentials.json")
        try:
            with open(credentialsFilePath) as j:
                fullCredentials = _json.load(j)
                setattr(self,'projects',fullCredentials['projects'])
                if project in fullCredentials.keys():
                    for k in fullCredentials[project].keys():
                        if not '__comment__' in k:
                            setattr(self,k,fullCredentials[project][k])
    
        except FileNotFoundError as e:
            print("Error Message: {0}".format(e))

