#!/resshare/general_processing_codes/python3_venv/bin/python
# the command above ^^^ sets python 3.11.11 as the interpreter for this program

# Created by Matthew Sherwood (matt.sherwood@wright.edu, matthew.sherwood.7.ctr@us.af.mil)
# Created on 22 FEB 2024
#
# Modified on

import os
import argparse
from pycondor import Job, Dagman
import datetime
import sys
from glob import glob as glob

#local import

REALPATH = os.path.realpath(__file__)
sys.path.append(os.path.dirname(REALPATH))
from helper_functions.bids_commands import *
from helper_functions.get_dir_identifiers import *
from helper_functions.read_credentials import *
from helper_functions.mysql_commands import *
from helper_functions.create_bin_condor_job import *
from helper_functions.create_fsl_condor_job import *
from helper_functions.create_python_condor_job import *
from helper_functions.id_check import id_check
from helper_functions.feat_full_firstlevel import *

from classes.creds import *


# GLOBAL INFO
#versioning
VERSION = '1.0.1'
DATE = '22 Feb 2024'
FSLDIR = os.environ["FSLDIR"]

#input argument parser
parser = argparse.ArgumentParser()

# ******************* PARSE COMMAND LINE ARGUMENTS ********************
def parse_arguments():

    #input options for main()
    requiredNamed = parser.add_argument_group('required arguments')
    requiredNamed.add_argument('-p','--project', action="store", dest="PROJECT", help="Perform full firstlevel FEAT for the selected project: " + ' '.join(creds.projects), default=None)

    parser.add_argument('--overwrite', action="store_true", dest="OVERWRITE", help="Force conversion by skipping directory and database checking", default=False)
    parser.add_argument('-s', '--submit', action="store_true", dest="SUBMIT", help="Submit conversion to condor for parallel conversion", default=False)
    parser.add_argument('--skip-id-check', action="store_true", dest="SKIPIDCHECK", help="Skip subject id checking in participants.tsv file", default=False)
    parser.add_argument('-v', '--version', action="store_true", dest="version", help="Display the current version")
    parser.add_argument('--progress', action="store_true", dest="progress", help="Show progress (default FALSE)", default=False)
    options = parser.parse_args()

    #determine the search table and search string
    if not options.PROJECT in creds.projects:
        if not options.version:
            print("ERROR: user must define a project using [-p|--project <project>]\n\n")
            parser.print_help()
        sys.exit()
        
    return options



