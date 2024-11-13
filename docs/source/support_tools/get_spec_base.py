#!/usr/bin/env python3
# the command above ^^^ sets python 3.10.10 as the interpreter for this program

# Created by Matthew Sherwood (matt.sherwood@wright.edu, matthew.sherwood.7.ctr@us.af.mil)
# Created on 16 Sept 2021
#
# 

import os
import sys

#local import
from classes.specBase import *


def get_spec_base(specFile):
    """
    Get metadata from a MRS file

    This program returns the MRS file information into the custom specBase class, which should be imported prior to calling get_sspec_base

    get_spec_base(specFile)

    Arguments:

        specFile (str): target MRS file

    Returns:
        None
    """

    specBase.outBase = os.path.splitext(os.path.basename(specFile))[0]
    base = specBase.outBase.split('sub-').split()
    specBase.subName = specBase.outBase.split('sub-')[1].split('_')[0]
    specBase.session = specBase.outBase.split('ses-')[1].split('_')[0]
    specBase.spectraName = specBase.outBase.split('acq-')[1].split('_')[0]
    