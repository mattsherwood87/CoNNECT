#!/resshare/wsuconnect/python3_venv/bin/python
# the command above ^^^ sets python 3.10.10 as the interpreter for this program

# Created by Matthew Sherwood (matt.sherwood@wright.edu, matthew.sherwood.7.ctr@us.af.mil)
# Created on 23 Dec 2020
#
# Modified on 25 October 2024 - update to new session formats and use of helper_functions
# Modified on 17 April 2023 - update to WSU format
# Modified on 24 Nov 2021 - improve efficiency based on processed_data_check output
# Modified on 5 Nov 2021 - implement BIDS formatting
# Modified on 11 Jan 2021 - add utilization of instance_ids.json

import os
import time
import sys
import datetime
import argparse
import pandas as pd
import shutil
from glob import glob as glob
import json


#local import
REALPATH = os.path.realpath(__file__)
sys.path.append(os.path.dirname(REALPATH))
import support_tools as st


# GLOBAL INFO
#versioning
VERSION = '5.0.0'
DATE = '25 October 2024'

#input argument parser

# ******************* PARSE COMMAND LINE ARGUMENTS ********************
parser = argparse.ArgumentParser('connect_create_raw_nii.py: copy raw nifti images (after dcm2nii conversion) to appropriate processed_data directory (will rename files according to parameters specific in <project>_scan_id.py within the Funding sub-directory within project_specific_functions directory')

parser.add_argument('-p','--project', required=True, action="store", dest="PROJECT", help="select a project from the credentials.json file", default=None)
parser.add_argument('-i','--in-dir', action="store", dest="IN_DIR", help="path to individual subject/session to search for raw nifti images", default=None)
parser.add_argument('--overwrite', action="store_true", dest="OVERWRITE", help="Force copy by skipping file checking", default=False)
parser.add_argument('--progress', help="Show progress (default FALSE)", action="store_true", dest="progress", default=False)
parser.add_argument('-v', '--version', help="Display the current version", action="store_true", dest="version")
    
        


# ******************* EVALUATE INPUT ARGUMENTS ********************
def evaluate_args(options):

    dataCheckFile = None
    
    #print version if selected
    if options.version:
        print('connect_create_raw_nii.py version {0}.'.format(VERSION)+" DATED: "+DATE)

    # if not os.path.isdir(options.IN_DIR):
    #     print('ERROR: input directory ' + options.IN_DIR + ' does NOT exist.')
    #     parser.print_help()


    if os.path.isfile(os.path.join(st.creds.dataDir,'derivatives','processing_logs',options.PROJECT + '_rawdata_check.tsv')):
        dataCheckFile = os.path.join(st.creds.dataDir,'derivatives','processing_logs',options.PROJECT + '_rawdata_check.tsv')
    else:
        print('WARNING: project data check file not found')
        print('\tRunning without optimization')

    return dataCheckFile


# ******************* CONFIRM EXTENSIONS ********************
def ext_check(filename):
    splitFilename = os.path.splitext(filename)
    if splitFilename[1] == ".gz":
        splitFilename2 = os.path.splitext(splitFilename[0])
        if splitFilename2[1] == ".nii":
            return 'nifti',splitFilename2[0]
        else:
            return '0','0'
    else:
        if splitFilename[1] == '.rda': 
            return 'rda',splitFilename[0]
        elif splitFilename[1] ==  '.txt': 
            return 'txt',splitFilename[0]
        elif splitFilename[1] ==  '.log': 
            return 'log',splitFilename[0]
        elif splitFilename[1] ==  '.7': 
            return '7',splitFilename[0]
        else: 
            return '0','0'



