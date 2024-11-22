#!/resshare/wsuconnect/python3_venv/bin/python
# the command above ^^^ sets python 3.10.10 as the interpreter for this program

# Created by Matthew Sherwood (matt.sherwood@wright.edu, matthew.sherwood.7.ctr@us.af.mil)
# Created on 26 Jan 2021
#
# Modified on 15 Nov 2024 - implementation of nipype workflow and nodes
# Modified on 29 Sept 2023 - add support for antspynet brain segmentation
# Modified on 28 July 2023 - add some corrections for multiple image types with difference acq parameters in same session
# Modified on 26 April 2023 - update to WSU
# Modified on 27 Sept 2021 - update to align with direct s3 mount
# Modified on 26 Jan 2021

import sys
import os
import argparse
import json
from nipype.interfaces import fsl
import nipype.pipeline.engine as pe
from nipype.interfaces.utility import Function
import ants
from glob import glob as glob
import datetime
from typing import Tuple

#local import
REALPATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
# sys.path.append(REALPATH)
# REALPATH = os.path.join('/resshare','general_processing_codes')
sys.path.append(REALPATH)
os.environ['MPLCONFIGDIR'] = os.path.join(REALPATH,'.config','matplotlib')

import support_tools as st


VERSION = '3.1.0'
DATE = '15 Nov 2024'


parser = argparse.ArgumentParser('flirt.py: perform FLIRT registration between input and reference/standard brain images')
FSLDIR = os.environ["FSLDIR"]

parser.add_argument('IN_FILE')
parser.add_argument('DATA_DIR')
parser.add_argument('FLIRT_PARAMS')
parser.add_argument('--bet-params',action='store',dest='BET_PARAMS',default=None)
parser.add_argument('--flirt-params',action='store',dest='FLIRT_PARAMS',default=None)
parser.add_argument('--overwrite',action='store_true',dest='OVERWRITE',default=False)
parser.add_argument('--progress',action='store_true',dest='progress',default=False)


def get_total_vols(main_file: str,FSLDIR: str) -> int:
    """
    compute the number of volumes in a NIfTI image

    :param main_file: fullpath to a NIfTI image
    :type main_file: str

    :param FSLDIR: path to the location of the FSL installation
    :type FSLDIR: str

    :return: number of volumes in image main_file
    :rtype: int
    """    
    import os
    import subprocess   
    proc = subprocess.check_output(os.path.join(FSLDIR,'bin','fslval') + ' ' + main_file + ' dim4',shell=True,encoding='utf-8')
    totalVols = int(proc.split(' ')[0])
    return totalVols

def do_antspynet_bet(main_file: str, main_file_brain: str, main_file_brainmask: str, bet_params: dict,bet_full_params: dict, REALPATH: str) -> Tuple[str, str]:
    """
    Performs antspynet brain extraction according to the specifications in the bet_params file.

    :param main_file: fullpath to a NIfTI image
    :type main_file: str

    :param main_file_brain: fullpath to the desired output NIfTI brain image
    :type main_file_brain: str

    :param main_file_brainmask: fullpath to the desired output NIfTI brainmask
    :type main_file_brainmask: str

    :param bet_params: bet_params keys from the BET parameter JSON control file
    :type bet_params: dict

    :param bet_full_params: full set of parameters loaded from the BET parameter JSON control file
    :type bet_full_params: dict

    :param REALPATH: fullpath to the wsuconnect python module
    :type REALPATH: str

    :return: a Tuple containing the fullpath to the brain extracted NIfTI image and the brain mask NIfTI image
    :rtype: Tuple[str, str]
    """    
    
    import ants
    import antspynet
    import os
    inImg = ants.image_read(main_file)
    brainSeg = antspynet.brain_extraction(inImg, modality=bet_params['modality'], antsxnet_cache_directory=os.path.join(REALPATH,'support_tools','antsxnet_cache'), verbose=True)
    brainSeg.to_file(os.path.join(os.path.dirname(main_file_brain),'antspynet_brainseg.nii.gz'))

    #create brainmask and brain image
    os.system('fslmaths ' + os.path.join(os.path.dirname(main_file_brain),'antspynet_brainseg.nii.gz') + ' -thr 0.9 -bin ' + main_file_brainmask)
    
    os.system('fslmaths ' + main_file + ' -mas ' + main_file_brainmask + ' ' + main_file_brain)

    #create tile mosaic overlay
    os.system('ConvertScalarImageToRGB 3 ' + main_file_brain + ' ' + main_file_brain.replace('brain','brain-red') + ' none red')
    print('\tCreated ' + main_file_brain.replace('brain','brain-red') + ' for tile mosaic creation')

    mosaicCmd = 'CreateTiledMosaic -i ' + main_file + ' -r ' + main_file_brain.replace('brain','brain-red') + ' -o ' + main_file_brain.replace('.nii.gz','-brain-mosaic.png')#.replace('sub-' + subName + '_ses-' + sesNum + '_','')
    for k in bet_full_params['mosaic_params'].keys():
        if len(k) == 1:
            mosaicCmd = mosaicCmd + ' -' + k + ' ' + bet_full_params['mosaic_params'][k]
        else:
            mosaicCmd = mosaicCmd + ' --' + k + ' ' + bet_full_params['mosaic_params'][k]
    os.system(mosaicCmd)
    

    print("\tDone creating Tile Mosaic")

    return main_file_brain, main_file_brainmask


