#!/resshare/general_processing_codes/python3_venv/bin/python
# the command above ^^^ sets python 3.10.9 as the interpreter for this program

# Created by Matthew Sherwood (matt.sherwood@wright.edu, matthew.sherwood.7.ctr@us.af.mil)
# Created on 19 July 2023
#
# Modified on 17 May 2024 - added pymeshlab support and stl generation

import sys
import os
import argparse
import json
import pymeshlab
from nipype.interfaces import freesurfer
from glob import glob as glob
import datetime

#local import
# REALPATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
# sys.path.append(REALPATH)
REALPATH = os.path.join('/resshare','general_processing_codes')
sys.path.append(REALPATH)
from helper_functions.flirt_pngappend import *
from helper_functions.get_dir_identifiers import *
from helper_functions.bids_commands import *


VERSION = '1.1.0'
DATE = '17 May 2024'


parser = argparse.ArgumentParser('asl_flirt.py: perform FLIRT registration between 2D ASL and structural/standard brain images')
FSLDIR = os.environ["FSLDIR"]

# s3 = boto3.resource('s3')

def parse_arguments():

    #input options for main()
    parser.add_argument('STAGE1_DIR')
    parser.add_argument('DATA_DIR')
    parser.add_argument('RECONALL_PARAMS')
    parser.add_argument('--overwrite',action='store_true',dest='OVERWRITE',default=False)
    parser.add_argument('--progress',action='store_true',dest='progress',default=False)
    options = parser.parse_args()
    return options


class InvalidJsonInput(Exception):
    "Raised when the input JSON control file does not contain the appropriate mandatory definitions"
    pass


