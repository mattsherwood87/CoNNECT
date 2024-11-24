# dti_flirt.py

# Created by Matthew Sherwood (matt.sherwood@wright.edu, matthew.sherwood.7.ctr@us.af.mil)
# Created on 26 July 2023
#
# Modified on 

import sys
import os
import argparse
import json
from nipype.interfaces import fsl
from glob import glob as glob
import datetime

#local import
REALPATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
# sys.path.append(REALPATH)
# REALPATH = os.path.join('/resshare','general_processing_codes')
sys.path.append(REALPATH)
import support_tools as st


VERSION = '1.0.0'
DATE = '26 July 2023'


FSLDIR = os.environ["FSLDIR"]


parser = argparse.ArgumentParser('asl_flirt.py: perform FLIRT registration between 2D ASL and structural/standard brain images')
parser.add_argument('-i', required=True, action='store',dest='IN_FILE', help='Input DTI file')
parser.add_argument('-d', required=True,action='store',dest='DATA_DIR', help="Project's directory on disk (see dataDir key in credentials JSON file)")
parser.add_argument('-f', required=True, action='store',dest='FLIRT_PARAMS', help='Path to the FLIRT parameter JSON control file')
parser.add_argument('--flirt-params',action='store',dest='FLIRT_PARAMS',default=None)
parser.add_argument('--overwrite',action='store_true',dest='OVERWRITE',default=False)
parser.add_argument('--progress',action='store_true',dest='progress',default=False)