# ******************* s3 bucket check ********************
def flirt(IN_FILE: str, DATA_DIR: str, FLIRT_PARAMS: str, bet_params_file: str=None, overwrite: bool=False, progress: bool=False):
    """
    This function performs FLIRT registration between IN_FILE and structural/standard brain images. Brain extraction will be performed on IN_FILE prior to registration if bet_params is specified.

    flirt(IN_FILE,DATA_DIR,FLIRT_PARAMS,overwrite=False,bet_params_file=None,progress=False)

    :param IN_FILE: fullpath to a NIfTI file
    :type IN_FILE: str

    :param DATA_DIR: fullpath to the project's data directory (project's 'dataDir' credential)
    :type DATA_DIR: str

    :param FLIRT_PARAMS: fullpath to project's 2D ASL FLIRT parameter file
    :type FLIRT_PARAMS: str

    :param bet_params_file: fullpath to project's brain extraction parameter file, defaults to None
    :type bet_params_file: str, optional

    :param overwrite: flag to overwrite existing files, defaults to False
    :type overwrite: bool, optional

    :param progress: flag to display command line output providing additional details on the processing status, defaults to False
    :type progress: bool, optional

    :raises Exception: general error encountered during execution
    """
    
    stdImageFile = None
    stdImage = False
    performFslRoi = False
    performBet = False
    secImage = False
    refImageFile = None
    refImage = False

    
    now = datetime.datetime.now()

    struc_regexStr = None
    workFlow = pe.Workflow(name='connect_flirt')
    b_fslroi = False
        
    try:
    
        if progress:
            os.system('echo "\n\nflirt.py version ' + VERSION + ' dated ' + DATE + '\n"')
            os.system('echo "running @ ' + now.strftime("%m-%d-%Y %H:%M:%S") + '\n"')
            os.system('echo "Reading JSON Files"')

        # Organize parameter inputs

        with open(FLIRT_PARAMS) as j:
            flirtFullParams = json.load(j)
        #additional processing options
        if 'fslroi' in flirtFullParams:
            performFslRoi = flirtFullParams.pop('fslroi')
        if 'bet' in flirtFullParams:
            performBet = flirtFullParams.pop('bet')

        #get main image parameters
        if 'main_image_params' in flirtFullParams:
            mainParams = flirtFullParams.pop('main_image_params')
            
        #get main FLIRT parameters
        if 'flirt_params' in flirtFullParams:
            flirtParams = flirtFullParams.pop('flirt_params')

        #(optional)get secondary image parameters
        if 'secondary_image_params' in flirtFullParams:
            secImageParams = flirtFullParams.pop('secondary_image_params')
            secImage = True

        #(optional) get structural image parameters
        if 'reference_image_params' in flirtFullParams:
            refImageParams = flirtFullParams.pop('reference_image_params')
            refImage = True

        #(optional) get standard image parameters for additional matrix concatenation
        if 'standard_reference_params' in flirtFullParams:
            stdImageParams = flirtFullParams.pop('standard_reference_params')
            stdImage = True
            if 'type' in stdImageParams:
                if stdImageParams['type'] == 'FSL':
                    stdImageFile = os.path.join(FSLDIR,'data','standard',stdImageParams['file'])
                elif stdImageParams['type'] == 'file':
                    stdImageFile = stdImageParams['file']
                    if not os.path.isfile(stdImageFile) and progress:
                        os.system('echo "WARNING: reference file specified in parameter file but the file cannot be located - ' + stdImageFile + '"')
                        os.system('echo "/tSkipping standard transformation and/or concatenation"')
                        stdImage = False
                else:
                    os.system('echo "WARNING: standard reference type not supported"')
                    os.system('echo "/tSkipping standard transformation and/or concatenation"')
            else:
                os.system('echo "WARNING: must specify type in standard_reference_params field"')
                os.system('echo "/tSkipping standard transformation and/or concatenation"')

        if bet_params_file:
            with open(bet_params_file) as j:
                betFullParams = json.load(j)
            if 'type' in betFullParams:
                betType = betFullParams.pop('type')
            if 'bet_params' in betFullParams:
                betParams = betFullParams.pop('bet_params')
            else:
                performBet = False


        #check if file exists on local disk
        mainFile = IN_FILE
        if not os.path.isfile(mainFile):
            if progress:
                os.system('echo "Main Image File Not Found"')
            return
        elif progress:
            os.system('echo "Main Image File Found: ' + mainFile + '"')

        #make output directory structure if it does not exist
    
        # create file inputs and outputs
        mainFileDir = os.path.dirname(mainFile)
        st.get_dir_identifiers_new(mainFileDir)
        mainFlirtOutputDir = os.path.join(DATA_DIR,'derivatives','sub-' + st.subject.id,'ses-' + st.subject.fullSesNum,mainParams['output_bids_location'],workFlow.name)#create base path and filename for move
        mainBetOutputDir = os.path.join(DATA_DIR,'derivatives','sub-' + st.subject.id,'ses-' + st.subject.fullSesNum,mainParams['output_bids_location'],workFlow.name)#create base path and filename for move


        workFlow.base_dir = mainFlirtOutputDir

        if not os.path.isdir(mainFlirtOutputDir):
            os.makedirs(mainFlirtOutputDir)
        if performBet:
            if not os.path.isdir(mainBetOutputDir) and bet_params_file:
                os.makedirs(mainBetOutputDir)
            os.chdir(mainBetOutputDir)

        #look for accompanying structural data on disk in derivatives
        if refImage and not refImageParams['type'] == 'std':
            ref_regexStr = st.get_bids_filename(**refImageParams['input_bids_labels'])
            if refImageParams['input_bids_location'] == 'rawdata':
                refImageFile = glob(os.path.join(os.path.dirname(os.path.dirname(mainFileDir)),'**','*' + ref_regexStr + '*'), recursive=True)
            elif refImageParams['input_bids_location'] == 'derivatives':
                refImageFile = glob(os.path.join(os.path.dirname(os.path.dirname(mainBetOutputDir)),'**','*' + ref_regexStr + '*'), recursive=True)
            else:
                os.system('echo "ERROR: structural file "bids_location" not supported"')
                os.system('echo "/tCannot perform FLIRT... exiting"')
                return

            if refImage:
                if len(refImageFile) > 0:
                    refImageFile = refImageFile[0]
                elif refImageParams['input_bids_location'] == 'rawdata':
                    os.system('echo "ERROR: structural file ' + os.path.join(os.path.dirname(mainFileDir),'anat','*' + ref_regexStr + '*') + ' not found"')
                    os.system('echo "/tCannot perform FLIRT... exiting"')
                    return
                elif refImageParams['input_bids_location'] == 'derivatives':
                    os.system('echo "ERROR: structural file ' + os.path.join(os.path.dirname(mainBetOutputDir),'anat','*' + ref_regexStr + '*') + ' not found"')
                    os.system('echo "/tCannot perform FLIRT... exiting"')
                    return

            if progress and refImageFile:
                os.system('echo "Reference Structural File Found: ' + refImageFile + '"')

        elif stdImageFile:
            refImageFile = stdImageFile

        else:
            os.system('echo "ERROR: standard reference file not found"')
            os.system('echo "/tCannot perform FLIRT... exiting"')
            return
        

        mainBidsLabels = st.get_bids_labels(mainFile)
        if secImage:
            # secBidsLabels = mainBidsLabels.copy()
            secBidsLabels = {}
            for k in secImageParams['input_bids_labels'].keys():
                secBidsLabels[k] = secImageParams['input_bids_labels'][k]
            for k in mainBidsLabels.keys():
                if 'task' in k or 'run' in k:
                    secBidsLabels[k] = mainBidsLabels[k]
            sec_regexStr = st.get_bids_filename(**secBidsLabels)
            secFile = glob(os.path.join(mainFileDir,'*' + sec_regexStr))
            # secFile = [x for x in secFile if 'acq-' + mainBidsLabels['acquisition'].split('-')[0] in 
            if len(secFile) > 0:
                secFile = secFile[0]
            else:
                os.system('echo "WARNING: secondary image file ' + os.path.join(os.path.dirname(mainFileDir),'*' + sec_regexStr + '*') + ' not found... skipping"')
                
            if progress and secFile:
                os.system('echo "Secondary File Found: ' + secFile + '"')


        # **********************************
        # get single volume for registration (maybe better with mean after running mcflirt?) 
        # **********************************
        if_getTotalVols = Function(input_names=["main_file","FSLDIR"],
                             output_names=["total_vols"],
                             function=get_total_vols)
        if performFslRoi:
            if type(mainParams['volume']) is int or mainParams['volume'] == 'center':
                #nd_getTotalVols = pe.Node(interface=if_getTotalVols, name='get_total_vols')
                if_getTotalVols.inputs.main_file = mainFile
                if_getTotalVols.inputs.FSLDIR = FSLDIR
                res = if_getTotalVols.run()
                totalVols = res.outputs.total_vols

                if mainParams['volume'] == 'center':
                    vols = int(totalVols/2)
                else:
                    vols = mainParams['volume']
                    if not vols < totalVols:
                        print('WARNING: user selected volume #' + str(vols) + ' but the image only contains ' + str(totalVols))
                        print('/tDefaulting to volume 1')
                        vols = 1
            else:
                os.system('echo "WARNING: improper volume selection, skipping volume extraction"')
                vols = None

            if vols:
                roi_mainBidsLabels = mainBidsLabels.copy()
                roi_mainBidsLabels['process'] = 'fslroi'
                roi_mainBidsLabels['description'] = 'vol-' + str(vols)
                for k in mainParams['output_bids_labels'].keys():
                    roi_mainBidsLabels[k] = mainParams['output_bids_labels'][k]
                outMainVolFile = os.path.join(mainBetOutputDir,st.get_bids_filename(subject=st.subject.id,session=st.subject.fullSesNum,**roi_mainBidsLabels))


                if os.path.isfile(outMainVolFile) and not overwrite:
                    mainFile = outMainVolFile
                    if progress:
                        os.system('echo "Single volume file already exists: ' + outMainVolFile + '"')

                else:
                    #fslroi = fsl.ExtractROI(in_file=mainFile,roi_file=outMainVolFile,t_min=vols,t_size=1)
                    #fslroi.run()
                    n_fslroi = pe.Node(interface=fsl.ExtractROI(),name='main_fslroi')
                    n_fslroi.inputs.in_file=mainFile
                    n_fslroi.inputs.roi_file=outMainVolFile
                    n_fslroi.inputs.t_min=vols
                    n_fslroi.inputs.t_size=1
                    n_fslroi.terminal_output = 'file_split'
                    # if progress:
                    #     os.system('echo "Creating single volume file from volume #' + str(vols) + ' as ' + outMainVolFile + '"')

                    #write JSON sidecar file
                    # d = {}
                    # d['Sources'] = ['bids:raw:' + fslroi.inputs.in_file.split(DATA_DIR + os.sep)[1]]
                    # d['FslRoiParameters'] = {'t_min': vols, 't_size': 1}
                    # d['SkullStripped'] = 'false'
                    # for k in mainParams['output_json_values'].keys():
                    #     d[k] = mainParams['output_json_values'][k]
                    # with open(fslroi.inputs.roi_file.split('.')[0] + '.json', 'w') as fp:
                    #     json.dump(d, fp, indent=4) 
                    
                    # mainFile = fslroi.inputs.roi_file
                    b_fslroi = True


        # **********************************
        # perform BET on main input
        # **********************************
        if performBet:
            bet_mainBidsLabels = mainBidsLabels.copy()
            if betType == 'FSL':
                bet_mainBidsLabels['process'] = 'fslbet'
            elif betType == 'ANTs':
                bet_mainBidsLabels['process'] = 'ants'
            elif betType == 'ANTsPyNet':
                bet_mainBidsLabels['process'] = 'antspynet'


            bet_mainBidsLabels['resolution'] = 'lo'
            if performFslRoi:
                bet_mainBidsLabels['description'] = 'vol-' + str(vols) + '-brain'
            else:
                bet_mainBidsLabels['description'] = 'brain'

            for k in mainParams['output_bids_labels'].keys():
                bet_mainBidsLabels[k] = mainParams['output_bids_labels'][k]

            mainFile_brain = os.path.join(mainBetOutputDir,st.get_bids_filename(subject=st.subject.id,session=st.subject.fullSesNum,**bet_mainBidsLabels))
            
            bet_mainBidsLabels['suffix'] = 'mask'
            mainFile_brainmask = os.path.join(mainBetOutputDir,st.get_bids_filename(subject=st.subject.id,session=st.subject.fullSesNum,**bet_mainBidsLabels))
                        
            #continue with BET?
            if os.path.isfile(mainFile_brain) and not overwrite:
                if progress:
                    os.system('echo "Skipping BET: brain extracted file found: ' + mainFile_brain + '"')
                mainFile = mainFile_brain
                    
            else:
                if progress:
                    os.system('echo "Performing BET on ' + mainFile + '"')
                    os.system('echo "\tOUTPUT: ' + mainFile_brain + '"')

                if betType == 'FSL':
                    n_bet = pe.Node(interface=fsl.BET(**betParams),name='main_bet')
                    n_bet.inputs.out_file = mainFile_brain
                    n_bet.terminal_output = 'file_split'
                    if b_fslroi:
                        workFlow.connect([(n_fslroi,n_bet,[('roi_file','in_file')])])
                    else:
                        n_bet.inputs.in_file = mainFile
                        workFlow.add_nodes([n_bet])

                #ANTs
                elif betType == 'ANTs':
                    btr = ants.segmentation.BrainExtraction(**betParams)
                    tmp_newMainFile = mainFile

                    #best performance with coronal images
                    btrFlirtFlag = False
                    if not 'acq-cor' in mainFile:
                        if 'acq-ax' in mainFile:
                            if 'axial' in mainFile:
                                tmp_newMainFile = tmp_newMainFile.replace('axial','coronal')
                            else:
                                tmp_newMainFile = tmp_newMainFile.replace('ax','cor')
                        elif 'acq-sag' in mainFile:
                            if 'sagittal' in mainFile:
                                tmp_newMainFile = tmp_newMainFile.replace('sagittal','coronal')
                            else:
                                tmp_newMainFile = tmp_newMainFile.replace('sag','cor')
                        if os.path.isfile(tmp_newMainFile):
                            btr.inputs.anatomical_image = tmp_newMainFile
                            btrFlirtFlag = True
                    else:
                        btr.inputs.anatomical_image = mainFile
                        btrFlirtFlag = True

                    if btrFlirtFlag:
                        betInFile = btr.inputs.anatomical_image
                        betOutFile = mainFile_brain
                        btr.run()
                        f = glob(os.path.join(os.getcwd(),'ants*BrainExtractionBrain.nii.gz'))

                    #register coronal with input T1 image
                    if btrFlirtFlag and not 'acq-cor' in mainFile:
                        flt = fsl.FLIRT(**flirtParams)
                        flt.inputs.in_file = btr.inputs.anatomical_image
                        flt.inputs.reference = mainFile
                        flt.inputs.interp = 'trilinear'
                        flt.inputs.dof = 7
                        flt.inputs.searchr_x = [-90, 90]
                        flt.inputs.searchr_y = [-90, 90]
                        flt.inputs.searchr_z = [-90, 90]
                        flt.inputs.bins = 256
                        flt.inputs.cost = 'corratio'
                        flt.inputs.cost_func = 'mutualinfo'
                        flt.inputs.out_matrix_file = os.path.join(mainBetOutputDir,'reg','tmp_to_axial' + '.mat')
                        flt.inputs.out_file = os.path.join(mainBetOutputDir,'reg','tmp_axial.nii.gz')

                        if not os.path.isdir(os.path.dirname(flt.inputs.out_file)):
                            os.makedirs(os.path.dirname(flt.inputs.out_file))
                        flt.run()


                    else:
                        f = glob(os.path.join(os.getcwd(),'ants*BrainExtractionBrain.nii.gz'))
                        if f:
                            os.rename(f,mainFile_brain)

    
                elif betType == 'ANTsPyNet':
                    n_bet = pe.Node(interface=Function(input_names=["main_file","main_file_brain","main_file_brainmask","bet_params","bet_full_params","REALPATH"],
                                                                  output_names=["out_file","out_file_mask"],
                                                                  function=do_antspynet_bet),
                                                name='main_bet')
                    n_bet.inputs.main_file_brain = mainFile_brain
                    n_bet.inputs.main_file_brainmask = mainFile_brainmask
                    n_bet.inputs.bet_params = betParams
                    n_bet.inputs.bet_full_params = betFullParams
                    n_bet.inputs.REALPATH = REALPATH
                    n_bet.terminal_output = 'file_split'
                    if b_fslroi:
                        workFlow.connect([(n_fslroi,n_bet,[('roi_file','main_file')])])
                    else:
                        n_bet.inputs.main_file = mainFile
                        workFlow.add_nodes([n_bet])

                
                #write JSON sidecar file
                # d = {}
                # d['BetProgram'] = betType
                # d['BetParameters'] = betParams.copy()
                # if 'derivatives' in betInFile:
                #     d['Sources'] = 'bids:derivatives:' + betInFile.split(DATA_DIR + os.sep)[1]
                # else:
                #     d['Sources'] = 'bids:raw:' + betInFile.split(DATA_DIR + os.sep)[1]
                # d['SkullStripped'] = True
                # d['Type'] = 'Brain'
                # for k in mainParams['output_json_values'].keys():
                #     d[k] = mainParams['output_json_values'][k]

                # with open(betOutFile.split('.')[0] + '.json', 'w') as fp:
                #     json.dump(d, fp, indent=4)


                    
                # create brain mask (all but antspynet)
                # ----------------------------------
                if betType == 'FSL':
                    n_fslmaths1 = pe.Node(interface=fsl.ImageMaths(),name='main_create_brainmask')
                    n_fslmaths1.inputs.out_file = mainFile_brainmask


                    workFlow.connect([(n_bet,n_fslmaths1,[('out_file','in_file')])])

                elif betType == 'ANTs':
                    if btrFlirtFlag and not 'acq-cor' in mainFile:
                        #apply registration to brain mask and mainFile (input image)
                        f = glob(os.path.join(os.getcwd(),'ants*BrainExtractionMask.nii.gz'))
                        if f and len(f) == 1:
                            applyxfm = fsl.ApplyXFM()
                            applyxfm.inputs.in_file = f[0]
                            applyxfm.inputs.reference = mainFile
                            applyxfm.inputs.apply_xfm = True
                            # applyBidsLabels = fltBidsLabels.copy()
                            applyxfm.inputs.out_file = os.path.join(mainFile_brainmask)
                            applyxfm.inputs.in_matrix_file = flt.inputs.out_matrix_file

                            applyxfm.run()

                            betOutFile = mainFile_brain


                            os.system('fslmaths ' + mainFile_brainmask + ' -bin ' + mainFile_brainmask)
                            os.system('fslmaths ' + mainFile + ' -mas ' + mainFile_brainmask + ' ' + mainFile_brain)
                    else:
                        f = glob(os.path.join(os.getcwd(),'ants*BrainExtractionMask.nii.gz'))
                        if f and len(f) == 1:
                            os.rename(f[0],mainFile_brainmask)

                # if 'anat' in mainBetOutputDir:
                #     if not os.path.isfile(os.path.join(mainBetOutputDir,os.path.basename(mainFile))):
                #         shutil.copyfile(mainFile,os.path.join(mainBetOutputDir,os.path.basename(mainFile)))
                #     if not os.path.isfile(os.path.join(mainBetOutputDir,os.path.basename(mainFile).split('.')[0] + '_brain.nii.gz')):
                #         shutil.copyfile(mainFile_brain,os.path.join(mainBetOutputDir,os.path.basename(mainFile).split('.')[0] + '_brain.nii.gz'))




                


                #write corresponding JSON file
                # d['Sources'] = [d['Sources'],
                #     'bids:derivatives:' + betOutFile.split(DATA_DIR + os.sep)[1]]
                # d['SkullStripped'] = True
                # d['Type'] = 'Brain'
                # for k in mainParams['output_json_values'].keys():
                #     d[k] = mainParams['output_json_values'][k]

                # with open(mainFile_brainmask.split('.')[0] + '.json', 'w') as fp:
                #     json.dump(d, fp, indent=4) 

                # mainFile = mainFile_brain


                # apply brain mask to secondary image?
                # -------------------------------
                if secImage:
                    secBidsLabels = st.get_bids_labels(secFile)
                    secBidsLabels['process'] = bet_mainBidsLabels['process']
                    secBidsLabels['resolution'] = 'lo'
                    secBidsLabels['description'] = 'brain'
                    secBidsLabels['extension'] = 'nii.gz'
                    secFile_brain = os.path.join(mainBetOutputDir,st.get_bids_filename(subject=st.subject.id,session=st.subject.fullSesNum,**secBidsLabels))


                    n_fslmaths = pe.Node(interface=fsl.ImageMaths(),name='sec_apply_brainmask')
                    n_fslmaths.inputs.in_file = secFile
                    n_fslmaths.inputs.out_file = secFile_brain

                    if betType == 'FSL':
                        workFlow.connect([(n_fslmaths1,n_fslmaths,[('out_file','mask_file')])])

                    elif betType == "ANTsPyNet":
                        workFlow.connect([(n_bet,n_fslmaths,[('out_file_mask','mask_file')])])

                    
                    # os.system('fslmaths ' + secFile + ' -mas ' + mainFile_brainmask + ' ' + secFile_brain)

                    # #write corresponding JSON file
                    # d = {}
                    # d['BetProgram'] = betType
                    # d['BetParameters'] = betParams.copy()
                    # d['Sources'] = ['bids:raw:' + secFile.split(DATA_DIR + os.sep)[1],
                    #                 'bids:derivatives:' + mainFile_brainmask.split(DATA_DIR + os.sep)[1]]
                    # d['SkullStripped'] = True
                    # d['Type'] = 'Brain'
                    # for k in mainParams['output_json_values'].keys():
                    #     d[k] = mainParams['output_json_values'][k]

                    # with open(secFile_brain.split('.')[0] + '.json', 'w') as fp:
                    #     json.dump(d, fp, indent=4)   
                    
                    # secFile = secFile_brain


        # **********************************
        # run FLIRT on Main Image Input
        # **********************************

        ###neeed to check if output exists?????
        if refImageFile:
            n_flt = pe.Node(interface=fsl.FLIRT(**flirtParams),name='main_reg')
            n_flt.inputs.reference = refImageFile
            n_flt.terminal_output = 'file_split'
            


            
            fltBidsLabels = mainBidsLabels.copy()
            
            if refImageParams['type'] == 'std':
                for k in stdImageParams['output_bids_labels'].keys():
                    fltBidsLabels[k] = stdImageParams['output_bids_labels'][k]
                if performFslRoi and 'brain' in mainFile:
                    fltBidsLabels['description'] = 'vol-' + str(vols) + '-brain'
                elif performFslRoi:
                    fltBidsLabels['description'] = 'vol-' + str(vols) 
                elif 'brain' in mainFile:
                    fltBidsLabels['description'] = 'brain'

            else:
                for k in refImageParams['output_bids_labels'].keys():
                    fltBidsLabels[k] = refImageParams['output_bids_labels'][k]
                if performFslRoi and 'brain' in mainFile:
                    fltBidsLabels['description'] = 'vol-' + str(vols) + '-brain'
                elif performFslRoi:
                    fltBidsLabels['description'] = 'vol-' + str(vols) 
                elif 'brain' in mainFile:
                    fltBidsLabels['description'] = 'brain'
            n_flt.inputs.out_file = os.path.join(mainFlirtOutputDir,st.get_bids_filename(subject=st.subject.id,session=st.subject.fullSesNum,**fltBidsLabels))
            inputMatrixBase = st.get_bids_labels(IN_FILE)
            if 'acquisition' in inputMatrixBase.keys():
                inputMatrixBase = inputMatrixBase['acquisition'] + '-'
            else:
                inputMatrixBase = ''

            
            for k in mainBidsLabels.keys():
                if 'task' in k:
                    mainParams['out_matrix_base'] = mainParams['out_matrix_base'] + '_task-' + mainBidsLabels[k]
                if 'run' in k:
                    mainParams['out_matrix_base'] = mainParams['out_matrix_base'] + '_run-' + mainBidsLabels[k]
            if refImageParams['type'] == 'std':
                n_flt.inputs.out_matrix_file = os.path.join(mainFlirtOutputDir,inputMatrixBase + mainParams['out_matrix_base'] + '2' + stdImageParams['out_matrix_suffix'] + '.mat')
            else:
                n_flt.inputs.out_matrix_file = os.path.join(mainFlirtOutputDir,inputMatrixBase + mainParams['out_matrix_base'] + '2' + refImageParams['out_matrix_base'] + '.mat')


            if os.path.isfile(n_flt.inputs.out_matrix_file) and not overwrite:
                if progress:
                    os.system('echo "Skipping FLIRT: registration matrix file found: ' + flt.inputs.out_matrix_file + '"')
                    
            else:                
                # if b_fslroi:
                workFlow.connect([(n_bet,n_flt,[('out_file','in_file')])])
                # else:
                #     n_flt.inputs.in_file = mainFile
                # if progress:
                #     os.system('echo "\tSuccess!"')


                # invert registration matrix
                # ----------------------------------
                n_invt = pe.Node(interface=fsl.ConvertXFM(),name="main_reg_invert")
                
                n_invt.inputs.invert_xfm = True
                if refImageParams['type'] == 'std':
                    n_invt.inputs.out_file = os.path.join(mainFlirtOutputDir,stdImageParams['out_matrix_suffix'] + '2' + inputMatrixBase + mainParams['out_matrix_base'] + '.mat')
                else:
                    n_invt.inputs.out_file = os.path.join(mainFlirtOutputDir,refImageParams['out_matrix_base'] + '2' + inputMatrixBase + mainParams['out_matrix_base'] + '.mat')


                if not os.path.isfile(n_invt.inputs.out_file) or overwrite:
                    workFlow.connect([(n_flt,n_invt,[('out_matrix_file','in_file')])])

                #capture image of flirt results
                n_pngAppend = pe.Node(interface=Function(input_names=["in_file","reference","out_file"],
                                                                  output_names=[],
                                                                  function=st.flirt_pngappend),
                                                name='main_reg_overlay')
                n_pngAppend.inputs.out_file = os.path.join(mainFlirtOutputDir,os.path.basename(n_flt.inputs.out_matrix_file).split('.')[0] + '.png')
            
                n_pngAppend.inputs.reference=refImageFile
                workFlow.connect([(n_flt,n_pngAppend,[('out_file','in_file')])])

            # apply registration to secondary image
            # ----------------------------------
            if secImage:
                n_applyXfm = pe.Node(interface=fsl.ApplyXFM(),name='sec_reg_apply')
                n_applyXfm.inputs.apply_xfm = True
                applyBidsLabels = fltBidsLabels.copy()
                for k in secImageParams['output_bids_labels'].keys():
                    applyBidsLabels[k] = secImageParams['output_bids_labels'][k]
                n_applyXfm.inputs.out_file = os.path.join(mainFlirtOutputDir,st.get_bids_filename(subject=st.subject.id,session=st.subject.fullSesNum,**applyBidsLabels))
                
                workFlow.connect([(n_fslmaths,n_applyXfm,[('out_file','in_file')])])
                n_applyXfm.inputs.reference = refImageFile
                workFlow.connect([(n_flt,n_applyXfm,[('out_matrix_file','in_matrix_file')])])


                # if os.path.isfile(applyxfm.inputs.out_file) and not overwrite:
                #     if progress:
                #         os.system('echo "Skipping APPLYXFM: output transformed file already exists: ' + applyxfm.inputs.out_file + '"')
                        
                # else:
                #     if progress:
                #         os.system('echo "Applying transformation to secondary image to produce ' + applyxfm.inputs.out_file + '"')
                #     applyxfm.run()

                    # write JSON sidecar
                    # d['Sources'] = [d['Sources'],
                    #                 'bids:derivatives:' + applyxfm.inputs.in_matrix_file.split(DATA_DIR + os.sep)[1]]
                    # with open(applyxfm.inputs.out_file.split('.')[0] + '.json', 'w') as fp:
                    #     json.dump(d, fp, indent=4)  

            
                    # capture image of FLIRT results
                        
                for k in mainBidsLabels.keys():
                    if 'task' in k:
                        secImageParams['out_matrix_base'] = secImageParams['out_matrix_base'] + '_task-' + mainBidsLabels[k]
                    if 'run' in k:
                        secImageParams['out_matrix_base'] = secImageParams['out_matrix_base'] + '_run-' + mainBidsLabels[k]
                #capture image of flirt results
                n_pngAppend2 = pe.Node(interface=Function(input_names=["in_file","reference","out_file"],
                                                                  output_names=[],
                                                                  function=st.flirt_pngappend),
                                                name='sec_reg_overlay')
                n_pngAppend2.inputs.out_file = os.path.join(mainFlirtOutputDir,os.path.basename(n_flt.inputs.out_matrix_file).split('.')[0].replace(mainParams['out_matrix_base'],secImageParams['out_matrix_base']) + '.png')
                
            
                n_pngAppend2.inputs.reference=refImageFile
                workFlow.connect([(n_flt,n_pngAppend2,[('out_file','in_file')])])                                                                     



            # concatenate reference-to-standard to input-to-reference
            # ----------------------------------
            if not refImageParams['type'] == "std" and stdImageFile:
                strucRegPath = os.path.join(os.path.dirname(mainFlirtOutputDir),'anat')
                strucRegMatrix = refImageParams['out_matrix_base'] + '2' + stdImageParams['out_matrix_suffix'] + '.mat'
                strucRegMatrix = glob(os.path.join(os.path.dirname(os.path.dirname(mainFlirtOutputDir)),'**',strucRegMatrix), recursive=True)[0]
                if not os.path.isfile(strucRegMatrix):
                    os.system('echo "Warning: cannot find structural registration file ' + strucRegMatrix + '"')
                    os.system('echo "Skipping matrix concatenation"')
                    return

                if progress:
                    os.system('echo "Structural to standard registration found: ' + strucRegMatrix + '"')

                #find concat input-to-reference with reference-to-standard
                n_cvt = pe.Node(interface=fsl.ConvertXFM(),name='main_reg_concat') 
                n_cvt.inputs.in_file2 = strucRegMatrix
                n_cvt.inputs.concat_xfm = True
                n_cvt.inputs.out_file = os.path.join(mainFlirtOutputDir,inputMatrixBase + mainParams['out_matrix_base'] + '2' + stdImageParams['out_matrix_suffix'] + '.mat')
                

                workFlow.connect([(n_flt,n_cvt,[('out_matrix_file','in_file')])])


                # if not os.path.isfile(invt.inputs.out_file) or overwrite:
                #     invt.run()
                #     if progress:
                #         os.system('echo "\tSuccess!"')

                #find inverse
                n_invt2 = pe.Node(interface=fsl.ConvertXFM(),name='main_reg_concat_invert')
                n_invt2.inputs.invert_xfm = True
                n_invt2.inputs.out_file = os.path.join(mainFlirtOutputDir,stdImageParams['out_matrix_suffix'] + '2' + inputMatrixBase + mainParams['out_matrix_base'] + '.mat')


                workFlow.connect([(n_cvt,n_invt2,[('out_file','in_file')])])
                

                # if not os.path.isfile(invt.inputs.out_file) or overwrite:
                #     invt.run()


                #apply input-to-standard to input
                n_applyXfm2 = pe.Node(interface=fsl.ApplyXFM(),name='main_reg_concat_apply')

                n_applyXfm2.inputs.apply_xfm = True

                applyBidsLabels = mainBidsLabels.copy()
                for k in refImageParams['output_bids_labels'].keys():
                    applyBidsLabels[k] = stdImageParams['output_bids_labels'][k]
                n_applyXfm2.inputs.out_file = os.path.join(mainFlirtOutputDir,st.get_bids_filename(subject=st.subject.id,session=st.subject.fullSesNum,**applyBidsLabels))
                
                n_applyXfm2.inputs.reference = stdImageFile

                workFlow.connect([(n_bet,n_applyXfm2,[('out_file','in_file')])])
                workFlow.connect([(n_cvt,n_applyXfm2,[('out_file','in_matrix_file')])])

    

                # if os.path.isfile(applyxfm.inputs.out_file) and not overwrite:
                #     if progress:
                #         os.system('echo "Skipping APPLYXFM: output transformed file already exists: ' + applyxfm.inputs.out_file + '"')

                # else:
                #     if progress:
                #         os.system('echo "Applying ' + applyxfm.inputs.in_matrix_file + ' to ' + applyxfm.inputs.in_file + '"')
                #         os.system('echo "\tOut File: ' + applyxfm.inputs.out_file + '"')
                #     applyxfm.run()

                #     #write JSON sidecar
                #     d = {}
                #     d['Sources'] = ['bids:derivatives:' + applyxfm.inputs.in_file.split(DATA_DIR + os.sep)[1],
                #                     'bids:derivatives:' + applyxfm.inputs.in_matrix_file.split(DATA_DIR + os.sep)[1]]
                #     d['SpatialReference'] = 'file:' + applyxfm.inputs.reference
                #     if 'brain' in flt.inputs.in_file:
                #         d['SkullStripped'] = True
                #         d['Type'] = 'Brain'
                #     else:
                #         d['SkullStripped'] = False
                #     d['RegistrationFiles'] = ['bids:derivatives:' + flt.inputs.out_matrix_file.split(DATA_DIR + os.sep)[1],
                #                             'bids:derivatives:' + applyxfm.inputs.in_matrix_file.split(DATA_DIR + os.sep)[1]]
                #     for k in stdImageParams['output_json_values'].keys():
                #         d[k] = stdImageParams['output_json_values'][k]
                #     with open(applyxfm.inputs.out_file.split('.')[0] + '.json', 'w') as fp:
                #         json.dump(d, fp, indent=4)  

                    #create registration png
                n_pngAppend3 = pe.Node(interface=Function(input_names=["in_file","reference","out_file"],
                                                                output_names=[],
                                                                function=st.flirt_pngappend),
                                        name='main_reg_concat_overlay')
                n_pngAppend3.inputs.out_file = os.path.join(mainFlirtOutputDir,os.path.basename(n_cvt.inputs.out_file).split('.')[0] + '.png')
            
                n_pngAppend3.inputs.reference=stdImageFile
            
                workFlow.connect([(n_applyXfm2,n_pngAppend3,[('out_file','in_file')]) ]) 


                # (OPTIONAL) Apply to secondary image
                if secImage:
                    n_applyXfm3 = pe.Node(interface=fsl.ApplyXFM(),name='sec_reg_concat_apply')

                    n_applyXfm3.inputs.apply_xfm = True

                    for k in secImageParams['output_bids_labels'].keys():
                        applyBidsLabels[k] = secImageParams['output_bids_labels'][k]
                    n_applyXfm3.inputs.out_file = os.path.join(mainFlirtOutputDir,st.get_bids_filename(subject=st.subject.id,session=st.subject.fullSesNum,**applyBidsLabels))
                    
                    n_applyXfm3.inputs.reference = stdImageFile

                    workFlow.connect([(n_fslmaths,n_applyXfm3,[('out_file','in_file')])])
                    workFlow.connect([(n_cvt,n_applyXfm3,[('out_file','in_matrix_file')])])

                    

                    # if os.path.isfile(applyxfm.inputs.out_file) and not overwrite:
                    #     if progress:
                    #         os.system('echo "Skipping APPLYXFM: output transformed file already exists: ' + applyxfm.inputs.out_file + '"')

                    # else:
                    #     if progress:
                    #         os.system('echo "Applying ' + applyxfm.inputs.in_matrix_file + ' to ' + applyxfm.inputs.in_file + '"')
                    #         os.system('echo "\tOut File: ' + applyxfm.inputs.out_file + '"')
                    #     applyxfm.run()

                    #     #write JSON sidecar
                    #     l = d['Sources']
                    #     l.append('bids:derivatives:' + applyxfm.inputs.in_file.split(DATA_DIR + os.sep)[1])
                    #     d['Sources'] = l
                    #     with open(applyxfm.inputs.out_file.split('.')[0] + '.json', 'w') as fp:
                    #         json.dump(d, fp, indent=4) 


                    n_pngAppend4 = pe.Node(interface=Function(input_names=["in_file","reference","out_file"],
                                                                output_names=[],
                                                                function=st.flirt_pngappend),
                                        name='sec_reg_concat_overlay')
                    n_pngAppend4.inputs.out_file = os.path.join(mainFlirtOutputDir,os.path.basename(n_cvt.inputs.out_file).split('.')[0].replace(mainParams['out_matrix_base'],secImageParams['out_matrix_base']) + '.png')
                    
                
                    n_pngAppend4.inputs.reference=stdImageFile
                    workFlow.connect([(n_applyXfm3,n_pngAppend4,[('out_file','in_file')])])

                        



            #remove lingering matrix files left in the current working directory
            # for f in glob(os.path.join(os.getcwd(),'sub-' + subName + '*.mat')):
            #     os.remove(f)

            # outputFileList = glob(os.path.join(mainFlirtOutputDir,'*'))
            # if os.path.isdir(mainBetOutputDir):
            #     outputFileList.extend(glob(os.path.join(mainBetOutputDir,'*')))
            # os.system('echo "\n\nFLIRT (flirt.py, version ' + VERSION + ' ' + DATE + ') has successfully completed for input file: ' + mainFile + '\nThe files that have been produced:"')
            # print('\t',end='')
            # print(*outputFileList, sep = "\n\t")
            workFlow.run()
            workFlow.write_graph(graph2use='flat')
            workFlow.write_graph(dotfilename='graph.dot', graph2use='hierarchical', format='png', simple_form=True)


    except Exception as e:
        print("Error Message: {0}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        # sys.stdout = orig_stdout 
        # 

        # sys.stdout = orig_stdout
        # with open(os.path.join(mainFlirtOutputDir,'flirt.log'), 'a') as logFile:
        #     print('Got stdout: \n{0}'.format(bytes.getvalue().decode('utf-8')), file=logFile)       
        return

    # sys.stdout = orig_stdout
    # with open(os.path.join(mainFlirtOutputDir,'flirt.log'), 'a') as logFile:
    #     print('Got stdout: \n{0}'.format(bytes.getvalue().decode('utf-8')), file=logFile)



if __name__ == '__main__':
    """
    The entry point of this program for command-line utilization.
    """
    options = parser.parse_args()
    argsDict = {}
    if options.BET_PARAMS:
        argsDict['bet_params_file'] = options.BET_PARAMS
    if options.OVERWRITE:
        argsDict['overwrite'] = options.OVERWRITE
    if options.progress:
        argsDict['progress'] = options.progress
    flirt(options.IN_FILE,options.DATA_DIR,options.FLIRT_PARAMS,**argsDict)

    


