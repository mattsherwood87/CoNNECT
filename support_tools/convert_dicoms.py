#!/resshare/wsuconnect/python3_venv/bin/python
# the command above ^^^ sets python 3.10.10 as the interpreter for this program

# Created by Matthew Sherwood (matt.sherwood@wright.edu, matthew.sherwood.7.ctr@us.af.mil)
# Created on 28 Dec 2020
#
# Modified on 15 Nov 2024 - argparse updates for documentation
# Modified on 16 Sep 2021 - remove copy commands that are unnecessary due to directly mounting s3 buckets

import os
from nipype.interfaces.dcm2nii import Dcm2niix
import argparse

#versioning
VERSION = '2.0.1'
DATE = '15 Nov 2024'

# ******************* PARSE COMMAND LINE ARGUMENTS ********************
parser = argparse.ArgumentParser('convert_dicoms.py: Command-line execution of DICOM to NIfTI conversion via dcm2niix. Converted NIfTI images are placed in the directory containing the imput sourcedata directory.')
parser.add_argument('-i','--in-dir',required=True, action='store',dest='INDIR',help='(str) fullpath to a sourcedata directory containing DICOM images')
parser.add_argument('--progress',required=False,action='store_true',dest='PROGRESS',help='(bool) run in verbose mode')




# ******************* CONVERT DICOMS ********************
def convert_dicoms(INDIR: str,PROGRESS: bool=False):
    """
    This function converts sourcedata DICOM images to NIfTI images in the input sourcedata directory. This function requires the installation of dcm2niix. Converted NIfTI images are placed in the directory containing the imput sourcedata directory.

    convert_dicoms(INDIR,PROGRESS=False)

    :param INDIR: fullpath to a sourcedata directory containing DICOM images for conversion
    :type INDIR: str

    :param PROGRESS: flag to display command line output providing additional details on the processing status, defaults to False
    :type PROGRESS: bool, optional
    """

    if os.path.isdir(INDIR):
        #setup dicom conversion to nifti
        converter = Dcm2niix()

        #setup dcm2niix inputs
        converter.inputs.source_dir = INDIR
        #converter.inputs.compression = 5
        # converter.inputs.output_dir = os.path.dirname(INDIR)
        converter.inputs.output_dir = INDIR
        #converter.source_in_filename = 'y'
        converter.inputs.has_private = True
        converter.inputs.compress = 'y'
        converter.inputs.out_filename = '%f_%z_%s'
        #converter.inputs.ignore_deriv = True
        converter.inputs.ignore_deriv = False
        converter.inputs.verbose = PROGRESS

        

        #update progress if selected
        if PROGRESS:
            print('Converting dicoms in ' + converter.inputs.source_dir + ' to ' + converter.inputs.output_dir)

        #run conversion
        converter.run() 
    else:
        print('ERROR: cannot confirm input directory on disk')



if __name__ == '__main__':
    """
    The entry point of this program for command-line utilization.
    """
    options = parser.parse_args()
    # print('Converting dicoms in ' + options.INDIR + ' to ')
    convert_dicoms(options.INDIR,options.PROGRESS)