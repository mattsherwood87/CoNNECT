#!/resshare/general_processing_codes/python3_venv/bin/python
# the command above ^^^ sets python 3.10.10 as the interpreter for this program

# Created by Matthew Sherwood (matt.sherwood@wright.edu, matthew.sherwood.7.ctr@us.af.mil)
# Created on 26 Jan 2021
#
# Modified on 29 Sept 2023 - add support for antspynet brain segmentation
# Modified on 28 July 2023 - add some corrections for multiple image types with difference acq parameters in same session
# Modified on 26 April 2023 - update to WSU
# Modified on 27 Sept 2021 - update to align with direct s3 mount
# Modified on 26 Jan 2021

import sys
import os
os.environ['MPLCONFIGDIR'] = '/resshare/.config/matplotlib'
import argparse
# import boto3
import re
import json
import subprocess
from nipype.interfaces import fsl
# from nipype.interfaces import ants
import ants
import antspynet
from glob import glob as glob
import logging

#local import
# REALPATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
# sys.path.append(REALPATH)
REALPATH = os.path.join('/resshare','general_processing_codes')
sys.path.append(REALPATH)
from helper_functions.flirt_pngappend import *
from helper_functions.get_dir_identifiers import *
from helper_functions.bids_commands import *


VERSION = '3.1.0'
DATE = '29 Sep 2023'


parser = argparse.ArgumentParser('flirt.py: perform FLIRT registration between input and reference/standard brain images')
FSLDIR = os.environ["FSLDIR"]

logger = logging.getLogger(__name__)

# s3 = boto3.resource('s3')
#

def parse_arguments():

    #input options for main()
    parser.add_argument('IN_FILE')
    parser.add_argument('DATA_DIR')
    parser.add_argument('FLIRT_PARAMS')
    parser.add_argument('--bet-params',action='store',dest='BET_PARAMS',default=None)
    parser.add_argument('--flirt-params',action='store',dest='FLIRT_PARAMS',default=None)
    parser.add_argument('--overwrite',action='store_true',dest='OVERWRITE',default=False)
    parser.add_argument('--progress',action='store_true',dest='progress',default=False)
    options = parser.parse_args()
    return options