# ******************* s3 bucket check ********************
def dti_flirt(IN_FILE: str, DATA_DIR: str, FLIRT_PARAMS: str, overwrite: bool=False, progress: bool=False):
    """
    This function performs FLIRT registration between IN_FILE and structural/standard brain images similar to flirt.py. Registration will be applied to all secondary images in the same directory as IN_FILE.

    dti_flirt(IN_FILE,DATA_DIR,FLIRT_PARAMS,overwrite=False,progress=False)

    :param IN_FILE: fullpath to a NIfTI file
    :type IN_FILE: str

    :param DATA_DIR: fullpath to the project's data directory (project's 'dataDir' credential)
    :type DATA_DIR: str

    :param FLIRT_PARAMS: fullpath to project's 2D ASL FLIRT parameter file
    :type FLIRT_PARAMS: str

    :param overwrite: OPTIONAL flag to overwrite existing files (default=False)
    :type overwrite: bool

    :param progress: OPTIONAL flag to display command line output providing additional details on the processing status
    :type progress: bool

    :raises FileNotFoundError: FLIRT_PARAMS file not found on disk

    :raises Exception: general error encountered during execution

    :return: None
    """
    
    outputFileList = []
    stdImageFile = None
    refImageFile = None
    refImage = False

    try:
        now = datetime.datetime.now()

        struc_regexStr = None
        if progress:
            print('\n\nflirt.py version ' + VERSION + ' dated ' + DATE + '\n')
            print('running @ ' + now.strftime("%m-%d-%Y %H:%M:%S") + '\n')
            print('Reading JSON Files')

        try:
            with open(FLIRT_PARAMS) as j:
                flirtFullParams = json.load(j)

            #get main image parameters
            if 'main_image_params' in flirtFullParams:
                mainParams = flirtFullParams.pop('main_image_params')
                
            #get main FLIRT parameters
            if 'flirt_params' in flirtFullParams:
                flirtParams = flirtFullParams.pop('flirt_params')

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
                            print('WARNING: reference file specified in parameter file but the file cannot be located - ' + stdImageFile)
                            print('/tSkipping standard transformation and/or concatenation')
                            stdImage = False
                    else:
                        print('WARNING: standard reference type not supported')
                        print('/tSkipping standard transformation and/or concatenation')
                else:
                    print('WARNING: must specify type in standard_reference_params field')
                    print('/tSkipping standard transformation and/or concatenation')

        except FileNotFoundError as e:
            print("Error Message: {0}".format(e))
            return


        #check if file exists on local disk
        mainFile = IN_FILE
        if not os.path.isfile(mainFile):
            if progress:
                print('ERROR: Main Image File Not Found')
            return
        elif progress:
            print('Main Image File Found: ' + mainFile)
        
        # create file inputs and outputs
        mainFileDir = os.path.dirname(mainFile)
        st.subject.get_id(mainFileDir)
        mainFlirtOutputDir = os.path.join(DATA_DIR,'derivatives','sub-' + st.subject.id,'ses-' + st.subject.sesNum,'flirt',mainParams['output_bids_location'])#create base path and filename for move
        if not os.path.isdir(mainFlirtOutputDir):
            os.makedirs(mainFlirtOutputDir)

        #look for accompanying structural data on disk in derivatives
        if refImage and not refImageParams['type'] == 'std':
            ref_regexStr = st.bids.get_bids_filename(**refImageParams['input_bids_labels'])
            if refImageParams['input_bids_location'] == 'raw':
                refImageFile = glob(os.path.join(DATA_DIR,'rawdata','sub-' + st.subject.id,'ses-' + st.subject.sesNum,'anat','*' + ref_regexStr + '*'))
            elif refImageParams['input_bids_location'] == 'derivatives':
                refImageFile = glob(os.path.join(DATA_DIR,'derivatives','sub-' + st.subject.id,'ses-' + st.subject.sesNum,'bet','anat','*' + ref_regexStr + '*'))
            else:
                print('ERROR: structural file "bids_location" not supported')
                print('/tCannot perform FLIRT... exiting')
                return

            if refImage:
                if len(refImageFile) > 0:
                    refImageFile = refImageFile[0]
                elif refImageParams['input_bids_location'] == 'rawdata':
                    print('ERROR: structural file ' + os.path.join(DATA_DIR,'rawdata','sub-' + st.subject.id,'ses-' + st.subject.sesNum,'anat','*' + ref_regexStr + '*') + ' not found')
                    print('/tCannot perform FLIRT... exiting')
                    return
                elif refImageParams['input_bids_location'] == 'derivatives':
                    print('ERROR: structural file ' + os.path.join(DATA_DIR,'derivatives','sub-' + st.subject.id,'ses-' + st.subject.sesNum,'bet','anat','*' + ref_regexStr + '*') + ' not found')
                    print('/tCannot perform FLIRT... exiting')
                    return

            if progress and refImageFile:
                print('Reference Structural File Found: ' + refImageFile)

        elif stdImageFile:
            refImageFile = stdImageFile

        else:
            print('ERROR: standard reference file not found')
            print('/tCannot perform FLIRT... exiting')
            return
        

        mainBidsLabels = st.bids.get_bids_labels(mainFile)
        secBidsLabels = mainBidsLabels.copy()
        secFiles = glob(os.path.join(DATA_DIR,'derivatives','sub-' + st.subject.id,'ses-' + st.subject.sesNum,'dtifit',mainParams['output_bids_location'],'*.nii.gz'))
        if not secFiles:
            print('WARNING: secondary image files not found in  ' + os.path.join(DATA_DIR,'derivatives','sub-' + st.subject.id,'ses-' + st.subject.sesNum,'dtifit',mainParams['output_bids_location'],'*.nii.gz'))
            print('\tSKIPPING application of transforms to secondary images')
            
        if progress and secFiles:
            print('Secondary Files Found')


        


                # apply brain mask to secondary images? - already dont
                # -------------------------------
        # brainMask = glob(os.path.join(DATA_DIR,'derivatives','sub-' + st.subject.id,'ses-' + st.subject.sesNum,'bet',mainParams['output_bids_location'],'*brain*mask.nii.gz'))
        # if len(brainMask) == 1:
        #     brainMask = brainMask[0]
        # for secFile in secFiles:
        #     secBidsLabels = get_bids_labels(secFile)
        #     secBidsLabels['process'] = mainBidsLabels['process']
        #     secBidsLabels['resolution'] = 'lo'
        #     secBidsLabels['description'] = secBidsLabels + '-brain'
        #     secBidsLabels['extension'] = 'nii.gz'
        #     secFile_brain = os.path.join(os.path.dirname(secFile),get_bids_filename(subject=st.subject.id,session=st.subject.sesNum,**secBidsLabels))
        #     os.system('fslmaths ' + secFile + ' -mas ' + brainmask + ' ' + secFile_brain)

        #     #write corresponding JSON file
        #     d = {}
        #     d['BetProgram'] = betType
        #     d['BetParameters'] = betParams.copy()
        #     d['Sources'] = ['bids:raw:' + secFile.split(DATA_DIR + os.sep)[1],
        #                     'bids:derivatives:' + mainFile_brainmask.split(DATA_DIR + os.sep)[1]]
        #     d['SkullStripped'] = True
        #     d['Type'] = 'Brain'
        #     for k in mainParams['output_json_values'].keys():
        #         d[k] = mainParams['output_json_values'][k]

        #     with open(secFile_brain.split('.')[0] + '.json', 'w') as fp:
        #         json.dump(d, fp, indent=4)   
            
        #     secFile = secFile_brain
        #     outputFileList.append(secFile)


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
                if 'brain' in mainFile:
                    fltBidsLabels['description'] = 'brain'

            else:
                for k in refImageParams['output_bids_labels'].keys():
                    fltBidsLabels[k] = refImageParams['output_bids_labels'][k]
                if 'brain' in mainFile:
                    fltBidsLabels['description'] = 'brain'
            flt.inputs.out_file = os.path.join(mainFlirtOutputDir,st.bids.get_bids_filename(subject=st.subject.id,session=st.subject.sesNum, **fltBidsLabels))
            if refImageParams['type'] == 'std':
                flt.inputs.out_matrix_file = os.path.join(mainFlirtOutputDir,mainParams['out_matrix_base'] + '2' + stdImageParams['out_matrix_suffix'] + '.mat')
            else:
                flt.inputs.out_matrix_file = os.path.join(mainFlirtOutputDir,mainParams['out_matrix_base'] + '2' + refImageParams['out_matrix_base'] + '.mat')


            if os.path.isfile(flt.inputs.out_matrix_file) and not overwrite:
                if progress:
                    print('Skipping FLIRT: registration matrix file found: ' + flt.inputs.out_matrix_file)
                    
            else:
                if progress:
                    print('Performing FLIRT:')
                    print('\tInput File: ' + flt.inputs.in_file)
                    print('\tReference: ' + flt.inputs.reference)
                    print('\tOut File: ' + flt.inputs.out_file)
                    print('\tOut Matrix File: ' + flt.inputs.out_matrix_file)
                flt.run()
                outputFileList.append(flt.inputs.out_file)
                outputFileList.append(flt.inputs.out_matrix_file)
                if progress:
                    print('\tSuccess!')


                # invert registration matrix
                # ----------------------------------
                invt = fsl.ConvertXFM()
                invt.inputs.in_file = flt.inputs.out_matrix_file
                invt.inputs.invert_xfm = True
                if refImageParams['type'] == 'std':
                    invt.inputs.out_file = os.path.join(mainFlirtOutputDir,stdImageParams['out_matrix_suffix'] + '2' + mainParams['out_matrix_base'] + '.mat')
                else:
                    invt.inputs.out_file = os.path.join(mainFlirtOutputDir,refImageParams['out_matrix_base'] + '2' + mainParams['out_matrix_base'] + '.mat')

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


                if not os.path.isfile(invt.inputs.out_file) or overwrite:
                    invt.run() 
                    outputFileList.append(invt.inputs.out_file) 

                
                if refImageParams['type'] == 'std':
                    pngFile = os.path.join(mainFlirtOutputDir,mainParams['out_matrix_base'] + '2' + stdImageParams['out_matrix_suffix'] + '.png')
                else:
                    pngFile = os.path.join(mainFlirtOutputDir,mainParams['out_matrix_base'] + '2' + refImageParams['out_matrix_base'] + '.png')

                if not os.path.isfile(pngFile):
                    st.flirt_pngappend(flt.inputs.out_file,flt.inputs.reference,pngFile)
                    outputFileList.append(os.path.join(mainFlirtOutputDir,pngFile))

            
            # apply registration to secondary image
            # ----------------------------------
            for secFile in secFiles:
                applyxfm = fsl.ApplyXFM()
                applyxfm.inputs.in_file = secFile
                applyxfm.inputs.reference = refImageFile
                applyxfm.inputs.apply_xfm = True
                applyBidsLabels = st.bids.get_bids_labels(secFile)
                applyBidsLabels = refImageParams['output_bids_labels'].copy()
                applyBidsLabels['suffix'] = 'dwi_' + st.bids.get_bids_labels(secFile)['suffix']
                applyxfm.inputs.out_file = os.path.join(mainFlirtOutputDir,st.bids.get_bids_filename(subject=st.subject.id,session=st.subject.sesNum,**applyBidsLabels))
                applyxfm.inputs.in_matrix_file = flt.inputs.out_matrix_file


                if os.path.isfile(applyxfm.inputs.out_file) and not overwrite:
                    if progress:
                        print('Skipping APPLYXFM: output transformed file already exists: ' + applyxfm.inputs.out_file)
                        
                else:
                    if progress:
                        print('Applying transformation to secondary image to produce ' + applyxfm.inputs.out_file)
                    applyxfm.run()
                    outputFileList.append(applyxfm.inputs.out_file)

                    # write JSON sidecar
                    d['Sources'] = [d['Sources'],
                                    'bids:derivatives:' + applyxfm.inputs.in_matrix_file.split(DATA_DIR + os.sep)[1]]
                    with open(applyxfm.inputs.out_file.split('.')[0] + '.json', 'w') as fp:
                        json.dump(d, fp, indent=4)  

            
                    # if refImageParams['type'] == 'std':
                    #     pngFile = os.path.join(mainFlirtOutputDir,secImageParams['out_matrix_base'] + '2' + stdImageParams['out_matrix_suffix'] + '.png')
                    # else:
                    #     pngFile = os.path.join(mainFlirtOutputDir,secImageParams['out_matrix_base'] + '2' + refImageParams['out_matrix_base'] + '.png')

                    # if not os.path.isfile(pngFile):
                    #     flirt_pngappend(flt.inputs.out_file,flt.inputs.reference,pngFile)
                    #     outputFileList.append(os.path.join(mainFlirtOutputDir,pngFile))                                                                                             



            # concatenate reference-to-standard to input-to-reference
            # ----------------------------------
            if not refImageParams['type'] == "std" and stdImageFile:
                strucRegPath = os.path.join(os.path.dirname(mainFlirtOutputDir),'anat')
                strucRegMatrix = os.path.join(strucRegPath,refImageParams['out_matrix_base'] + '2' + stdImageParams['out_matrix_suffix'] + '.mat')
                if not os.path.isfile(strucRegMatrix):
                    print('Warning: cannot find structural registration file ' + strucRegMatrix)
                    print('Skipping matrix concatenation')
                    return

                if progress:
                    print('Structural to standard registration found: ' + strucRegMatrix)

                #find concat input-to-reference with reference-to-standard
                invt = fsl.ConvertXFM()
                invt.inputs.in_file = flt.inputs.out_matrix_file
                invt.inputs.in_file2 = strucRegMatrix
                invt.inputs.concat_xfm = True
                invt.inputs.out_file = os.path.join(mainFlirtOutputDir,mainParams['out_matrix_base'] + '2' + stdImageParams['out_matrix_suffix'] + '.mat')
                if progress:
                    print('Concatenating FLIRT transform with standard transform:')
                    print('\tInput File: ' + invt.inputs.in_file)
                    print('\tInput FIle 2: ' + invt.inputs.in_file2)
                    print('\tOut File: ' + invt.inputs.out_file)


                if not os.path.isfile(invt.inputs.out_file) or overwrite:
                    invt.run()
                    outputFileList.append(invt.inputs.out_file)
                    if progress:
                        print('\tSuccess!')

                #find inverse
                invt = fsl.ConvertXFM()
                invt.inputs.in_file = os.path.join(mainFlirtOutputDir,mainParams['out_matrix_base'] + '2' + stdImageParams['out_matrix_suffix'] + '.mat')
                invt.inputs.invert_xfm = True
                invt.inputs.out_file = os.path.join(mainFlirtOutputDir,stdImageParams['out_matrix_suffix'] + '2' + mainParams['out_matrix_base'] + '.mat')


                if not os.path.isfile(invt.inputs.out_file) or overwrite:
                    invt.run()
                    outputFileList.append(invt.inputs.out_file)


                #apply input-to-standard to input
                applyxfm = fsl.ApplyXFM()
                applyxfm.inputs.in_file = mainFile
                applyxfm.inputs.reference = stdImageFile
                applyxfm.inputs.apply_xfm = True
                applyBidsLabels = mainBidsLabels.copy()
                for k in refImageParams['output_bids_labels'].keys():
                    applyBidsLabels[k] = stdImageParams['output_bids_labels'][k]
                applyxfm.inputs.out_file = os.path.join(mainFlirtOutputDir,st.bids.get_bids_filename(subject=st.subject.id,session=st.subject.sesNum,**applyBidsLabels))
                applyxfm.inputs.in_matrix_file = os.path.join(mainFlirtOutputDir,mainParams['out_matrix_base'] + '2' + stdImageParams['out_matrix_suffix'] + '.mat')


                if os.path.isfile(applyxfm.inputs.out_file) and not overwrite:
                    if progress:
                        print('Skipping APPLYXFM: output transformed file already exists: ' + applyxfm.inputs.out_file)

                else:
                    if progress:
                        print('Applying ' + applyxfm.inputs.in_matrix_file + ' to ' + applyxfm.inputs.in_file)
                        print('\tOut File: ' + applyxfm.inputs.out_file)
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
                    st.flirt_pngappend(applyxfm.inputs.out_file,applyxfm.inputs.reference,os.path.join(mainFlirtOutputDir,os.path.basename(applyxfm.inputs.in_matrix_file).split('.')[0] + '.png'))
                    outputFileList.append(os.path.join(mainFlirtOutputDir,os.path.join(mainFlirtOutputDir,os.path.basename(applyxfm.inputs.in_matrix_file).split('.')[0] + '.png')))


                # (OPTIONAL) Apply to secondary image
                for secFile in secFiles:
                    applyxfm = fsl.ApplyXFM()
                    applyxfm.inputs.in_file = secFile
                    applyxfm.inputs.reference = refImageFile
                    applyxfm.inputs.apply_xfm = True
                    applyBidsLabels = st.bids.get_bids_labels(secFile)
                    applyBidsLabels = stdImageParams['output_bids_labels'].copy()
                    applyBidsLabels['suffix'] = 'dwi_' + st.bids.get_bids_labels(secFile)['suffix']
                    applyxfm.inputs.out_file = os.path.join(mainFlirtOutputDir,st.bids.get_bids_filename(subject=st.subject.id,session=st.subject.sesNum,**applyBidsLabels))
                    applyxfm.inputs.in_matrix_file = flt.inputs.out_matrix_file


                    if os.path.isfile(applyxfm.inputs.out_file) and not overwrite:
                        if progress:
                            print('Skipping APPLYXFM: output transformed file already exists: ' + applyxfm.inputs.out_file)
                            
                    else:
                        if progress:
                            print('Applying transformation to secondary image to produce ' + applyxfm.inputs.out_file)
                        applyxfm.run()
                        outputFileList.append(applyxfm.inputs.out_file)

                        # write JSON sidecar
                        d['Sources'] = [d['Sources'],
                                        'bids:derivatives:' + applyxfm.inputs.in_matrix_file.split(DATA_DIR + os.sep)[1]]
                        with open(applyxfm.inputs.out_file.split('.')[0] + '.json', 'w') as fp:
                            json.dump(d, fp, indent=4) 


            print('\n\nFLIRT (flirt.py, version ' + VERSION + ' ' + DATE + ') has successfully completed for input file: ' + mainFile + '\nThe files that have been produced:')
            print(*outputFileList, sep = "\n\t")

            #remove lingering matrix files left in the current working directory
            for f in glob(os.path.join(os.getcwd(),'sub-' + st.subject.id + '*.mat')):
                os.remove(f)


    except Exception as e:
        print("Error Message: {0}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
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
    dti_flirt(options.IN_FILE,options.DATA_DIR,options.FLIRT_PARAMS,**argsDict)

    


