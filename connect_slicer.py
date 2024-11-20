#!/resshare/general_processing_codes/python3_venv/bin/python
# the command above ^^^ sets python 3.10.10 as the interpreter for this program

# Created by Matthew Sherwood (matt.sherwood@wright.edu, matthew.sherwood.7.ctr@us.af.mil)
# Created on 27 July 2023
#
# Modified on 7 Feb 2024 - added condor job support

import os
# import pymysql
import argparse
import sys
import pandas as pd
import numpy as np
from glob import glob as glob
import datetime
import subprocess


#local import
REALPATH = os.path.dirname(os.path.realpath(__file__))
sys.path.append(REALPATH)



# GLOBAL INFO
#versioning
VERSION = '1.0.0'
DATE = '15 July 2024'


FSLDIR = os.environ["FSLDIR"]


#input argument parser
parser = argparse.ArgumentParser()

# ******************* PARSE COMMAND LINE ARGUMENTS ********************
def parse_arguments():

    #input options for main()
    requiredNamed = parser.add_argument_group('required arguments')
    requiredNamed.add_argument('-i','--in', required=True, action="store", dest="INFILE", help="input file to overlay and slice", default=None)
    parser.add_argument('--start', action="store", dest="START", type=int, help="Start slice number, default 0", default=None)
    parser.add_argument('--end', action="store", dest="END", type=int, help="End slice number, default all slices", default=None)
    parser.add_argument('-l','--lower', action="store", dest="LOWER", type=float, help="lower threshold for overlay, default 2.3", default=2.3)
    parser.add_argument('-u','--upper', action="store", dest="UPPER", type=float, help="upper threshold for overlay, default 4.5", default=4.5)
    parser.add_argument('--ref', action="store", dest="REF", help="Reference image, default FSL MNI T1 2mm brain", default="${FSLDIR}/data/standard/MNI152_T1_2mm_brain")
    parser.add_argument('--lut', action="store", dest="LUT", help="Colormap LUT, must be in $FSLDIR/etc/luts, default render1.lut", default="${FSLDIR}/etc/luts/render1.lut")
    parser.add_argument('-v', '--version', action="store_true", dest="version", help="Display the current version")
    parser.add_argument('--progress', action="store_true", dest="progress", help="Show progress (default FALSE)", default=False)
    options = parser.parse_args()

    

    return options


# ******************* EVALUATE COMMAND LINE ARGUMENTS ********************
# def evaluate_args(options):
    
#     #SEARCHTABLE=None
#     groupIdFile = None    

#     if os.path.isfile(os.path.join(creds.dataDir,'rawdata','participants.tsv')):
#         groupIdFile = os.path.join(creds.dataDir,'rawdata','participants.tsv')

#     segstatsInputFile = os.path.join(creds.dataDir,'code',options.PROJECT + '_extract_segstats_input.json')
#     if not os.path.isfile(segstatsInputFile):
#         return

#     with open(segstatsInputFile) as j:
#         segstatsInput = json.load(j)


#     return groupIdFile, segstatsInput



# ******************* MAIN ********************
def main():
    """
    The entry point of this program.
    """
    #read crendentials from $SCRATCH_DIR/instance_ids.json

    #get and evaluate options
    options = parse_arguments()

    
        
    d = os.path.dirname(options.INFILE)
    b = os.path.basename(options.INFILE)
    newFile = os.path.join(d,'render_' + b)
    os.system(' '.join([os.path.join(FSLDIR,'bin','overlay'), '1 0', options.REF, '3000 8500', options.INFILE, str(options.LOWER), str(options.UPPER), newFile]))

    #get input dims
    dims = []
    for di in ['dim1','dim2','dim3']:
        proc = subprocess.check_output(' '.join([os.path.join(FSLDIR,'bin','fslval'), options.INFILE, di]),shell=True,encoding='utf-8')
        dims.append(int(proc.split(' ')[0]))


    for plane in ['axial','sagittal','coronal']:
        if plane == 'axial':
            dim = dims[2]
            pl = 'z'
        elif plane == 'sagittal':
            dim = dims[0]
            pl = 'x'
        elif plane == 'coronal':
            dim = dims[1]
            pl = 'y'

        if not options.START:
             options.START = 0
        if not options.END:
             options.END = dim

        for slice in range(options.START,options.END):
            sliceNum = slice/dim
            outPng = os.path.join(d,os.path.basename(newFile).split('.')[0],plane,'%s_%s%03d_thr-%s-%s.png' %(b.split('.')[0], pl, slice, "{:.2f}".format(options.LOWER).replace('.','p'),"{:.2f}".format(options.UPPER).replace('.','p')))
            # print(outPng)

            if not os.path.isdir(os.path.dirname(outPng)):
                 os.makedirs(os.path.dirname(outPng))
            os.system(' '.join([os.path.join(FSLDIR,'bin','slicer'), '-l', options.LUT, '-u', newFile, '-s', '4', '-' + pl, str(sliceNum), outPng]))
         


             

            

       
    

if __name__ == '__main__':
    main()