# ******************* EVALUATE INPUT ARGUMENTS ********************
def process_single_dir(inDir,progress,override):
    #get time info for verbose option
    t = time.time()
    now = datetime.datetime.now()

    #update progress
    if progress:
        print("Searching " + inDir + " @" + now.strftime("%m-%d-%Y %H:%M:%S"))


    ls_updatedFiles = []
    ls_existingFiles = []


    #get subject name from filename
    # print(inDir)
    st.subject.get_id(inDir)
    # subjectName,sessionNum = get_dir_identifiers(inDir)

    if not st.subject.id:
        return ls_updatedFiles,ls_existingFiles


    #output if requested
    if progress:
        print('\t SUBJECT: ' + st.subject.id + ' SESSION: ' + st.subject.sesNum)

    #get all files in directory
    #source_fileList = sql_query(database=creds.database,searchtable=creds.searchSourceTable,searchcol='fullpath',regex=inDir,exclusion=['IMA','BMP','MRDC','REPORT'])#orinclusion=['.nii','.7','.log','.txt','.rda','.json'])
    source_fileList = glob(os.path.join(inDir,'*.*'))
    source_fileList.sort()
    for filepath in source_fileList:
        try:
            # splitFilename = os.path.splitext(os.path.join(inDir,filename))

            #only progress if nifti
            sourceDir = os.path.dirname(filepath)
            filename = os.path.basename(filepath)
            ext, basename = ext_check(filename)

            #file has an extension
            if ext != '0':
                
                #formulate output directory
                outDir = os.path.dirname(inDir)
                outDir = outDir.split('sourcedata')[0] + 'rawdata'

                #check if associated json exists
                if ext == 'nifti' and os.path.join(sourceDir,basename + '.json') in source_fileList:

                    #get scan identifier
                    scanName, bidsDir, scanKeys = st.get_scan_id(sourceDir,basename)
                    

                    if scanName == '0':
                        if progress:
                            print('\t\tskipping: ' + os.path.join(sourceDir,basename) + '\tscan type: NOT DEFINED')

                    else:
                        if progress:#this is just a nother test
                            print('\t\tprocessing: ' + os.path.join(sourceDir,basename) + '\tscan type: ' + scanName)
                        
                        #create base path and filename for move
                        baseOutput = os.path.join(outDir,'sub-' + st.subject.id,'ses-' + st.subject.sesNum,bidsDir,
                                                  'sub-' + st.subject.id + '_ses-' + st.subject.sesNum + scanName)
                        
                        #create directory if is does not exist
                        if not os.path.isdir(os.path.dirname(baseOutput)):
                            os.makedirs(os.path.dirname(baseOutput))
                            if progress:
                                print('\t\t\tcreating output directory ' + os.path.basename(baseOutput))

                        # if not os.path.isdir(os.path.dirname(baseOutput.replace('s3://' + creds.bucket,creds.s3_dir))):
                        #     os.makedirs(os.path.dirname(baseOutput.replace('s3://' + creds.bucket,creds.s3_dir)))
                        #     if progress:
                        #         print('\t\t\tcreating output directory ' + os.path.dirname(baseOutput.replace('s3://' + creds.bucket,creds.s3_dir)))

                        #move associated json, txt, and nii.gz files
                        if os.path.join(sourceDir,basename + '.nii.gz') in source_fileList:
                            if override or not os.path.isfile(baseOutput + '.nii.gz'):
                                shutil.move(os.path.join(sourceDir,basename + '.nii.gz'), baseOutput + '.nii.gz')
                                d={}
                                d['fullpath'] = os.path.join(sourceDir,basename + '.nii.gz')
                                st.mysql_commands.sql_table_remove(st.creds.searchSourceTable,d)
                                
                                ls_updatedFiles.append(baseOutput + '.nii.gz')
                                if progress:
                                    print('\t\t\tcopying ' + os.path.join(sourceDir,basename + '.nii.gz') + ' to ' + baseOutput + '.nii.gz')
                                
                        if os.path.join(sourceDir,basename + '.json') in source_fileList:
                            if override or not os.path.isfile(baseOutput + '.json'):
                                shutil.move(os.path.join(sourceDir,basename + '.json'), baseOutput + '.json')
                                d={}
                                d['fullpath'] = os.path.join(sourceDir,basename + '.json')
                                st.mysql_commands.sql_table_remove(st.creds.searchSourceTable,d)
                                ls_updatedFiles.append(baseOutput + '.json')
                                if progress:
                                    print('\t\t\tcopying ' + os.path.join(sourceDir,basename + '.json') + ' to ' + baseOutput + '.json')

                                if 'TaskName' in scanKeys.keys() or 'Units' in scanKeys.keys():
                                    with open(baseOutput + '.json', 'r') as j:
                                        imgHeader = json.load(j)
                                    for k in ['SliceTiming','TaskName','Units']:
                                        if k in scanKeys.keys():
                                            imgHeader[k] = scanKeys[k]

                                    if 'PhaseEncodingAxis' in imgHeader.keys():
                                        imgHeader['PhaseEncodingDirection'] = imgHeader.pop('PhaseEncodingAxis')

                                    if 'EstimatedEffectiveEchoSpacing' in imgHeader.keys():
                                        imgHeader['EffectiveEchoSpacing'] = imgHeader.pop('EstimatedEffectiveEchoSpacing')

                                    if 'EstimatedTotalReadoutTime' in imgHeader.keys():
                                        imgHeader['TotalReadoutTime'] = imgHeader.pop('PhaseEncodingAxis')
                                    
                                    with open(baseOutput + '.json', 'w') as j:
                                        json.dump(imgHeader, j, indent='\t', sort_keys=True)
                                
                        if os.path.join(sourceDir,basename + '.txt') in source_fileList:
                            if override or not os.path.isfile(baseOutput + '.txt'):
                                shutil.move(os.path.join(sourceDir,basename + '.txt'), baseOutput + '.txt')
                                d={}
                                d['fullpath'] = os.path.join(sourceDir,basename + '.txt')
                                st.mysql_commands.sql_table_remove(st.creds.searchSourceTable,d)
                                ls_updatedFiles.append(baseOutput + '.txt')
                                if progress:
                                    print('\t\t\tcopying ' + os.path.join(sourceDir,basename + '.txt') + ' to ' + baseOutput + '.txt')

                            #also copy bval and bvec files for DWI
                            if 'dwi' in scanName and not 'FA' in scanName:
                                if os.path.join(sourceDir,basename + '.bval') in source_fileList:
                                    if override or not os.path.isfile(baseOutput + '.bval'):
                                        shutil.move(os.path.join(sourceDir,basename + '.bval'),baseOutput + '.bval')
                                        shutil.move(os.path.join(sourceDir,basename + '.bvec'),baseOutput + '.bvec')
                                        d={}
                                        d['fullpath'] = [os.path.join(sourceDir,basename + '.bvec'), os.path.join(sourceDir,basename + '.bvec')]
                                        st.mysql_commands.sql_table_remove(st.creds.searchSourceTable,d)
                                        # os.rename(os.path.join(inDir,basename + '.bval'),baseOutput + '.bval')
                                        # os.rename(os.path.join(inDir,basename + '.bvec'),baseOutput + '.bvec')
                                        # os.system("cp " + os.path.join(inDir,basename + '.bval') + " " + baseOutput + ".bval")
                                        # os.system("cp " + os.path.join(inDir,basename + '.bvec') + " " + baseOutput + ".bvec")
                                        ls_updatedFiles.append(baseOutput + '.bval')
                                        ls_updatedFiles.append(baseOutput + '.bvec')
                                        if progress:
                                            print('\t\t\tcopying ' + os.path.join(sourceDir,basename + '.bval') + ' to ' + baseOutput + '.bval')
                                            print('\t\t\tcopying ' + os.path.join(sourceDir,basename + '.bvec') + ' to ' + baseOutput + '.bvec')


                # elif ext == 'rda' or ext == '7':
                #     tmp_outDir = os.path.join(outDir,'sub-' + subjectName,'sess-' + sessionNum)
                #     if not os.path.isdir(tmp_outDir.replace('s3://' + creds.bucket,creds.s3_dir)):
                #         os.makedirs(tmp_outDir.replace('s3://' + creds.bucket,creds.s3_dir))
                #         if progress:
                #             print('\t\t\tcreating output directory ' + tmp_outDir.replace('s3://' + creds.bucket,creds.s3_dir))

                #     tmp_outDir = os.path.join(tmp_outDir,'svs')
                #     if not os.path.isdir(tmp_outDir.replace('s3://' + creds.bucket,creds.s3_dir)):
                #         os.makedirs(tmp_outDir.replace('s3://' + creds.bucket,creds.s3_dir))
                #         if progress:
                #             print('\t\t\tcreating output directory ' + tmp_outDir.replace('s3://' + creds.bucket,creds.s3_dir))

                #     #move associated rda, log, or .7 file file
                #     if progress:
                #         print('\t\tprocessing: ' + os.path.join(inDir,basename) + ' scan type: ' + ext)

                #     get_spec_base(os.path.join(inDir,basename + '.' + ext),creds)
                #     # os.rename(os.path.join(inDir,basename + '.' + ext),os.path.join(outDir,subjectName,'SESSION_' + sessionNum,basename + '.' + ext))
                #     outFile = os.path.join(tmp_outDir,subjectName + '_SESS' + sessionNum + '_acq-' + specBase.spectraType + '-' + specBase.spectraName + '_svs.' + ext)
                #     if override or not os.path.isfile(outFile.replace('s3://' + creds.bucket,creds.s3_dir)):
                #         os.system('aws s3 cp ' + os.path.join(inDir.replace(creds.s3_dir,'s3://' + creds.bucket),basename + '.' + ext) + ' ' + outFile)
                #         # os.system("cp " + os.path.join(inDir,basename + '.' + ext) + " " + outFile)
                #         ls_updatedFiles.append(outFile)
                #         if progress:
                #             print('\t\t\tcopying ' + ext + ' file ' + outFile)
                #     else:
                #         if progress:
                #             print('\t\t\tskipping file ' + os.path.join(inDir,basename + '.' + ext))
                #         ls_existingFiles.append(os.path.join(inDir,basename + '.' + ext))

                elif ext in ['log','xdf']:
                    tmp_outDir = os.path.isdir(os.path.join(outDir,'sub-' + st.subject.id,'ses-' + st.subject.sesNum,'beh'))
                    if not os.path.isdir(tmp_outDir):
                        os.makedirs(tmp_outDir)
                        if progress:
                            print('\t\t\tcreating output directory ' + tmp_outDir)

                    #move associated rda, log, or .7 file file
                    if progress:
                        print('\t\tprocessing: ' + os.path.join(sourceDir,basename) + ' scan type: ' + ext)
                    if override or not os.path.isfile(os.path.join(tmp_outDir,basename + '.' + ext)):
                        outFile = os.path.join(tmp_outDir, basename + '.' + ext)
                        shutil.move(os.path.join(sourceDir,basename + '.' + ext),outFile)
                        d={}
                        d['fullpath'] = os.path.join(sourceDir,basename + '.' + ext)
                        st.mysql_commands.sql_table_remove(st.creds.searchSourceTable,d)
                        ls_updatedFiles.append(outFile)
                        if progress:
                            print('\t\t\tcopying ' + ext + ' file ' + outFile)
                    else:
                        if progress:
                            print('\t\t\tskipping file ' + os.path.join(sourceDir,basename + '.' + ext))
                        ls_existingFiles.append(os.path.join(sourceDir,basename + '.' + ext))

                elif ext == 'txt' and not os.path.join(sourceDir,basename + '.json') in source_fileList:
                    tmp_outDir = os.path.join(outDir,'sub-' + st.subject.id,'ses-' + st.subject.sesNum,'beh')
                    if not os.path.isdir(tmp_outDir):
                        os.makedirs(tmp_outDir)
                        if progress:
                            print('\t\t\tcreating output directory ' + tmp_outDir)

                    #move associated rda, log, or .7 file file
                    if progress:
                        print('\t\tprocessing: ' + os.path.join(sourceDir,basename) + ' scan type: ' + ext)
                    if override or not os.path.isfile(os.path.join(tmp_outDir,basename + '.' + ext)):
                        outFile = os.path.join(tmp_outDir,basename + '.' + ext)
                        shutil.move(os.path.join(sourceDir,basename + '.' + ext),outFile)
                        d={}
                        d['fullpath'] = os.path.join(sourceDir,basename + '.' + ext)
                        st.mysql_commands.sql_table_remove(st.creds.searchSourceTable,d)
                        ls_updatedFiles.append(outFile)
                        if progress:
                            print('\t\t\tcopying ' + ext + ' file ' + outFile)
                    else:
                        if progress:
                            print('\t\t\tskipping file ' + os.path.join(sourceDir,basename + '.' + ext))
                        ls_existingFiles.append(os.path.join(sourceDir,basename + '.' + ext))

        #catch any errors
        except Exception as e:
            print('ERROR: ' + basename + ' ', end='')
            print(e)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)


            outputTxt = os.path.join(st.creds.dataDir,'derivatives','processing_logs','connect_create_raw_nii',st.creds.project + '_create_raw_nii' + now.strftime('%Y%m%d_%H%M') + '.error')
            if not os.path.isdir(os.path.dirname(outputTxt)):
                os.makedirs(os.path.dirname(outputTxt))
            with open(outputTxt,'a+') as txtFile:
                txtFile.write('ERROR: ' + basename + ' ' + '\n\t')
                txtFile.write(str(e))
                txtFile.write('\n')

    #provide final update
    elapsed_t = time.time() - t
    if progress:
        print('\n\tCompleted searching ' + inDir + ' in ' + str(elapsed_t) + ' seconds')

    return ls_updatedFiles,ls_existingFiles



