#!/resshare/wsuconnect/python3_venv/bin/python
# the command above ^^^ sets python 3.10.9 as the interpreter for this program

# Created by Matthew Sherwood (matt.sherwood@wright.edu, matthew.sherwood.7.ctr@us.af.mil)
# Created on 19 July 2023
#
# MOdified on 17 Nov 2024 - updated commenting
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
REALPATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
# sys.path.append(REALPATH)
# REALPATH = os.path.join('/resshare','general_processing_codes')
sys.path.append(REALPATH)
import support_tools as st

FSLDIR = os.environ["FSLDIR"]


VERSION = '1.1.0'
DATE = '17 Nov 2024'


parser = argparse.ArgumentParser('fsreconall_stage2.py: perform FLIRT registration between 2D ASL and structural/standard brain images')
parser.add_argument('STAGE1_DIR',help='fullpath to the output directory for freesurfer reconall stage1 (autorecon1)')
parser.add_argument('DATA_DIR', help="fullpath to the project's data directory (project's 'dataDir' credential)")
parser.add_argument('RECONALL_PARAMS', help="fullpath to project's RECONALL parameter control file")
parser.add_argument('--overwrite',action='store_true',dest='OVERWRITE',default=False, help='overwrite existing files')
parser.add_argument('--progress',action='store_true',dest='progress',default=False, help='verbose mode')


class InvalidJsonInput(Exception):
    "Raised when the input JSON control file does not contain the appropriate mandatory definitions"
    pass


# ******************* s3 bucket check ********************
def fsreconall_stage2(STAGE1_DIR: str, DATA_DIR: str, RECONALL_PARAMS: str, overwrite: bool=False, progress: bool=False):
    """
    This function performs stage 2 and 3 of FreeSurfer reconall freesurfer_recon-all_input.json control file. 

    :param STAGE1_DIR: fullpath to a single subject/session reconall Stage 1 directory
    :type STAGE1_DIR: str
    
    :param DATA_DIR: fullpath to the project's data directory (project's 'dataDir' credential)
    :type DATA_DIR: str

    :param RECONALL_PARAMS: fullpath to project's FreeSurfer RECON-ALL parameter control file
    :type RECONALL_PARAMS: str

    :param overwrite: flag to overwrite existing files, defaults to False
    :type overwrite: bool, optional

    :param progress: flag to display command line output providing additional details on the processing status, defaults to False
    :type progress: bool, optional

    :raises InvalidJsonInput: error encountered when the input JSON control file does not contain the appropriate mandatory definitions

    :raises Exception: general error encountered during execution
    """ 
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
        st.get_dir_identifiers_new(STAGE1_DIR)
            
        #find associated brainmask image 
        if 'brainmask_regex' in reconallFullParams.keys():
            newRegexStr = reconallFullParams['brainmask_regex'].split('.')
            in_brainmaskFile = glob(os.path.join(DATA_DIR,'derivatives','sub-' + st.subject.id,'ses-' + st.subject.sesNum,'bet','anat','*' + newRegexStr[0] + '_manual.' + '.'.join(newRegexStr[1:]) + '*'))
            if len(in_brainmaskFile) == 1:
                STAGE1_DIR = os.path.join(os.path.dirname(STAGE1_DIR) + '_manual',os.path.basename(STAGE1_DIR))
                if progress:
                    print('Found input brainmask, continuing with analysis')

            else:
                in_brainmaskFile = glob(os.path.join(DATA_DIR,'derivatives','sub-' + st.subject.id,'ses-' + st.subject.sesNum,'bet','anat','*' + reconallFullParams['brainmask_regex'] + '*'))
                if len(in_brainmaskFile) == 1:
                    if progress:
                        print('Found input brainmask, continuing with analysis')

                else:
                    print('ERROR: did not find associated brainmask in ' + os.path.join(DATA_DIR,'derivatives','sub-' + st.subject.id,'ses-' + st.subject.sesNum,'bet','anat','*' + reconallFullParams['brainmask_regex'] + '*'))
                    return

        # # move subjects dir to reconall output directory
        os.system('export SUBJECTS_DIR=' + STAGE1_DIR)
        if progress:
            print('SUBJECTS_DIR redirected to output directory: ' + STAGE1_DIR)


        #move output FS brainmask to orig space and convert to nifti
        if not os.path.isfile(os.path.join(STAGE1_DIR,'mri','T1w.a2009s.segstats.dat')) or overwrite:
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
            reconallCmd = 'recon-all -autorecon2 -autorecon3 -subjid sub-' + st.subject.id + '_ses-' + st.subject.sesNum + ' -sd ' + os.path.dirname(STAGE1_DIR)
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


            aparc2asegCmd = 'mri_aparc2aseg --s sub-' + st.subject.id + ' --a2009s'
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
            segstatsCmd = 'mri_segstats --subject sub-' + st.subject.id + '_ses-' + st.subject.sesNum + ' --seg ' + os.path.join(STAGE1_DIR,'mri','aparc+aseg-native.mgz') + ' --nonempty --brain-vol-from-seg --etiv --totalgray --surf-ctx-vol --subcortgray --ctab-default --in ' + os.path.join(STAGE1_DIR,'mri','rawavg.mgz') + ' --sum ' + os.path.join(STAGE1_DIR,'mri','T1w.segstats.dat') + ' --sd ' + os.path.dirname(STAGE1_DIR)
            os.system(segstatsCmd)

            #compute cortical thickness measurements
            segstatsCmd = 'mri_segstats --subject sub-' + st.subject.id + '_ses-' + st.subject.sesNum + ' --seg ' + os.path.join(STAGE1_DIR,'mri','aparc.a2009s+aseg-native.mgz') + ' --nonempty --brain-vol-from-seg --etiv --totalgray --surf-ctx-vol --subcortgray --ctab-default --in ' + os.path.join(STAGE1_DIR,'mri','rawavg.mgz') + ' --sum ' + os.path.join(STAGE1_DIR,'mri','T1w.a2009s.segstats.dat') + ' --sd ' + os.path.dirname(STAGE1_DIR)
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
    """
    The entry point of this program for command-line utilization.
    """

    options = parser.parse_args()
    argsDict = {}
    if options.OVERWRITE:
        argsDict['overwrite'] = options.OVERWRITE
    if options.progress:
        argsDict['progress'] = options.progress
    fsreconall_stage2(options.STAGE1_DIR,options.DATA_DIR,options.RECONALL_PARAMS,**argsDict)

    


