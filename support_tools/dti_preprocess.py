#!/resshare/wsuconnect/python3_venv/bin/python
# the command above ^^^ sets python 3.10.9 python venv environment

# Created by Matthew Sherwood (matt.sherwood@wright.edu, matthew.sherwood.7.ctr@us.af.mil)
# Created on 23 June 2023
#
# Modified on 
import sys
import os
import argparse
import json
import platform
from nipype.interfaces import fsl
from glob import glob as glob
import datetime
import shutil

#local import
REALPATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
REALPATH = os.path.join('/resshare','general_processing_codes')
sys.path.append(REALPATH)
import support_tools as st


VERSION = '1.0.0'
DATE = '23 June 2023'


parser = argparse.ArgumentParser('dti_preprocess.py: preprocess all DTI rawdata according to the FSL eddy pipeline')
FSLDIR = os.environ["FSLDIR"]

parser.add_argument('IN_FILE',help='Input DTI file')
parser.add_argument('DATA_DIR',help="fullpath to the Project's data directory (see 'dataDir' key in credentials JSON file)")
parser.add_argument('DTI_PARAMS',help='fullpath to the DTI JSON control JSON file')
parser.add_argument('--overwrite',action='store_true',dest='OVERWRITE',default=False,help='overwrite existing output files')
parser.add_argument('--progress',action='store_true',dest='progress',default=False,help='verbose mode')