# ******************* Setup Main Processing ********************
def modality_process(options,*args,**kwargs):
    submit = kwargs.get('submit',None)
    error = kwargs.get('error',None)
    output = kwargs.get('output',None)
    log = kwargs.get('log',None)
    dagman = kwargs.get('dagman',None)

    #load parameter JSON control file
    try:
        dtiInputFile = os.path.join(creds.dataDir,'code',options.PROJECT + '_feat_full_firstlevel_input.json')
        if not os.path.isfile(os.path.join(creds.dataDir,'code',options.PROJECT + '_feat_full_firstlevel_input.json')):
            return

        with open(dtiInputFile) as j:
            featInput = json.load(j)

        #asl sql_query inputs
        incExcDict = {}
        if 'inclusion_list' in featInput:
            incExcDict['inclusion'] = featInput.pop('inclusion_list')
        if 'exclusion_list' in featInput:
            incExcDict['exclusion'] = featInput.pop('exclusion_list')

        #(optional) get structural image parameters
        if 'reference_image_params' in featInput:
            refImageParams = featInput.pop('reference_image_params')
            refImage = True

    except FileNotFoundError as e:
        print("Error Message: {0}".format(e))
        sys.exit()

    regexStr = featInput['bold_regexstr']

    if not incExcDict:
        filesToProcess = sql_query(database=creds.database,searchtable=creds.searchTable,searchcol='fullpath',regex=regexStr,progress=False)
    else:
        filesToProcess = sql_query(database=creds.database,searchtable=creds.searchTable,searchcol='fullpath',regex=regexStr,**incExcDict,progress=False)



    # loop throught files
    filesToProcess.sort()
    featFlag = False
    job_flag = True
    featFlag = False
    job2_flag = True
    threadCount = 0
    for f in filesToProcess:
        if options.progress:
            print('Evaluating input BOLD file: ' + f)

        #get subject name and see if they should be discarded
        subName, sesNum = get_dir_identifiers(os.path.dirname(f))
        if options.progress:
            print('\tSUBJECT: ' + subName + ' SESSION: ' + sesNum)
        if not id_check(subName) and not options.SKIPIDCHECK:
            print('WAARNING: subject excluded from analysis. To perform the analysis run with the skip ID check option.')
            continue

        boldInputLabels = get_bids_labels(f)
        if not 'task' in boldInputLabels.keys():
            continue
        elif boldInputLabels['task'] in featInput.keys():
            boldTask = boldInputLabels['task']
        else:
            continue


        # make output directory in derivatives
        featOutputDir = os.path.join(creds.dataDir,'derivatives','sub-' + subName,'ses-' + sesNum,'feat','func',os.path.basename(f).split('.')[0] + '.feat')
        featDesignDir = os.path.join(creds.dataDir,'derivatives','sub-' + subName,'ses-' + sesNum,'feat','func',os.path.basename(f).split('.')[0] + '.design')
        # if not os.path.isdir(featOutputDir):
        #     os.makedirs(featOutputDir)
        if os.path.isdir(featOutputDir):
            #check for processed output
            outFile = glob(os.path.join(featOutputDir, '*zstat*.nii.gz'))
            if len(outFile) >= 1 and not options.OVERWRITE:
                continue
            elif len(outFile) >= 1: #output exists, overwrite specified
                os.system('rm -rf ' + featOutputDir)

        #copy design files
        if not os.path.isdir(featDesignDir):
            os.makedirs(featDesignDir)
        os.system('cp -RL ' + os.path.join(creds.dataDir, 'code' ,'bold_designs', 'task-' + boldTask, featInput[boldTask]['design_basename'] + '*') + ' ' + featDesignDir)

        if 'step2_design_basename' in featInput[boldTask].keys():
            os.system('cp -RL ' + os.path.join(creds.dataDir, 'code' ,'bold_designs', 'task-' + boldTask, featInput[boldTask]['step2_design_basename'] + '*') + ' ' + featDesignDir)


        #look for accompanying structural data on disk in derivatives
        if refImage and 'highres_files' in featInput[boldTask]['line_pairs'].keys():
            ref_regexStr = get_bids_filename(**refImageParams['input_bids_labels'])
            mainFileDir = os.path.dirname(f)
            mainBetOutputDir = os.path.join(creds.dataDir,'derivatives','sub-' + subName,'ses-' + sesNum,'bet',refImageParams['input_bids_type'])#create base path and filename for move

            if refImageParams['input_bids_location'] == 'rawdata':
                refImageFile = glob(os.path.join(os.path.dirname(mainFileDir),refImageParams['input_bids_type'],'*' + ref_regexStr.split('_')[1] + '*'))
            elif refImageParams['input_bids_location'] == 'derivatives':
                refImageFile = glob(os.path.join(mainBetOutputDir,'*' + ref_regexStr.split('_')[1] + '*'))
            else:
                print('ERROR: structural file "bids_location" not supported. This should be "rawdata" or "derivatives"')
                print('\tCannot perform FEAT as specified... continuing to next file')
                continue

            for item in ref_regexStr.split('_')[2:]:
                refImageFile = [x for x in refImageFile if item in x]

            if 'exclusion_list' in refImageParams.keys():
                for item in refImageParams['exclusion_list']:
                    refImageFile = [x for x in refImageFile if not item in x]
            
            if len(refImageFile) > 0:
                refImageFile = refImageFile[0]
                if options.progress:
                    print('\tFound associated reference image: ' + refImageFile)
            elif refImageParams['input_bids_location'] == 'rawdata':
                print('ERROR: structural file ' + os.path.join(os.path.dirname(mainFileDir),'anat','*' + ref_regexStr + '*') + ' not found')
                print('\tCannot perform FEAT... skipping')
                continue
            elif refImageParams['input_bids_location'] == 'derivatives':
                print('ERROR: structural file ' + os.path.join(os.path.dirname(mainBetOutputDir),'*' + ref_regexStr + '*') + ' not found')
                print('\tCannot perform FEAT... skipping"')
                continue

       
        
        #modify design file
        try:
            with open(os.path.join(featDesignDir,featInput[boldTask]['design_basename'] + '.fsf'),'r',encoding='utf-8') as file:
                designData = file.readlines()

        except FileNotFoundError as e:
            print("Error Message: {0}".format(e))
            continue

        # Refine FEAT Design file
        for k in featInput[boldTask]['line_pairs'].keys():
            if 'outputdir' in k:
                designData[featInput[boldTask]['line_pairs'][k]-1] = 'set fmri(outputdir) "' + featOutputDir + '"\n'
            elif 'feat_files' in k:
                designData[featInput[boldTask]['line_pairs'][k]-1] = 'set feat_files(1) "' + f + '"\n'
            elif 'highres_files' in k:
                designData[featInput[boldTask]['line_pairs'][k]-1] = 'set highres_files(1) "' + refImageFile + '"\n'
            # elif 'init_standard' in k and 'out_matrix_base' in refImageParams.keys():
            #     strucRegDir = os.path.join(creds.dataDir,'derivatives','sub-' + subName,'ses-' + sesNum,'flirt',refImageParams['input_bids_type'])
            #     strucRegMatrix = os.path.join(strucRegDir,refImageParams['out_matrix_base']  + '.mat')
            #     if not os.path.isfile(strucRegMatrix):
            #         print('Warning: cannot find structural registration file ' + strucRegMatrix)
            #         print('\tSkipping matrix concatenation')
            #     else:
            #         if options.progress:
            #             print('\tStructural to standard registration found: ' + strucRegMatrix)
            #         designData[featInput[boldTask]['line_pairs'][k]-1] = 'set fmri(init_standard) "' + strucRegMatrix + '"\n'
            else:
                print('WARNING: support for line_pair option ' + k + ' is not available')
                print('\tskipping this request and proceeding. Contact Matthew Sherwood')

        with open(os.path.join(featDesignDir,featInput[boldTask]['design_basename'] + '.fsf'), 'w', encoding='utf-8') as file:
            file.writelines(designData)


        #Refine FEAT step 2 design file 
        if 'step2_line_pairs' in featInput[boldTask].keys():
            #modify design file
            try:
                with open(os.path.join(featDesignDir,featInput[boldTask]['step2_design_basename'] + '.fsf'),'r',encoding='utf-8') as file:
                    designData = file.readlines()

            except FileNotFoundError as e:
                print("Error Message: {0}".format(e))
                continue     

            skipFlag = False
            for k in featInput[boldTask]['step2_line_pairs'].keys():
                if 'analysis' in k:
                    designData[featInput[boldTask]['step2_line_pairs'][k]-1] = 'set fmri(analysis)) 2\n'
                elif 'inputtype' in k:
                    designData[featInput[boldTask]['step2_line_pairs'][k]-1] = 'set fmri(inputtype) 1\n'
                elif 'prestats' in k:
                    designData[featInput[boldTask]['step2_line_pairs'][k]-1] = 'set fmri(filtering_yn) 0\n'
                elif 'poststats' in k:
                    designData[featInput[boldTask]['step2_line_pairs'][k]-1] = 'set fmri(poststats_yn) 0\n'
                elif 'outputdir' in k:
                    designData[featInput[boldTask]['step2_line_pairs'][k]-1] = 'set fmri(outputdir) "' + featOutputDir + '"\n'
                elif 'feat_files' in k:
                    designData[featInput[boldTask]['step2_line_pairs'][k]-1] = 'set feat_files(1) "' + featOutputDir + '"\n'
                elif 'custom' in k:
                    ls_customFiles = []
                    if featInput[boldTask][k]['input_bids_location'] == 'rawdata':
                        ls_customFiles = glob(os.path.join(os.path.dirname(mainFileDir),featInput[boldTask][k]['input_bids_type'],'*' + featInput[boldTask][k]['regex'] + '*'))
                    elif refImageParams['input_bids_location'] == 'derivatives':
                        ls_customFiles = glob(os.path.join(mainFileDir.replace('rawdata','derivatives'),featInput[boldTask][k]['input_bids_type'],'*' + featInput[boldTask][k]['regex'] + '*'))
                    else:
                        print('ERROR: ' + k + ' "bids_location" not supported. This should be "rawdata" or "derivatives"')
                        print('\tCannot perform FEAT as specified... continuing to next file')
                        skipFlag = True
                        continue
                    
                    if not ls_customFiles:
                        print('ERROR: could not find any files specified by ' + k + ' regex')
                        print('\tCannot perform FEAT as specified... continuing to next file')
                        skipFlag = True
                        continue

                    if 'run' in f:
                        s_run = [x for x in f.split('_') if 'run' in x][0]
                        ls_customFiles =[x for x in ls_customFiles if s_run in x]
                    if 'inclusion_list' in featInput[boldTask][k].keys():
                        for item in featInput[boldTask][k]['inclusion_list']:
                            ls_customFiles =[x for x in ls_customFiles if item in x]

                    if len(ls_customFiles) != 1:
                        print('ERROR: found none or more than one file specified by ' + k )
                        print('\tCannot perform FEAT as specified... continuing to next file')
                        skipFlag = True
                        continue
                    designData[featInput[boldTask]['step2_line_pairs'][k]-1] = 'set fmri(' + k + ') "' + ls_customFiles[0]  + '"\n'
                else:
                    print('WARNING: support for line_pair option ' + k + ' is not available')
                    print('\tskipping this request and proceeding. Contact Matthew Sherwood')

            if skipFlag:
                continue

            with open(os.path.join(featDesignDir,featInput[boldTask]['step2_design_basename'] + '.fsf'), 'w', encoding='utf-8') as file:
                file.writelines(designData)

        #do I need to insert custom registration?
        if refImage and 'out_matrix_base' in refImageParams.keys():
            strucRegDir = os.path.join(creds.dataDir,'derivatives','sub-' + subName,'ses-' + sesNum,'flirt',refImageParams['input_bids_type'])
            strucRegMatrix = glob(os.path.join(strucRegDir,'*' + refImageParams['out_matrix_base']  + '.mat'))
            if len(strucRegMatrix) != 1:
                print('ERROR: found none or more than one structrual registration file')
                print('\tCannot perform FEAT as specified... continuing to next file')
                continue
            strucRegMatrix = strucRegMatrix[0]
            if not os.path.isfile(strucRegMatrix):
                os.system('echo "Warning: cannot find structural registration file ' + strucRegMatrix + '"')
                os.system('echo "Skipping matrix concatenation"')


        #run job on condor?
        if not options.SUBMIT:
            if refImage and 'out_matrix_base' in refImageParams.keys() and strucRegMatrix:
                feat_full_firstlevel(creds.dataDir, subName, sesNum, featDesignDir, featOutputDir, featInput[boldTask]['design_basename'], progress=options.progress, reference=refImageFile, step2designbasename=featInput[boldTask]['step2_design_basename'], strucregmatrix=strucRegMatrix)
            else:
                feat_full_firstlevel(creds.dataDir, subName, sesNum, featDesignDir, featOutputDir, featInput[boldTask]['design_basename'], progress=options.progress)
        else:

            if job_flag:
                job_feat = create_python_condor_job('feat_full_firstlevel','feat_full_firstlevel.py',
                                                    creds.machineNames,
                                                    submit,
                                                    error,
                                                    output,
                                                    log,
                                                    dagman) 
                job_flag = False 

            #create argument string
            argStr = (creds.dataDir + ' ' + 
                    subName + ' ' +
                    sesNum + ' ' +
                    featDesignDir + ' ' +
                    featOutputDir + ' ' +
                    featInput[boldTask]['design_basename'] + ' ' 
                    )
            if refImage:
                argStr += ' --reference ' + refImageFile
            if options.progress:
                argStr += ' --progress'
            if 'step2_design_basename' in featInput[boldTask].keys():
                argStr += ' --step2-design-basename ' + featInput[boldTask]['step2_design_basename']
            if strucRegMatrix:
                argStr += ' --struc-reg-matrix ' + strucRegMatrix

            #add arguments to condor job
            job_feat.add_arg(argStr)# + ' > ' + os.path.join(creds.s3_dir,s3_outLog))
            print('\tAdded job for feat full firstlevel analysis for file:  ' + f)
            print('\tOutput Directory:  ' + featOutputDir)
            featFlag = True




        




    if options.SUBMIT and featFlag:
        dagman.build_submit(fancyname=True)


    return


# ******************* MAIN ********************
def main():
    """
    The entry point of this program.
    """

    #get and evaluate options
    options = parse_arguments()
    read_credentials(options.PROJECT)

    #do some prep for parallel processing 
    if options.SUBMIT:
        #get some precursors
        now = datetime.datetime.today().strftime('%Y%m%d_%H%M')
        base = os.path.join(creds.dataDir,'derivatives','processing_logs','connect_feat_full_firstlevel')
        if not os.path.isdir(base):
            os.makedirs(base)

        #output files
        submit = os.path.join(base,'feat_full_firstlevel_' + now + '.submit')
        error = os.path.join(base,'feat_full_firstlevel_' + now + '.error')
        output = os.path.join(base,'feat_full_firstlevel_' + now + '.output')
        log = os.path.join(base,'feat_full_firstlevel_' + now + '.log')
        dagman = Dagman(name=options.PROJECT + '-feat_full_firstlevel', submit=submit)


        #perform struc 2 standard registration
        modality_process(options,submit=submit,error=error,output=output,log=log,dagman=dagman)

    else:
        modality_process(options)

    

    

if __name__ == '__main__':
    main()