# ******************* PROCESS MULTIPLE DIRECTORIES ********************
def process_multiple_dir(inDir,progress,override):
    

    ls_updatedFiles = []
    ls_existingFiles = []

    #loop over all session directories that you can find
    source_dirsToProcess = st.mysql_commands.sql_query_dirs(regex='acq-',source=False,progress=True)#,inclusion=incExcDict['inclusion'],exclusion=incExcDict['exclusion'])
    a = [x for x in source_dirsToProcess]
    a = sorted(list(set(a)))
    #a=sorted([x[0] for x in os.walk(inDir) if 'ses' in os.path.basename(x[0])])

    for item in a:
        if 'ses-' in item:
            tmp_ls_updatedFiles,tmp_ls_existingFiles = process_single_dir(item,progress,override)
            ls_existingFiles.extend(tmp_ls_existingFiles)
            ls_updatedFiles.extend(tmp_ls_updatedFiles)

    return ls_updatedFiles,ls_existingFiles


# *******************  MAIN  ******************** 
if __name__ == '__main__':
    """
    The entry point of this program.
    """
    options = parser.parse_args()


    st.creds.read(options.PROJECT)
    dataCheckFile = evaluate_args(options)
    now = datetime.datetime.today().strftime('%Y%m%d_%H%M')

    if dataCheckFile:
        df_rawData = pd.read_csv(dataCheckFile, sep='\t')
        df_rawData.sort_values(by=['participant_id','session'])
        # del df_rawData['Unnamed: 0']
    else:
        df_rawData = pd.DataFrame()


    

    #loop over all tables
    if not options.IN_DIR:
        ls_updatedFiles,ls_existingFiles = process_multiple_dir(os.path.join(st.creds.dataDir,'sourcedata'),options.progress,options.OVERWRITE)
    else:
        ls_updatedFiles,ls_existingFiles = process_single_dir(options.IN_DIR,options.progress,options.OVERWRITE)
        #print("Successfully updated " + sqlTable + "\n\tTotal time: " + str(elapsed_t) + " seconds\n\n")

    outputTxt = os.path.join(st.creds.dataDir,'derivatives','processing_logs','connect_create_raw_nii',st.creds.project + '_create_raw_nii-' + now + '_updated_files.log')
    if not os.path.isdir(os.path.dirname(outputTxt)):
        os.makedirs(os.path.dirname(outputTxt))
    with open(outputTxt,'a+') as txtFile:
        txtFile.writelines("%s\n" % l for l in ls_updatedFiles)

    outputTxt = os.path.join(st.creds.dataDir,'derivatives','processing_logs','connect_create_raw_nii',st.creds.project + '_create_raw_nii-' + now + '_existing_files.log')
    with open(outputTxt,'w') as txtFile:
        txtFile.writelines("%s\n" % l for l in ls_existingFiles)