# ******************* s3 bucket check ********************
def dti_preprocess(IN_FILE: str, DATA_DIR: str, DTI_PARAMS: str, overwrite: bool=False, progress: bool=False):
    """
    This function performs FSL-based DTI preprocessing according to the FDT DTI pipeline (https://open.win.ox.ac.uk/pages/fslcourse/practicals/fdt1/index.html) prior to FLIRT/FNIRT and TBSS. 

    dti_preprocess(IN_FILE,DATA_DIR,FLIRT_PARAMS,overwrite=False,progress=False)

    :param IN_FILE: fullpath to a DTI rawdata NIfTI file
    :type IN_FILE: str

    :param DATA_DIR: fullpath to the project's data directory (project's 'dataDir' credential)
    :type DATA_DIR: str

    :param DTI_PARAMS: fullpath to project's 2D ASL FLIRT parameter file
    :type DTI_PARAMS: str

    :param overwrite: flag to overwrite existing files, defaults to False
    :type overwrite: bool, optional

    :param progress: flag to display command line output providing additional details on the processing status, defaults to False
    :type progress: bool, optional

    :raises FileNotFoundError: FLIRT_PARAMS file not found on disk

    :raises Exception: general error encountered during execution
    """
    

    try:
        now = datetime.datetime.now()

        if progress:
            print('\n\ndti_preprocess.py version ' + VERSION + ' dated ' + DATE + '\n')
            print('running @ ' + now.strftime("%m-%d-%Y %H:%M:%S") + '\n')
            print('Reading JSON Files')

        try:
            with open(DTI_PARAMS) as j:
                dtiFullParams = json.load(j)

                # Organize parameter inputs
                #additional processing options

                #get main image parameters
                if 'main_image_params' in dtiFullParams:
                    mainParams = dtiFullParams.pop('main_image_params')
                    
                #get main eddy parameters
                if 'eddy_params' in dtiFullParams:
                    eddyParams = dtiFullParams.pop('eddy_params')
                    
                #get main eddy parameters
                if 'dtifit_params' in dtiFullParams:
                    dtifitParams = dtiFullParams.pop('dtifit_params')

        except FileNotFoundError as e:
            print("Error Message: {0}".format(e))
            return


        #check if file exists on local disk
        mainFile = IN_FILE
        if progress:
            print('Main Image: ' + mainFile)
        if not os.path.isfile(mainFile):
            if progress:
                print('\tERROR: Main Image File Not Found. Skipping')
            return
        elif progress:
            print('\tMain Image File Found: ' + mainFile)
        
        # create file inputs and outputs
        mainFileDir = os.path.dirname(mainFile)
        subName, fullSesNum, sesNum = st.get_dir_identifiers_new(mainFileDir)
        mainBetOutputDir = os.path.join(DATA_DIR,'derivatives','sub-' + subName,'ses-' + sesNum,'bet',mainParams['output_bids_location'])#create base path and filename for move
        mainTopupOutputDir = os.path.join(DATA_DIR,'derivatives','sub-' + subName,'ses-' + sesNum,'topup',mainParams['output_bids_location'])#create base path and filename for move
        mainEddyOutputDir = os.path.join(DATA_DIR,'derivatives','sub-' + subName,'ses-' + sesNum,'eddy',mainParams['output_bids_location'])#create base path and filename for move
        mainDtifitOutputDir = os.path.join(DATA_DIR,'derivatives','sub-' + subName,'ses-' + sesNum,'dtifit',mainParams['output_bids_location'])#create base path and filename for move

        #make output directory structure if it does not exist
        if not os.path.isdir(mainBetOutputDir):
            os.makedirs(mainBetOutputDir)
        # os.chdir(mainBetOutputDir)

        #start with topup
        if not os.path.isdir(mainTopupOutputDir):
            os.makedirs(mainTopupOutputDir)
        os.chdir(mainTopupOutputDir)

        if not os.path.isdir(mainEddyOutputDir):
            os.makedirs(mainEddyOutputDir)

        if not os.path.isdir(mainDtifitOutputDir):
            os.makedirs(mainDtifitOutputDir)


        mainBidsLabels = st.bids_commands.get_bids_labels(mainFile)
        outputFileList = []

        #********************************************************
        # STEP 1: FSLROI - extract first B0 image from Main Image
        #********************************************************
        vols = 0
        roi_mainBidsLabels = mainBidsLabels.copy()
        roi_mainBidsLabels['process'] = 'fslroi'
        roi_mainBidsLabels['description'] = 'vol-' + str(vols)
        outMainVolFile = os.path.join(mainTopupOutputDir,st.bids.get_bids_filename(subject=subName,session=sesNum,**roi_mainBidsLabels))
        nodifFile = outMainVolFile

        if os.path.isfile(outMainVolFile) and not overwrite:
            if progress:
                print('WARNING: FSLROI - Single volume file already exists: ' + outMainVolFile)

        else:
            if progress:
                print('FSLROI: Creating single volume file from volume #' + str(vols) + ' as ' + outMainVolFile)
            fslroi = fsl.ExtractROI(in_file=mainFile,roi_file=outMainVolFile,t_min=vols,t_size=1)
            print(fslroi.cmdline)
            fslroi.run()
            outputFileList.append(fslroi.inputs.roi_file)

            #write JSON sidecar file
            d = {}
            d['Sources'] = ['bids:raw:' + fslroi.inputs.in_file.split(DATA_DIR + os.sep)[1]]
            d['FslRoiParameters'] = {'t_min': vols, 't_size': 1}
            d['SkullStripped'] = 'false'
            # for k in mainParams['output_json_values'].keys():
            #     d[k] = mainParams['output_json_values'][k]
            with open(fslroi.inputs.roi_file.split('.')[0] + '.json', 'w') as fp:
                json.dump(d, fp, indent=4) 
                
        


        #********************************************************
        # STEP 2: FSLMERGE - merge first B0 Image (A->P) with sbref image (P->A)
        #********************************************************
        #find sbref
        sbrefFile = glob(os.path.join(mainFileDir,'*sbref.nii.gz'))
        if len(sbrefFile) == 1:
            sbrefFile = sbrefFile[0]
            if progress:
                print('SBREF Image File Found: ' + sbrefFile)
                print('\tContinue processing...')
        else:
            print('WARNING: sbref image ' + os.path.join(os.path.dirname(mainFileDir),'*sbref.nii.gz') + ' not found... skipping')
            return
                
        merge_mainBidsLabels = mainBidsLabels.copy()
        merge_mainBidsLabels['process'] = 'fslmerge'
        merge_mainBidsLabels['description'] = 'AP-PA'
        outMergeFile = os.path.join(mainTopupOutputDir,st.bids.get_bids_filename(subject=subName,session=sesNum,**merge_mainBidsLabels))


        if os.path.isfile(outMergeFile) and not overwrite:
            if progress:
                print('WARNING: FSLMERGE - Single volume file already exists: ' + outMergeFile)

        else:
            if progress:
                print('FSLMERGE: Creating temporal merge of ' + nodifFile + ' and ' + sbrefFile)
            os.system('fslmerge -t ' + outMergeFile + ' ' + nodifFile + ' ' + sbrefFile)
            outputFileList.append(outMergeFile)

            #write JSON sidecar file
            d = {}
            d['Sources'] = ['bids:derivatives:' + nodifFile.split(DATA_DIR + os.sep)[1],
                            'bids:raw:' + sbrefFile.split(DATA_DIR + os.sep)[1]]
            d['SkullStripped'] = 'false'
            # for k in mainParams['output_json_values'].keys():
            #     d[k] = mainParams['output_json_values'][k]
            with open(outMergeFile.split('.')[0] + '.json', 'w') as fp:
                json.dump(d, fp, indent=4) 

        
        #********************************************************
        # STEP 3: FSL TOPUP - bias field correction
        #********************************************************
        # formulate output
        tu_corr_mainBidsLabels = mainBidsLabels.copy()
        tu_corr_mainBidsLabels['process'] = 'topup'
        tu_corr_mainBidsLabels['description'] = 'iout'
        tu_corr_mainBidsLabels['extension'] = None
        outCorrFile = os.path.join(mainTopupOutputDir,st.bids.get_bids_filename(subject=subName,session=sesNum,**tu_corr_mainBidsLabels))
        tu_base_mainBidsLabels = mainBidsLabels.copy()
        tu_base_mainBidsLabels['process'] = 'topup'
        tu_base_mainBidsLabels['description'] = 'B1'
        tu_base_mainBidsLabels['extension'] = None
        outBaseFile = os.path.join(mainTopupOutputDir,st.bids.get_bids_filename(subject=subName,session=sesNum,**tu_base_mainBidsLabels))
        tu_field_mainBidsLabels = mainBidsLabels.copy()
        tu_field_mainBidsLabels['process'] = 'topup'
        tu_field_mainBidsLabels['description'] = 'fout'
        tu_field_mainBidsLabels['extension'] = None
        outFieldFile = os.path.join(mainTopupOutputDir,st.bids.get_bids_filename(subject=subName,session=sesNum,**tu_field_mainBidsLabels))

        # create topup object
        #first copy acqp input to local eddy output directory
        shutil.copyfile(eddyParams['acqp'],os.path.join(mainEddyOutputDir,os.path.basename(eddyParams['acqp'])))
        eddyParams['acqp'] = os.path.join(mainEddyOutputDir,os.path.basename(eddyParams['acqp']))
        topup = fsl.TOPUP(in_file=outMergeFile,config=dtiFullParams['topup_config'],encoding_file=eddyParams['acqp'],out_base=outBaseFile,out_corrected=outCorrFile,out_field=outFieldFile,out_logfile=os.path.join(mainTopupOutputDir,'topup.log'))

        # has it already been ran?
        if os.path.isfile(outFieldFile + '.nii.gz') and not overwrite:
            if progress:
                print('WARNING: TOPUP - topup outputs exist')

        else: #run topup and produce JSON sidecar
            if progress:
                print('FSLTOPUP: Running Topup on  ' + outMergeFile)
            topup.run()

            #write JSON sidecar file
            d = {}
            d['Sources'] = ['bids:derivatives:' + outMergeFile.split(DATA_DIR + os.sep)[1],
                            'bids:derivatives:' + eddyParams['acqp'].split(DATA_DIR + os.sep)[1]]
            d['SpatialReference'] = 'orig'
            d['SkullStripped'] = 'false'
            # for k in mainParams['output_json_values'].keys():
            #     d[k] = mainParams['output_json_values'][k]
            with open(outCorrFile.split('.')[0] + '.json', 'w') as fp:
                json.dump(d, fp, indent=4) 


        #********************************************************
        # STEP 4: FSL BET - extract brain/produce brain mask
        #********************************************************
        #average topup iout
        tmean_mainBidsLabels = mainBidsLabels.copy()
        tmean_mainBidsLabels['process'] = 'topup'
        tmean_mainBidsLabels['description'] = 'iout-tmean'
        tmean_mainBidsLabels['extension'] = None
        outTmeanFile = os.path.join(mainTopupOutputDir,st.bids.get_bids_filename(subject=subName,session=sesNum,**tmean_mainBidsLabels))

        # has fslmaths already been ran?
        if os.path.isfile(outTmeanFile + '.nii.gz') and not overwrite:
            if progress:
                print('WARNING: FSLMATHS - ' + outTmeanFile + '.nii.gz already exist, skipping for now')

        else: #run topup and produce JSON sidecar
            if progress:     
                print('FSLMATHS: Running fslmaths to average 4th dimension of ' + outCorrFile + '.nii.gz')
            os.system('fslmaths ' + outCorrFile + '.nii.gz' + ' -Tmean ' + outTmeanFile)

            #write JSON sidecar file
            d = {}
            d['Sources'] = ['bids:derivatives:' + outCorrFile.split(DATA_DIR + os.sep)[1] + '.nii.gz']
            d['SpatialReference'] = 'orig'
            d['SkullStripped'] = 'false'
            # for k in mainParams['output_json_values'].keys():
            #     d[k] = mainParams['output_json_values'][k]
            with open(outTmeanFile.split('.')[0] + '.json', 'w') as fp:
                json.dump(d, fp, indent=4) 

        #extract brain
        os.chdir(mainBetOutputDir)
        tmean_brain_mainBidsLabels = mainBidsLabels.copy()
        tmean_brain_mainBidsLabels['process'] = 'fslbet'
        tmean_brain_mainBidsLabels['description'] = 'iout-tmean-brain'
        tmean_brain_mainBidsLabels['extension'] = None
        outTmeanBrainFile = os.path.join(mainBetOutputDir,st.bids_commands.get_bids_filename(subject=subName,session=sesNum,**tmean_brain_mainBidsLabels))    

        # has bet already been ran?
        if os.path.isfile(outTmeanBrainFile + '.nii.gz') and not overwrite:
            if progress:
                print('WARNING: FSL BET - ' + outTmeanBrainFile + '.nii.gz already exist, skipping for now')

        else: #run topup and produce JSON sidecar
            if progress:     
                print('FSLBET: Running fsl bet on ' + outTmeanFile + '.nii.gz')   
            os.system('bet ' + outTmeanFile + '.nii.gz' + ' ' + outTmeanBrainFile + '.nii.gz -m -f 0.3')

            #write JSON sidecar file
            d = {}
            d['Sources'] = ['bids:derivatives:' + outTmeanFile.split(DATA_DIR + os.sep)[1] + '.nii.gz']
            d['SpatialReference'] = 'orig'
            d['SkullStripped'] = 'true'
            # for k in mainParams['output_json_values'].keys():
            #     d[k] = mainParams['output_json_values'][k]
            with open(outTmeanBrainFile.split('.')[0] + '.json', 'w') as fp:
                json.dump(d, fp, indent=4) 



        #********************************************************
        # STEP 5: FSL EDDY - Perform eddy current correction
        #********************************************************
        # Formulate output
        os.chdir(mainEddyOutputDir)
        eddy_mainBidsLabels = mainBidsLabels.copy()
        eddy_mainBidsLabels['process'] = 'eddy-gpu'
        eddy_mainBidsLabels['description'] = 'unwarped'
        eddy_mainBidsLabels['extension'] = None
        outEddyFile = os.path.join(mainEddyOutputDir,st.bids_commands.get_bids_filename(subject=subName,session=sesNum,**eddy_mainBidsLabels)) 
        
        # produce base eddy command-line argument
        if dtiFullParams['type'] == 'gpu':
            # eddyCmd = 'ssh msherwood@10.11.0.31 -t \'bash -l -c "eddy_cuda'
            eddyCmd = 'eddy_cuda'
        else:
            eddyCmd = 'eddy'
        eddyCmd = eddyCmd + ' --imain=' + mainFile + ' --mask=' + outTmeanBrainFile + '_mask.nii.gz' + ' --bvecs=' + mainFile.replace('.nii.gz','.bvec') + ' --bvals=' + mainFile.replace('.nii.gz','.bval') + ' --out=' + outEddyFile + ' --topup=' + topup.inputs.out_base
        
        #add options specified in JSON control file
        eddyKeys = ['acqp', 'index', 'mb', 'mb_offs', 'slspec', 'json', 'mporder', 's2vlambda', 'flm', 'slm', 'fwhm', 'niter', 's2v_niter', 'interp', 's2v_interp', 'resamp', 'nvoxhp', 'initrand', 'ff', 'ol_nstd', 'ol_nvox', 'ol_type', 'mbs_niter', 'mbs_lambda', 'mbs_ksp']
        eddyFlags = ['cnr_maps', 'residuals', 'fep', 'repol', 'os_pos', 'ol_sqr', 'estimate_move_by_susceptibility','dont_sep_offs_move', 'dont_peas', 'data_is_shelled', 'verbose']
        
        #loop through specified keys in JSON control file
        tmpEddyList = []
        for k in eddyParams.keys():
            if k in eddyKeys:
                if type(eddyParams[k]) is int:
                    eddyCmd = eddyCmd + ' --' + k + '=' + str(eddyParams[k])
                else:
                    if k in ['index','slspec']:
                        shutil.copyfile(eddyParams[k],os.path.join(mainEddyOutputDir,os.path.basename(eddyParams[k])))
                        eddyParams[k] = os.path.join(mainEddyOutputDir,os.path.basename(eddyParams[k]))
                        tmpEddyList = tmpEddyList + ['bids:derivatives:' + eddyParams[k].split(DATA_DIR + os.sep)[1]]
                    eddyCmd = eddyCmd + ' --' + k + '=' + eddyParams[k]
            elif k in eddyFlags:
                if eddyParams[k]:
                    eddyCmd = eddyCmd + ' --' + k

        
        # if dtiFullParams['type'] == 'gpu':
        #     eddyCmd = eddyCmd + '"\''

        
        # produce base eddy_quad (individual qc) command-line argument
        eddyQuadCmd = 'eddy_quad ' + outEddyFile 
        eddyQuadKeys = ['eddyIdx', 'eddyParams']
        eddyQuadKeyMaps = ['index', 'acqp']
        c = 0
        for k in eddyQuadKeyMaps:
            if k in eddyParams.keys():
                eddyQuadCmd = eddyQuadCmd + ' --' + eddyQuadKeys[c] + ' ' + eddyParams[k]
            c = c + 1

        eddyQuadCmd = eddyQuadCmd + ' --mask ' + outTmeanBrainFile + '_mask.nii.gz' + ' --bvals ' + mainFile.replace('.nii.gz','.bval') + ' --bvecs ' + mainFile.replace('.nii.gz','.bvec') + ' --output-dir ' + outEddyFile + '.qc'
        if 'slspec'  in eddyParams.keys():
            eddyQuadCmd = eddyQuadCmd + ' --slspec ' + eddyParams['slspec']
        eddyQuadCmd = eddyQuadCmd + ' --verbose'
                

        # run EDDY and EDDY QC  *****NEED TO ADD FILE CHECKING AND JSON SIDECARS
        # has eddy already been ran?
        if os.path.isfile(outEddyFile + '.nii.gz') and not overwrite:
            if progress:
                print('WARNING: EDDY - eddy outputs exist, skipping for now')

        else: #run topup and produce JSON sidecar
            if progress:
                print('FSL EDDY: Running Eddy on  ' + mainFile)


            # # print(eddyCmd)
            # if dtiFullParams['type'] == 'gpu':
            #     if not os.path.isdir(os.path.dirname(mainTopupOutputDir).replace('resshare','connect-npc-gpu')):
            #         os.makedirs(os.path.dirname(mainTopupOutputDir).replace('resshare','connect-npc-gpu'))
            #     # print('rsync -r -e "ssh" --progress ' + mainTopupOutputDir + ' msherwood@connect-npc-gpu:' + os.path.dirname(mainTopupOutputDir))
            #     os.system('cp -RL ' + mainTopupOutputDir + ' ' + os.path.dirname(mainTopupOutputDir).replace('resshare','connect-npc-gpu'))
            #     if not os.path.isdir(os.path.dirname(mainBetOutputDir).replace('resshare','connect-npc-gpu')):
            #         os.makedirs(os.path.dirname(mainBetOutputDir).replace('resshare','connect-npc-gpu'))
            #     os.system('cp -RL ' + mainBetOutputDir + ' ' + os.path.dirname(mainBetOutputDir).replace('resshare','connect-npc-gpu'))
            #     if not os.path.isdir(os.path.dirname(mainEddyOutputDir).replace('resshare','connect-npc-gpu')):
            #         os.makedirs(os.path.dirname(mainEddyOutputDir).replace('resshare','connect-npc-gpu'))

            os.system(eddyCmd)

            # if dtiFullParams['type'] == 'gpu':
            #     if not os.path.isdir(os.path.dirname(mainEddyOutputDir)):
            #         os.makedirs(os.path.dirname(mainEddyOutputDir))
            #     os.system('cp -RL ' + mainEddyOutputDir + ' ' + os.path.dirname(mainEddyOutputDir).replace('resshare','connect-npc-gpu'))

            #write JSON sidecar file
            d = {}
            d['Sources'] = ['bids:raw:' + mainFile.split(DATA_DIR + os.sep)[1],
                            'bids:raw:' + mainFile.split(DATA_DIR + os.sep)[1].replace('.nii.gz','.bvec'),
                            'bids:raw:' + mainFile.split(DATA_DIR + os.sep)[1].replace('.nii.gz','.bval'),
                            'bids:derivatives:' + outTmeanBrainFile.split(DATA_DIR + os.sep)[1] + '_mask.nii.gz',
                            'bids:derivatives:' + eddyParams['acqp'].split(DATA_DIR + os.sep)[1]] + tmpEddyList
            d['SpatialReference'] = 'orig'
            d['SkullStripped'] = 'true'
            # for k in mainParams['output_json_values'].keys():
            #     d[k] = mainParams['output_json_values'][k]
            with open(outEddyFile.split('.')[0] + '.json', 'w') as fp:
                json.dump(d, fp, indent=4) 

        # has eddy_quad already been ran?
        if os.path.isdir(outEddyFile + '.qc') and not overwrite:
            if progress:
                print('WARNING: EDDY QUAD - eddy outputs exist, skipping for now')

        else: #run topup and produce JSON sidecar
            if progress:
                print('FSL EDDY_QUAD: Running eddy_quad on  ' + mainFile)
            print(eddyQuadCmd)
            os.system(eddyQuadCmd)
        


        #********************************************************
        # STEP 5: FSL DTIFIT - produce FA/MD/other DTI outputs
        #********************************************************
        #formulate output
        os.chdir(mainDtifitOutputDir)
        dtifit_mainBidsLabels = mainBidsLabels.copy()
        dtifit_mainBidsLabels['process'] = 'dtifit'
        eddy_mainBidsLabels['description'] = 'dti'
        dtifit_mainBidsLabels['extension'] = None
        outDtifitFile = os.path.join(mainDtifitOutputDir,st.bids.get_bids_filename(subject=subName,session=sesNum,**dtifit_mainBidsLabels)) 

        #create dtifit object
        dtifit = fsl.DTIFit(dwi=outEddyFile + '.nii.gz',
                            bvecs=mainFile.replace('.nii.gz','.bvec'),
                            bvals=mainFile.replace('.nii.gz','.bval'),
                            mask=outTmeanBrainFile + '_mask.nii.gz',
                            base_name=outDtifitFile)
        
        # run dtifit    ******NEED TO ADD FILE CHECKING AND JSON SIDECARS
        # has eddy_quad already been ran?
        if os.path.isfile(outDtifitFile + '_FA.nii.gz') and not overwrite:
            if progress:
                print('WARNING: DTIFIT - dtifit outputs exist, skipping for now')

        else: #run topup and produce JSON sidecar
            if progress:
                print('FSL DTIFIT: Running dtifit on  ' + outEddyFile)
            dtifit.run()

            # for k in ['FA','L1','L2','L3','MD','MO','S0','V1','V2','V3']:
            for dtiOutFile in glob(os.path.join(mainDtifitOutputDir,'*.nii.gz')):
                d = {}
                d['Sources'] = ['bids:derivatives:' + outEddyFile.split(DATA_DIR + os.sep)[1] + '.nii.gz',
                                'bids:raw:' + mainFile.split(DATA_DIR + os.sep)[1].replace('.nii.gz','.bvec'),
                                'bids:raw:' + mainFile.split(DATA_DIR + os.sep)[1].replace('.nii.gz','.bval')]
                d['SpatialReference'] = 'orig'
                d['SkullStripped'] = 'true'
                # for k in mainParams['output_json_values'].keys():
                #     d[k] = mainParams['output_json_values'][k]
                with open(dtiOutFile.split('.')[0] + '.json', 'w') as fp:
                    json.dump(d, fp, indent=4) 

                #also produce a file with outputs * 1000
                os.system('fslmaths ' + dtiOutFile + ' -mul 1000 ' + dtiOutFile.split('.')[0] + '-1000.nii.gz')




        #********************************************************
        # STEP 6: RSYNC - if running gpu-based eddy, synchronize output back to master/central storage
        #********************************************************
        # if dtiFullParams['type'] == 'gpu':
        #     os.system('rsync -r -e "ssh" --progress /resshare/projects/2022_KBR_Cog_Neuro_2/measurement_statbility/derivatives/sub-101/ses-20230612-1 nw028mss@10.11.0.40:/resshare/projects/2022_KBR_Cog_Neuro_2/measurement_statbility/derivatives/sub-101')


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

    print('1')
    options = parser.parse_args()
    print('2')
    argsDict = {}
    if options.OVERWRITE:
        argsDict['overwrite'] = options.OVERWRITE
    if options.progress:
        argsDict['progress'] = options.progress
    dti_preprocess(options.IN_FILE,options.DATA_DIR,options.DTI_PARAMS,**argsDict)



    