# ******************* s3 bucket check ********************
def flirt(IN_FILE,DATA_DIR,FLIRT_PARAMS,*args,**kwargs):
    """
    This function performs FLIRT registration between IN_FILE and structural/standard brain images. Brain extraction will be performed on IN_FILE prior to registration if bet_params is specified.

    flirt(IN_FILE,DATA_DIR,FLIRT_PARAMS,overwrite=False,bet_params=None,progress=False)

    Arguments:

        IN_FILE (str): fullpath to a NIfTI file

        DATA_DIR (str): fullpath to the project's data directory (project's 'dataDir' credential)

        FLIRT_PARAMS (str): fullpath to project's 2D ASL FLIRT parameter file

        args (str): a sequence of program arguments
            
        bet_params (str): OPTIONAL fullpath to project's brain extraction parameter file
            
        overwrite (BOOL): OPTIONAL flag to overwrite existing files (True) or not (False) 
            
        progress (BOOL): OPTIONAL flag to display command line output providing additional details on the processing status

    Returns:
        None
    """
    
    overwriteFlag = kwargs.get('overwrite',False)
    betParamsFile = kwargs.get('bet_params',None)
    progress = kwargs.get('progress',False)
    stdImageFile = None
    stdImage = False
    performFslRoi = False
    performBet = False
    secImage = False
    refImageFile = None
    refImage = False

    
    now = datetime.datetime.now()

    ls_logStrs = []
        
    try:
    
        if progress:
            ls_logStrs.append('flirt.py version ' + VERSION + ' dated ' + DATE)
            ls_logStrs.append('running @ ' + now.strftime("%m-%d-%Y %H:%M:%S"))
            ls_logStrs.append("Reading JSON Files")

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
                        ls_logStrs.append("WARNING: reference file specified in parameter file but the file cannot be located - " + stdImageFile)
                        ls_logStrs.append("/tSkipping standard transformation and/or concatenation")
                        stdImage = False
                else:
                    ls_logStrs.append("WARNING: standard reference type not supported")
                    ls_logStrs.append("/tSkipping standard transformation and/or concatenation")
            else:
                ls_logStrs.append("WARNING: must specify type in standard_reference_params field")
                ls_logStrs.append("/tSkipping standard transformation and/or concatenation")

        if betParamsFile:
            with open(betParamsFile) as j:
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
                ls_logStrs.append("Main Image File Not Found")
            return
        elif progress:
            ls_logStrs.append("Main Image File Found: " + mainFile)

        #make output directory structure if it does not exist
    
        # create file inputs and outputs
        mainFileDir = os.path.dirname(mainFile)
        subName, sesNum = get_dir_identifiers(mainFileDir)
        mainFlirtOutputDir = os.path.join(DATA_DIR,'derivatives','sub-' + subName,'ses-' + sesNum,'flirt',mainParams['output_bids_location'])#create base path and filename for move
        mainBetOutputDir = os.path.join(DATA_DIR,'derivatives','sub-' + subName,'ses-' + sesNum,'bet',mainParams['output_bids_location'])#create base path and filename for move

        if not os.path.isdir(mainFlirtOutputDir):
            os.makedirs(mainFlirtOutputDir)
        if performBet:
            if not os.path.isdir(mainBetOutputDir) and betParamsFile:
                os.makedirs(mainBetOutputDir)
            os.chdir(mainBetOutputDir)

        
        logging.basicConfig(filename=os.path.join(mainFlirtOutputDir,'flirt.log'), level=logging.DEBUG)
        for logStr in ls_logStrs:
            logger.info(logStr)

        #look for accompanying structural data on disk in derivatives
        if refImage and not refImageParams['type'] == 'std':
            ref_regexStr = get_bids_filename(**refImageParams['input_bids_labels'])
            if refImageParams['input_bids_location'] == 'rawdata':
                refImageFile = glob(os.path.join(os.path.dirname(mainFileDir),'anat','*' + ref_regexStr + '*'))
            elif refImageParams['input_bids_location'] == 'derivatives':
                refImageFile = glob(os.path.join(os.path.dirname(mainBetOutputDir),'anat','*' + ref_regexStr + '*'))
            else:
                logger.error('structural file "bids_location" not supported')
                logger.error('/tCannot perform FLIRT... exiting')
                return

            if refImage:
                if len(refImageFile) > 0:
                    refImageFile = refImageFile[0]
                elif refImageParams['input_bids_location'] == 'rawdata':
                    logger.error('structural file ' + os.path.join(os.path.dirname(mainFileDir),'anat','*' + ref_regexStr + '*') + ' not found')
                    logger.error('/tCannot perform FLIRT... exiting')
                    return
                elif refImageParams['input_bids_location'] == 'derivatives':
                    logger.error('structural file ' + os.path.join(os.path.dirname(mainBetOutputDir),'anat','*' + ref_regexStr + '*') + ' not found')
                    logger.error('/tCannot perform FLIRT... exiting')
                    return

            if progress and refImageFile:
                logger.info('Reference Structural File Found: ' + refImageFile)

        elif stdImageFile:
            refImageFile = stdImageFile

        else:
            logger.error("ERROR: standard reference file not found")
            logger.error("/tCannot perform FLIRT... exiting")
            return
        

        mainBidsLabels = get_bids_labels(mainFile)
        if secImage:
            # secBidsLabels = mainBidsLabels.copy()
            secBidsLabels = {}
            for k in secImageParams['input_bids_labels'].keys():
                secBidsLabels[k] = secImageParams['input_bids_labels'][k]
            for k in mainBidsLabels.keys():
                if 'task' in k or 'run' in k:
                    secBidsLabels[k] = mainBidsLabels[k]
            sec_regexStr = get_bids_filename(**secBidsLabels)
            secFile = glob(os.path.join(mainFileDir,'*' + sec_regexStr))
            # secFile = [x for x in secFile if 'acq-' + mainBidsLabels['acquisition'].split('-')[0] in x]
            if len(secFile) > 0:
                secFile = secFile[0]
            else:
                logger.warning('WARNING: secondary image file ' + os.path.join(os.path.dirname(mainFileDir),'*' + sec_regexStr + '*') + ' not found... skipping')
                
            if progress and secFile:
                logger.info('Secondary File Found: ' + secFile)


        # **********************************
        # get single volume for registration (maybe better with mean after running mcflirt?) 
        # **********************************
        if performFslRoi:
            if type(mainParams['volume']) is int:
                proc = subprocess.check_output(os.path.join(FSLDIR,'bin','fslval') + ' ' + mainFile + ' dim4',shell=True,encoding='utf-8')
                totalVols = int(proc.split(' ')[0])
                vols = mainParams['volume']
                if not vols < totalVols:
                    logger.warning('user selected volume #' + vols + ' but the image only containins ' + totalVols)
                    logger.warning('/tDefaulting to volume 1')
                    vols = 1
            elif mainParams['volume'] == 'center':
                proc = subprocess.check_output(os.path.join(FSLDIR,'bin','fslval') + ' ' + mainFile + ' dim4',shell=True,encoding='utf-8')
                totalVols = int(proc.split(' ')[0])
                vols = int(totalVols/2)
            else:
                logger.warning('improper volume selection, skipping volume extraction')
                vols = None

            if vols:
                roi_mainBidsLabels = mainBidsLabels.copy()
                roi_mainBidsLabels['process'] = 'fslroi'
                roi_mainBidsLabels['description'] = 'vol-' + str(vols)
                for k in mainParams['output_bids_labels'].keys():
                    roi_mainBidsLabels[k] = mainParams['output_bids_labels'][k]
                outMainVolFile = os.path.join(mainBetOutputDir,get_bids_filename(subject=subName,session=sesNum,**roi_mainBidsLabels))


                if os.path.isfile(outMainVolFile) and not overwriteFlag:
                    mainFile = outMainVolFile
                    if progress:
                        logger.info('Single volume file already exists: ' + outMainVolFile)

                else:
                    fslroi = fsl.ExtractROI(in_file=mainFile,roi_file=outMainVolFile,t_min=vols,t_size=1)
                    fslroi.run()
                    if progress:
                        logger.info('Creating single volume file from volume #' + str(vols) + ' as ' + outMainVolFile)

                    #write JSON sidecar file
                    d = {}
                    d['Sources'] = ['bids:raw:' + fslroi.inputs.in_file.split(DATA_DIR + os.sep)[1]]
                    d['FslRoiParameters'] = {'t_min': vols, 't_size': 1}
                    d['SkullStripped'] = 'false'
                    for k in mainParams['output_json_values'].keys():
                        d[k] = mainParams['output_json_values'][k]
                    with open(fslroi.inputs.roi_file.split('.')[0] + '.json', 'w') as fp:
                        json.dump(d, fp, indent=4) 
                    
                    mainFile = fslroi.inputs.roi_file


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

            mainFile_brain = os.path.join(mainBetOutputDir,get_bids_filename(subject=subName,session=sesNum,**bet_mainBidsLabels))
            
            bet_mainBidsLabels['suffix'] = 'mask'
            mainFile_brainmask = os.path.join(mainBetOutputDir,get_bids_filename(subject=subName,session=sesNum,**bet_mainBidsLabels))
                        
            #continue with BET?
            if os.path.isfile(mainFile_brain) and not overwriteFlag:
                if progress:
                    logger.info('Skipping BET: brain extracted file found: ' + mainFile_brain)
                mainFile = mainFile_brain
                    
            else:
                if progress:
                    logger.info('Performing BET on ' + mainFile)
                    logger.info('\tOUTPUT: ' + mainFile_brain)

                if betType == 'FSL':
                    btr = fsl.BET(**betParams)
                    btr.inputs.in_file = mainFile
                    btr.inputs.out_file = mainFile_brain
                    betInFile = btr.inputs.in_file
                    betOutFile = btr.inputs.out_file
                    btr.run()

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
                    inImg = ants.image_read(mainFile)
                    brainSeg = antspynet.brain_extraction(inImg, modality=betParams['modality'], antsxnet_cache_directory=os.path.join(REALPATH,'helper_functions','antsxnet_cache'), verbose=True)
                    brainSeg.to_file(os.path.join(os.path.dirname(mainFile_brain),'antspynet_brainseg.nii.gz'))

                    #create brainmask and brain image
                    os.system('fslmaths ' + os.path.join(os.path.dirname(mainFile_brain),'antspynet_brainseg.nii.gz') + ' -thr 0.9 -bin ' + mainFile_brainmask)
                    
                    os.system('fslmaths ' + mainFile + ' -mas ' + mainFile_brainmask + ' ' + mainFile_brain)
                    
                    betInFile = mainFile
                    betOutFile = mainFile_brain
                
                #write JSON sidecar file
                d = {}
                d['BetProgram'] = betType
                d['BetParameters'] = betParams.copy()
                if 'derivatives' in betInFile:
                    d['Sources'] = 'bids:derivatives:' + betInFile.split(DATA_DIR + os.sep)[1]
                else:
                    d['Sources'] = 'bids:raw:' + betInFile.split(DATA_DIR + os.sep)[1]
                d['SkullStripped'] = True
                d['Type'] = 'Brain'
                for k in mainParams['output_json_values'].keys():
                    d[k] = mainParams['output_json_values'][k]

                with open(betOutFile.split('.')[0] + '.json', 'w') as fp:
                    json.dump(d, fp, indent=4)


                    
                # create brain mask (all but antspynet)
                # ----------------------------------
                if betType == 'FSL':
                    os.system('fslmaths ' + betOutFile + ' -bin ' + mainFile_brainmask)
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




                #create tile mosaic overlay
                os.system('ConvertScalarImageToRGB 3 ' + mainFile_brain + ' ' + mainFile_brain.replace('brain','brain-red') + ' none red')
                if progress:
                    print('\tCreated ' + mainFile_brain.replace('brain','brain-red') + ' for tile mosaic creation')

                mosaicCmd = 'CreateTiledMosaic -i ' + mainFile + ' -r ' + mainFile_brain.replace('brain','brain-red') + ' -o ' + mainFile_brain.replace('.nii.gz','-brain-mosaic.png').replace('sub-' + subName + '_ses-' + sesNum + '_','')
                for k in betFullParams['mosaic_params'].keys():
                    if len(k) == 1:
                        mosaicCmd = mosaicCmd + ' -' + k + ' ' + betFullParams['mosaic_params'][k]
                    else:
                        mosaicCmd = mosaicCmd + ' --' + k + ' ' + betFullParams['mosaic_params'][k]
                os.system(mosaicCmd)
                

                if progress:
                    os.system('echo -n "\tDone creating Tile Mosaic"')


                #write corresponding JSON file
                d['Sources'] = [d['Sources'],
                    'bids:derivatives:' + betOutFile.split(DATA_DIR + os.sep)[1]]
                d['SkullStripped'] = True
                d['Type'] = 'Brain'
                for k in mainParams['output_json_values'].keys():
                    d[k] = mainParams['output_json_values'][k]

                with open(mainFile_brainmask.split('.')[0] + '.json', 'w') as fp:
                    json.dump(d, fp, indent=4) 

                mainFile = mainFile_brain


                # apply brain mask to secondary image?
                # -------------------------------
                if secImage:
                    secBidsLabels = get_bids_labels(secFile)
                    secBidsLabels['process'] = bet_mainBidsLabels['process']
                    secBidsLabels['resolution'] = 'lo'
                    secBidsLabels['description'] = 'brain'
                    secBidsLabels['extension'] = 'nii.gz'
                    secFile_brain = os.path.join(mainBetOutputDir,get_bids_filename(subject=subName,session=sesNum,**secBidsLabels))
                    os.system('fslmaths ' + secFile + ' -mas ' + mainFile_brainmask + ' ' + secFile_brain)

                    #write corresponding JSON file
                    d = {}
                    d['BetProgram'] = betType
                    d['BetParameters'] = betParams.copy()
                    d['Sources'] = ['bids:raw:' + secFile.split(DATA_DIR + os.sep)[1],
                                    'bids:derivatives:' + mainFile_brainmask.split(DATA_DIR + os.sep)[1]]
                    d['SkullStripped'] = True
                    d['Type'] = 'Brain'
                    for k in mainParams['output_json_values'].keys():
                        d[k] = mainParams['output_json_values'][k]

                    with open(secFile_brain.split('.')[0] + '.json', 'w') as fp:
                        json.dump(d, fp, indent=4)   
                    
                    secFile = secFile_brain


        # **********************************
        # run FLIRT on Main Image Input
        # **********************************

        ###neeed to check if output exists?????
        if refImageFile:
            flt = fsl.FLIRT(**flirtParams)
            flt.inputs.in_file = mainFile
            flt.inputs.reference = refImageFile
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
            flt.inputs.out_file = os.path.join(mainFlirtOutputDir,get_bids_filename(subject=subName,session=sesNum,**fltBidsLabels))
            inputMatrixBase = get_bids_labels(IN_FILE)
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
                flt.inputs.out_matrix_file = os.path.join(mainFlirtOutputDir,inputMatrixBase + mainParams['out_matrix_base'] + '2' + stdImageParams['out_matrix_suffix'] + '.mat')
            else:
                flt.inputs.out_matrix_file = os.path.join(mainFlirtOutputDir,inputMatrixBase + mainParams['out_matrix_base'] + '2' + refImageParams['out_matrix_base'] + '.mat')


            if os.path.isfile(flt.inputs.out_matrix_file) and not overwriteFlag:
                if progress:
                    logger.info('Skipping FLIRT: registration matrix file found: ' + flt.inputs.out_matrix_file)
                    
            else:
                if progress:
                    logger.info('Performing FLIRT:')
                    logger.info('\tInput File: ' + flt.inputs.in_file)
                    logger.info('\tReference: ' + flt.inputs.reference)
                    logger.info('\tOut File: ' + flt.inputs.out_file)
                    logger.info('\tOut Matrix File: ' + flt.inputs.out_matrix_file)
                flt.run()
                if progress:
                    logger.info('\tSuccess!')


                # invert registration matrix
                # ----------------------------------
                invt = fsl.ConvertXFM()
                invt.inputs.in_file = flt.inputs.out_matrix_file
                invt.inputs.invert_xfm = True
                if refImageParams['type'] == 'std':
                    invt.inputs.out_file = os.path.join(mainFlirtOutputDir,stdImageParams['out_matrix_suffix'] + '2' + inputMatrixBase + mainParams['out_matrix_base'] + '.mat')
                else:
                    invt.inputs.out_file = os.path.join(mainFlirtOutputDir,refImageParams['out_matrix_base'] + '2' + inputMatrixBase + mainParams['out_matrix_base'] + '.mat')

                #write corresponding JSON files
                d = {}
                d['FslFlirtParameters'] = flirtParams
                d['Sources'] = 'bids:derivatives:' + flt.inputs.in_file.split(DATA_DIR + os.sep)[1]
                if refImageParams['type'] == 'std':
                    d['SpatialReference'] = 'file:' + flt.inputs.reference
                    for k in stdImageParams['output_json_values'].keys():
                        d[k] = stdImageParams['output_json_values'][k]
                else:
                    d['SpatialReference'] = 'bids:' + refImageParams['input_bids_location'] + ':' + flt.inputs.reference.split(DATA_DIR + os.sep)[1]
                    for k in refImageParams['output_json_values'].keys():
                        d[k] = refImageParams['output_json_values'][k]
                if 'brain' in flt.inputs.in_file:
                    d['SkullStripped'] = True
                    d['Type'] = 'Brain'
                else:
                    d['SkullStripped'] = False
                d['RegistrationFiles'] = ['bids:derivatives:' + flt.inputs.out_matrix_file.split(DATA_DIR + os.sep)[1],
                                        'bids:derivatives:' + invt.inputs.out_file.split(DATA_DIR + os.sep)[1]]
                with open(flt.inputs.out_file.split('.')[0] + '.json', 'w') as fp:
                    json.dump(d, fp, indent=4)  


                if not os.path.isfile(invt.inputs.out_file) or overwriteFlag:
                    invt.run() 

                #capture image of flirt results
                flirt_pngappend(flt.inputs.out_file,flt.inputs.reference,os.path.join(mainFlirtOutputDir,os.path.basename(flt.inputs.out_matrix_file).split('.')[0] + '.png'))

            
            # apply registration to secondary image
            # ----------------------------------
            if secImage:
                applyxfm = fsl.ApplyXFM()
                applyxfm.inputs.in_file = secFile
                applyxfm.inputs.reference = refImageFile
                applyxfm.inputs.apply_xfm = True
                applyBidsLabels = fltBidsLabels.copy()
                for k in secImageParams['output_bids_labels'].keys():
                    applyBidsLabels[k] = secImageParams['output_bids_labels'][k]
                applyxfm.inputs.out_file = os.path.join(mainFlirtOutputDir,get_bids_filename(subject=subName,session=sesNum,**applyBidsLabels))
                applyxfm.inputs.in_matrix_file = flt.inputs.out_matrix_file


                if os.path.isfile(applyxfm.inputs.out_file) and not overwriteFlag:
                    if progress:
                        logger.info('Skipping APPLYXFM: output transformed file already exists: ' + applyxfm.inputs.out_file)
                        
                else:
                    if progress:
                        os.system('echo "Applying transformation to secondary image to produce ' + applyxfm.inputs.out_file + '"')
                    applyxfm.run()

                    # write JSON sidecar
                    d['Sources'] = [d['Sources'],
                                    'bids:derivatives:' + applyxfm.inputs.in_matrix_file.split(DATA_DIR + os.sep)[1]]
                    with open(applyxfm.inputs.out_file.split('.')[0] + '.json', 'w') as fp:
                        json.dump(d, fp, indent=4)  

            
                    # capture image of FLIRT results
                        
                    for k in mainBidsLabels.keys():
                        if 'task' in k:
                            secImageParams['out_matrix_base'] = secImageParams['out_matrix_base'] + '_task-' + mainBidsLabels[k]
                        if 'run' in k:
                            secImageParams['out_matrix_base'] = secImageParams['out_matrix_base'] + '_run-' + mainBidsLabels[k]
                    flirt_pngappend(flt.inputs.out_file,flt.inputs.reference,os.path.join(mainFlirtOutputDir,os.path.basename(applyxfm.inputs.in_matrix_file).split('.')[0].replace(mainParams['out_matrix_base'],secImageParams['out_matrix_base']) + '.png'))                                                                           



            # concatenate reference-to-standard to input-to-reference
            # ----------------------------------
            if not refImageParams['type'] == "std" and stdImageFile:
                strucRegPath = os.path.join(os.path.dirname(mainFlirtOutputDir),'anat')
                strucRegMatrix = os.path.join(strucRegPath,refImageParams['out_matrix_base'] + '2' + stdImageParams['out_matrix_suffix'] + '.mat')
                if not os.path.isfile(strucRegMatrix):
                    logger.warning('cannot find structural registration file ' + strucRegMatrix)
                    logger.info('Skipping matrix concatenation')
                    return

                if progress:
                    logger.info('Structural to standard registration found: ' + strucRegMatrix)

                #find concat input-to-reference with reference-to-standard
                invt = fsl.ConvertXFM()
                invt.inputs.in_file = flt.inputs.out_matrix_file
                invt.inputs.in_file2 = strucRegMatrix
                invt.inputs.concat_xfm = True
                invt.inputs.out_file = os.path.join(mainFlirtOutputDir,inputMatrixBase + mainParams['out_matrix_base'] + '2' + stdImageParams['out_matrix_suffix'] + '.mat')
                if progress:
                    logger.info('Concatenating FLIRT transform with standard transform:')
                    logger.info('\tInput File: ' + invt.inputs.in_file)
                    logger.info('\tInput FIle 2: ' + invt.inputs.in_file2)
                    logger.info('\tOut File: ' + invt.inputs.out_file)


                if not os.path.isfile(invt.inputs.out_file) or overwriteFlag:
                    invt.run()
                    if progress:
                        logger.info('\tSuccess!')

                #find inverse
                invt = fsl.ConvertXFM()
                invt.inputs.in_file = os.path.join(mainFlirtOutputDir,inputMatrixBase + mainParams['out_matrix_base'] + '2' + stdImageParams['out_matrix_suffix'] + '.mat')
                invt.inputs.invert_xfm = True
                invt.inputs.out_file = os.path.join(mainFlirtOutputDir,stdImageParams['out_matrix_suffix'] + '2' + inputMatrixBase + mainParams['out_matrix_base'] + '.mat')


                if not os.path.isfile(invt.inputs.out_file) or overwriteFlag:
                    invt.run()


                #apply input-to-standard to input
                applyxfm = fsl.ApplyXFM()
                applyxfm.inputs.in_file = mainFile
                applyxfm.inputs.reference = stdImageFile
                applyxfm.inputs.apply_xfm = True
                applyBidsLabels = mainBidsLabels.copy()
                for k in refImageParams['output_bids_labels'].keys():
                    applyBidsLabels[k] = stdImageParams['output_bids_labels'][k]
                applyxfm.inputs.out_file = os.path.join(mainFlirtOutputDir,get_bids_filename(subject=subName,session=sesNum,**applyBidsLabels))
                applyxfm.inputs.in_matrix_file = os.path.join(mainFlirtOutputDir,inputMatrixBase + mainParams['out_matrix_base'] + '2' + stdImageParams['out_matrix_suffix'] + '.mat')


                if os.path.isfile(applyxfm.inputs.out_file) and not overwriteFlag:
                    if progress:
                        logger.info('Skipping APPLYXFM: output transformed file already exists: ' + applyxfm.inputs.out_file)

                else:
                    if progress:
                        logger.info('Applying ' + applyxfm.inputs.in_matrix_file + ' to ' + applyxfm.inputs.in_file)
                        logger.info('\tOut File: ' + applyxfm.inputs.out_file)
                    applyxfm.run()

                    #write JSON sidecar
                    d = {}
                    d['Sources'] = ['bids:derivatives:' + applyxfm.inputs.in_file.split(DATA_DIR + os.sep)[1],
                                    'bids:derivatives:' + applyxfm.inputs.in_matrix_file.split(DATA_DIR + os.sep)[1]]
                    d['SpatialReference'] = 'file:' + applyxfm.inputs.reference
                    if 'brain' in flt.inputs.in_file:
                        d['SkullStripped'] = True
                        d['Type'] = 'Brain'
                    else:
                        d['SkullStripped'] = False
                    d['RegistrationFiles'] = ['bids:derivatives:' + flt.inputs.out_matrix_file.split(DATA_DIR + os.sep)[1],
                                            'bids:derivatives:' + applyxfm.inputs.in_matrix_file.split(DATA_DIR + os.sep)[1]]
                    for k in stdImageParams['output_json_values'].keys():
                        d[k] = stdImageParams['output_json_values'][k]
                    with open(applyxfm.inputs.out_file.split('.')[0] + '.json', 'w') as fp:
                        json.dump(d, fp, indent=4)  

                    #create registration png
                    flirt_pngappend(applyxfm.inputs.out_file,applyxfm.inputs.reference,os.path.join(mainFlirtOutputDir,os.path.basename(applyxfm.inputs.in_matrix_file).split('.')[0] + '.png'))


                # (OPTIONAL) Apply to secondary image
                if secImage:
                    applyxfm = fsl.ApplyXFM()
                    applyxfm.inputs.in_file = secFile
                    applyxfm.inputs.reference = stdImageFile
                    applyxfm.inputs.apply_xfm = True
                    for k in secImageParams['output_bids_labels'].keys():
                        applyBidsLabels[k] = secImageParams['output_bids_labels'][k]
                    applyxfm.inputs.out_file = os.path.join(mainFlirtOutputDir,get_bids_filename(subject=subName,session=sesNum,**applyBidsLabels))
                    applyxfm.inputs.in_matrix_file = os.path.join(mainFlirtOutputDir,inputMatrixBase + mainParams['out_matrix_base'] + '2' + stdImageParams['out_matrix_suffix'] + '.mat')



                    if os.path.isfile(applyxfm.inputs.out_file) and not overwriteFlag:
                        if progress:
                            logger.info('Skipping APPLYXFM: output transformed file already exists: ' + applyxfm.inputs.out_file)

                    else:
                        if progress:
                            logger.info('Applying ' + applyxfm.inputs.in_matrix_file + ' to ' + applyxfm.inputs.in_file)
                            logger.info('\tOut File: ' + applyxfm.inputs.out_file)
                        applyxfm.run()

                        #write JSON sidecar
                        l = d['Sources']
                        l.append('bids:derivatives:' + applyxfm.inputs.in_file.split(DATA_DIR + os.sep)[1])
                        d['Sources'] = l
                        with open(applyxfm.inputs.out_file.split('.')[0] + '.json', 'w') as fp:
                            json.dump(d, fp, indent=4) 

                        

                        #run pngappend
                        flirt_pngappend(applyxfm.inputs.out_file,applyxfm.inputs.reference,os.path.join(mainFlirtOutputDir,os.path.basename(applyxfm.inputs.in_matrix_file).split('.')[0].replace(mainParams['out_matrix_base'],secImageParams['out_matrix_base']) + '.png'))


            #remove lingering matrix files left in the current working directory
            for f in glob(os.path.join(os.getcwd(),'sub-' + subName + '*.mat')):
                os.remove(f)

            outputFileList = glob(os.path.join(mainFlirtOutputDir,'*'))
            if os.path.isdir(mainBetOutputDir):
                outputFileList.extend(glob(os.path.join(mainBetOutputDir,'*')))
            logger.info('FLIRT (flirt.py, version ' + VERSION + ' ' + DATE + ') has successfully completed for input file: ' + mainFile)
            logger.info('The files that have been produced:')
            # print('\t',end='')
            for outF in outputFileList:
                logger.info(outF)
            # print(*outputFileList, sep = "\n\t")


    except Exception as e:
        print("Error Message: {0}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        logger.error(e.Message,exc_info=sys.exc_info())
        # sys.stdout = orig_stdout 
        # 

        # sys.stdout = orig_stdout
        # with open(os.path.join(mainFlirtOutputDir,'flirt.log'), 'a') as logFile:
        #     print('Got stdout: \n{0}'.format(bytes.getvalue().decode('utf-8')), file=logFile)       
        return

    # sys.stdout = orig_stdout
    # with open(os.path.join(mainFlirtOutputDir,'flirt.log'), 'a') as logFile:
    #     print('Got stdout: \n{0}'.format(bytes.getvalue().decode('utf-8')), file=logFile)


def main():
    """
    The entry point of this program.
    """
    options = parse_arguments()
    argsDict = {}
    if options.BET_PARAMS:
        argsDict['bet_params'] = options.BET_PARAMS
    if options.OVERWRITE:
        argsDict['overwrite'] = options.OVERWRITE
    if options.progress:
        argsDict['progress'] = options.progress
    flirt(options.IN_FILE,options.DATA_DIR,options.FLIRT_PARAMS,**argsDict)


if __name__ == '__main__':
    main()

    