# ******************* s3 bucket check ********************
def fsreconall_stage2(STAGE1_DIR,DATA_DIR,RECONALL_PARAMS,*args,**kwargs):
    """
    This function performs FLIRT registration between IN_FILE and structural/standard brain images. Brain extraction will be performed on IN_FILE prior to registration if bet_params is specified.

    flirt(IN_FILE,DATA_DIR,FLIRT_PARAMS,overwrite=False,bet_params=None,progress=False)

    Arguments:

        IN_FILE (str): fullpath to a NIfTI file

        DATA_DIR (str): fullpath to the project's data directory (project's 'dataDir' credential)

        RECONALL_PARAMS (str): fullpath to project's FS RECON-ALL parameter file

        args (str): a sequence of program arguments
            
        overwrite (BOOL): OPTIONAL flag to overwrite existing files (True) or not (False) 
            
        progress (BOOL): OPTIONAL flag to display command line output providing additional details on the processing status

    Returns:
        None
    """
    
    overwriteFlag = kwargs.get('overwrite',False)
    progress = kwargs.get('progress',False)
    outputFileList = []

    try:
        now = datetime.datetime.now()

        if progress:
            print('\n\nfsreconall_preprocess.py version ' + VERSION + ' dated ' + DATE + '\n')
            print('running @ ' + now.strftime("%m-%d-%Y %H:%M:%S") + '\n')
            print('Reading JSON Control File')

        #read parameter file
        with open(RECONALL_PARAMS) as j:
            reconallFullParams = json.load(j)

            # Organize parameter inputs
                
            #get main FLIRT parameters
            if 'reconall_params' in reconallFullParams:
                reconallParams = reconallFullParams.pop('reconall_params')
            else:
                raise InvalidJsonInput

            if 'main_image_params' in reconallFullParams:
                mainParams = reconallFullParams.pop('main_image_params')
            else:
                raise InvalidJsonInput
        
        # create file inputs and outputs
        subName, sesNum = get_dir_identifiers(STAGE1_DIR)
            
        #find associated brainmask image 
        if 'brainmask_regex' in reconallFullParams.keys():
            newRegexStr = reconallFullParams['brainmask_regex'].split('.')
            in_brainmaskFile = glob(os.path.join(DATA_DIR,'derivatives','sub-' + subName,'ses-' + sesNum,'bet','anat','*' + newRegexStr[0] + '_manual.' + '.'.join(newRegexStr[1:]) + '*'))
            if len(in_brainmaskFile) == 1:
                STAGE1_DIR = os.path.join(os.path.dirname(STAGE1_DIR) + '_manual',os.path.basename(STAGE1_DIR))
                if progress:
                    print('Found input brainmask, continuing with analysis')

            else:
                in_brainmaskFile = glob(os.path.join(DATA_DIR,'derivatives','sub-' + subName,'ses-' + sesNum,'bet','anat','*' + reconallFullParams['brainmask_regex'] + '*'))
                if len(in_brainmaskFile) == 1:
                    if progress:
                        print('Found input brainmask, continuing with analysis')

                else:
                    print('ERROR: did not find associated brainmask in ' + os.path.join(DATA_DIR,'derivatives','sub-' + subName,'ses-' + sesNum,'bet','anat','*' + reconallFullParams['brainmask_regex'] + '*'))
                    return

        # # move subjects dir to reconall output directory
        os.system('export SUBJECTS_DIR=' + STAGE1_DIR)
        if progress:
            print('SUBJECTS_DIR redirected to output directory: ' + STAGE1_DIR)


        #move output FS brainmask to orig space and convert to nifti
        if not os.path.isfile(os.path.join(STAGE1_DIR,'mri','T1w.a2009s.segstats.dat')) or overwriteFlag:
            if progress:
                print('Converting freesurfer brainmask to orig space and NIfTI format')

            vol2volCmd = 'mri_vol2vol --mov ' + os.path.join(STAGE1_DIR,'mri','brainmask.mgz') + ' --targ ' + os.path.join(STAGE1_DIR,'mri','rawavg.mgz') + ' --regheader --o ' + os.path.join(STAGE1_DIR,'mri','brainmask-native.mgz') + ' --no-save-reg'
            os.system(vol2volCmd)

            convertCmd = 'mri_convert -it mgz -ot nii ' + os.path.join(STAGE1_DIR,'mri','brainmask-native.mgz') + ' ' + os.path.join(STAGE1_DIR,'mri','brainmask-native.nii.gz')
            os.system(convertCmd)

            binCmd = 'fslmaths ' + os.path.join(STAGE1_DIR,'mri','brainmask-native.nii.gz') + ' -bin ' + os.path.join(STAGE1_DIR,'mri','brainmask-native_mask.nii.gz')
            os.system(binCmd)

            
            
            #mask freesurfer mask with input mask
            # maskCmd = 'fslmaths ' + os.path.join(STAGE1_DIR,'mri','brainmask-native_mask.nii.gz') + ' -mas ' + in_brainmaskFile[0] + ' ' + os.path.join(STAGE1_DIR,'mri','brainmask-new-native_mask.nii.gz')

            #copy brainmask
            if 'brainmask_regex' in reconallFullParams.keys():
                maskCmd = 'cp ' + in_brainmaskFile[0] + ' ' + os.path.join(STAGE1_DIR,'mri','brainmask-new-native_mask.nii.gz')
                os.system(maskCmd)


                #convert back to FS space
                vol2volCmd = 'mri_vol2vol --mov ' + os.path.join(STAGE1_DIR,'mri','brainmask-new-native_mask.nii.gz') + ' --targ ' + os.path.join(STAGE1_DIR,'mri','T1.mgz') + ' --regheader --o ' + os.path.join(STAGE1_DIR,'mri','brainmask.mgz') + ' --no-save-reg'
                os.system(vol2volCmd)

                #update binary value to align with original
                binCmd = 'mri_binarize --i ' + os.path.join(STAGE1_DIR,'mri','brainmask.mgz') + ' --o ' + os.path.join(STAGE1_DIR,'mri','brainmask.mgz') + ' --binval 999 --min 1'
                os.system(binCmd)


            #revise recon-all output by running stage 2 and 3
            reconallCmd = 'recon-all -autorecon2 -autorecon3 -subjid sub-' + subName + '_ses-' + sesNum + ' -sd ' + os.path.dirname(STAGE1_DIR)
            os.system(reconallCmd)

            #create output STL
            convertCmd = 'mris_convert ' + os.path.join(STAGE1_DIR,'surf','rh.pial') + ' ' + os.path.join(STAGE1_DIR,'surf','rh.stl') 
            os.system(convertCmd)
            convertCmd = 'mris_convert ' + os.path.join(STAGE1_DIR,'surf','lh.pial') + ' ' + os.path.join(STAGE1_DIR,'surf','lh.stl') 
            os.system(convertCmd)

            ms = pymeshlab.MeshSet()
            ms.load_new_mesh(os.path.join(STAGE1_DIR,'surf','lh.stl'))
            ms.load_new_mesh(os.path.join(STAGE1_DIR,'surf','rh.stl'))
            ms.generate_by_merging_visible_meshes()
            ms.meshing_decimation_quadric_edge_collapse()
            ms.apply_coord_hc_laplacian_smoothing()
            ms.save_current_mesh(os.path.join(STAGE1_DIR,'surf','brain_mesh.stl'),save_face_color=False)


            aparc2asegCmd = 'mri_aparc2aseg --s sub-' + subName + ' --a2009s'
            os.system(aparc2asegCmd)

            #convert revised aparc+aseg to native space
            #vol2volCmd = 'mri_vol2vol --mov ' + os.path.join(STAGE1_DIR,'mri','aparc+aseg.mgz') + ' --targ ' + os.path.join(STAGE1_DIR,'mri','rawavg.mgz') + ' --regheader --o ' + os.path.join(STAGE1_DIR,'mri','aparc+aseg-native.mgz') + ' --no-save-reg'
            vol2volCmd = 'mri_label2vol --seg ' + os.path.join(STAGE1_DIR,'mri','aparc+aseg.mgz') + ' --temp ' + os.path.join(STAGE1_DIR,'mri','rawavg.mgz') + ' --regheader ' + os.path.join(STAGE1_DIR,'mri','aparc+aseg.mgz') + '--o ' + os.path.join(STAGE1_DIR,'mri','aparc+aseg-native.mgz')
            os.system(vol2volCmd)

            #convert revised aparc+aseg to native space
            #vol2volCmd = 'mri_vol2vol --mov ' + os.path.join(STAGE1_DIR,'mri','aparc.a2009s+aseg.mgz') + ' --targ ' + os.path.join(STAGE1_DIR,'mri','rawavg.mgz') + ' --regheader --o ' + os.path.join(STAGE1_DIR,'mri','aparc.a2009s+aseg-native.mgz') + ' --no-save-reg'
            vol2volCmd = 'mri_label2vol --seg ' + os.path.join(STAGE1_DIR,'mri','aparc.a2009s+aseg.mgz') + ' --temp ' + os.path.join(STAGE1_DIR,'mri','rawavg.mgz') + ' --regheader ' + os.path.join(STAGE1_DIR,'mri','aparc.a2009s+aseg.mgz') + '--o ' + os.path.join(STAGE1_DIR,'mri','aparc+aseg-native.mgz')
            os.system(vol2volCmd)

            #compute cortical thickness measurements
            segstatsCmd = 'mri_segstats --subject sub-' + subName + '_ses-' + sesNum + ' --seg ' + os.path.join(STAGE1_DIR,'mri','aparc+aseg-native.mgz') + ' --nonempty --brain-vol-from-seg --etiv --totalgray --surf-ctx-vol --subcortgray --ctab-default --in ' + os.path.join(STAGE1_DIR,'mri','rawavg.mgz') + ' --sum ' + os.path.join(STAGE1_DIR,'mri','T1w.segstats.dat') + ' --sd ' + os.path.dirname(STAGE1_DIR)
            os.system(segstatsCmd)

            #compute cortical thickness measurements
            segstatsCmd = 'mri_segstats --subject sub-' + subName + '_ses-' + sesNum + ' --seg ' + os.path.join(STAGE1_DIR,'mri','aparc.a2009s+aseg-native.mgz') + ' --nonempty --brain-vol-from-seg --etiv --totalgray --surf-ctx-vol --subcortgray --ctab-default --in ' + os.path.join(STAGE1_DIR,'mri','rawavg.mgz') + ' --sum ' + os.path.join(STAGE1_DIR,'mri','T1w.a2009s.segstats.dat') + ' --sd ' + os.path.dirname(STAGE1_DIR)
            os.system(segstatsCmd)
        
    

    except OSError as e:
        print("Error Message: {0}".format(e))
        return
    except InvalidJsonInput:
        print("Invalid JSON INput: {0}".format(e))
        return
    except Exception as e:
        print("Error Message: {0}".format(e))
        return
        

        



if __name__ == '__main__':
    options = parse_arguments()
    argsDict = {}
    if options.OVERWRITE:
        argsDict['overwrite'] = options.OVERWRITE
    if options.progress:
        argsDict['progress'] = options.progress
    fsreconall_stage2(options.STAGE1_DIR,options.DATA_DIR,options.RECONALL_PARAMS,**argsDict)

    


