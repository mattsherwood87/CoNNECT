#!/resshare/general_processing_codes/python3_venv/bin/python
# the command above ^^^ sets python 3.10.10 as the interpreter for this program

# Created by Matthew Sherwood (matt.sherwood@wright.edu, matthew.sherwood.7.ctr@us.af.mil)
# Created on 28 Dec 2020
# Last modified on 16 Sept 2021
#
#last modifications: remove copy commands that are unnecessary due to directly mounting s3 buckets

import os
from nipype.interfaces.dcm2nii import Dcm2niix
import argparse

parser = argparse.ArgumentParser('convert_dicoms.py: Command-line execution of DICOM to NIfTI conversion via dcm2niix. Converted NIfTI images are placed in the directory containing the imput sourcedata directory.')

# ******************* PARSE COMMAND LINE ARGUMENTS ********************
def parse_arguments():

    #input options for main()
    parser.add_argument('-s','--source',action='store',dest='source_singleDir',required=True,help='(str) fullpath to a sourcedata directory containing DICOM images')
    parser.add_argument('--progress',required=False,dest='progress',default=False,type=bool,help='(bool) run in verbose mode')
    return parser



# ******************* CONVERT DICOMS ********************
def convert_dicoms(source_singleDir,progress):
    """
    This function converts sourcedata DICOM images to NIfTI images in the input sourcedata directory. This function requires the installation of dcm2niix. Converted NIfTI images are placed in the directory containing the imput sourcedata directory.

    convert_dicoms(source_singleDir,progress=False)

    Arguments:

        source_singleDir (str): fullpath to a sourcedata directory containing DICOM images
            
        progress (BOOL): OPTIONAL flag to display command line output providing additional details on the processing status

    Returns:
        None
    """

    if os.path.isdir(source_singleDir):
        #setup dicom conversion to nifti
        converter = Dcm2niix()

        #setup dcm2niix inputs
        converter.inputs.source_dir = source_singleDir
        #converter.inputs.compression = 5
        converter.inputs.output_dir = os.path.dirname(source_singleDir)
        #converter.source_in_filename = 'y'
        converter.inputs.has_private = True
        converter.inputs.compress = 'y'
        converter.inputs.out_filename = '%f_%z_%s'
        #converter.inputs.ignore_deriv = True
        converter.inputs.ignore_deriv = False
        converter.inputs.verbose = progress

        

        #update progress if selected
        if progress:
            print('Converting dicoms in ' + converter.inputs.source_dir + ' to ' + converter.inputs.output_dir)

        #run conversion
        converter.run() 
    else:
        print('ERROR: cannot confirm input directory on disk')

def main():
    """
    The entry point of this program.
    """
    parser2 = parse_arguments()
    options = parser2.parse_args()
    convert_dicoms(options.source_singleDir,options.progress)


if __name__ == '__main__':
    main()
