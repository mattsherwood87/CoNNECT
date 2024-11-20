#!/resshare/wsuconnect/python3_venv/bin/python
# the command above ^^^ sets python 3.10.10 as the interpreter for this program

# Created by Matthew Sherwood (matt.sherwood@wright.edu, matthew.sherwood.7.ctr@us.af.mil)
# Created on 28 Dec 2020
#
# v2.0.0 on 1 April 2023
# v1.1.2  on 25 Oct 2021 Modification (1.1.2) - add inclusion of *_dcm2nii_input.json for input parameters
# v1.1.1 on 16 Sept 2021 Modification (1.1.1) - remove checking local scratch disk for output using glob: unncessary with direct s3 mount
# v1.1.0 11 Jan 2021 Modification (1.1.0)- add utilization of instance_ids.json

import os
import argparse
from pycondor import Dagman
import datetime
import sys
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 


#local import
REALPATH = os.path.realpath(__file__)

sys.path.append(os.path.dirname(REALPATH))
import support_tools as st


# GLOBAL INFO
#versioning
VERSION = '2.1.0'
DATE = '14 Nov 2024'



# ******************* PARSE COMMAND LINE ARGUMENTS ********************
parser = argparse.ArgumentParser("This program is the batch wrapper command to perform DICOM to NIfTI conversion using dcm2niix. The program searches the specified project's searchSourceTable for acquisition folders (acq-*) which contain DICOM images and runs wsuconnect.support_tools.convert_dicoms for each returned directory.")
parser.add_argument('-p','--project', required=True, action="store", dest="PROJECT", help="update the selected project: " + ' '.join(st.creds.projects))
parser.add_argument('--overwrite', action="store_true", dest="OVERWRITE", help="Force conversion by skipping directory and database checking", default=False)
parser.add_argument('--docker', action="store_true", dest="DOCKER", help="Submit conversion to HTCondor and process in wsuconnect/neuro docker container [default=False]", default=False)
parser.add_argument('-s', '--submit', action="store_true", dest="SUBMIT", help="Submit conversion to condor for parallel conversion", default=False)
parser.add_argument('-v', '--version', action="store_true", dest="version", help="Display the current version")
parser.add_argument('--progress', action="store_true", dest="progress", help="Show progress (default FALSE)", default=False)



# ******************* MAIN ********************
def main():
    """
    The entry point of this program.
    """
    #read crendentials from $SCRATCH_DIR/instance_ids.json
    ls_updatedFiles = []
    ls_existingFiles = []

    #get and evaluate options
    options = parser.parse_args()
    
    if options.version:
        print('connect_dcm2nii.py version {0}.'.format(VERSION)+" DATED: "+DATE)
    
    # #determine if the project exists
    # if not options.PROJECT in st.creds.projects:
    #     if not options.version:
    #         print("ERROR: user must define a project using [-p|--project <project>]\n\n")
    #         parser.print_help()
    #     sys.exit()

    
    st.read_credentials(options.PROJECT)

    # find all directories to process
    source_dirsToProcess = sorted([x[0] for x in os.walk(os.path.join(st.creds.dataDir,'sourcedata')) if 'acq-' in os.path.basename(x[0])])
    source_dirsToProcess = list(set(source_dirsToProcess))

    now = datetime.datetime.today().strftime('%Y%m%d_%H%M')
    if options.SUBMIT or options.DOCKER:

        #splitDirs = source_dirsToProcess[0].split('/')
        base = os.path.join(st.creds.dataDir,'derivatives','processing_logs','connect_dcm2niix')
        # base = base.replace(creds.s3_prefix + '/','')
        if not os.path.isdir(base):
            os.makedirs(base)

        #output files
        submit = os.path.join(base,'dcm2niix_' + now + '.submit')
        error = os.path.join(base,'dcm2niix_' + now + '.error')
        output = os.path.join(base,'dcm2niix_' + now + '.output')
        log = os.path.join(base,'dcm2niix_' + now + '.log')
        dagman = Dagman(name=options.PROJECT + '-dcm2niix', submit=submit)
        

        #create jobs
        if options.DOCKER:
            job_dcm2nii = st.create_python_condor_job('dcm2niix',
                                                      'convert_dicoms.py',
                                                      st.creds.machineNames,
                                                      submit,
                                                      error,
                                                      output,
                                                      log,
                                                      dagman,
                                                      docker=True,
                                                      docker_image='wsuconnect/neuro',
                                                      docker_mount_if=st.creds.dockerMountIf,
                                                      request_cpus=1,
                                                      request_memory='5g')
        else:
            job_dcm2nii = st.create_python_condor_job('dcm2niix',
                                                      'convert_dicoms.py',
                                                      st.creds.machineNames,
                                                      submit,
                                                      error,
                                                      output,
                                                      log,
                                                      dagman)


    #convert each directory
    source_dirsToProcess.sort()
    for source_singleDir in source_dirsToProcess:
        # source_singleDir = source_singleDir.replace(creds.s3_prefix + '/','')
        if not options.OVERWRITE:
            #check output_dir for niftis on both sql db (processed_data) and local dir (optional override flag)
            subjectName,sessionNum = st.get_dir_identifiers(source_singleDir) #get subject name from filename

            #check processed_data directory for nifti images
            processedDataOutput = os.path.join('rawdata','sub-' + subjectName,'ses-' + sessionNum)#create base path and filename for move
            processedFlag = st.mysql_commands.sql_query_dir_check('nii.gz',processedDataOutput,False)

            #continue if no files in processed_data directory for given subject/session
            if processedFlag:
                ls_existingFiles.append(source_singleDir)
                if options.progress:
                    print('NIfTI Images Found: Skipping ' + source_singleDir)
            else:

                #convert dicoms to nifti files
                ls_updatedFiles.append(source_singleDir)
                if not options.SUBMIT and not options.DOCKER:  
                    st.convert_dicoms(source_singleDir,options.progress)
                else:
                    str_args = '-i ' + source_singleDir
                    if options.progress:
                        str_args += ' --progress'
                    job_dcm2nii.add_arg(str_args)
                    if options.progress:
                        print('Added directory to conversion queue ' + source_singleDir)               
                    

        else: #overwrite
            ls_updatedFiles.append(source_singleDir)
            if not options.SUBMIT:
                st.convert_dicoms(source_singleDir,options.progress)
            else:
                job_dcm2nii.add_arg(source_singleDir + ' ' + str(options.progress))
        
    if options.SUBMIT or options.DOCKER:
        # job_sleep.add_child(job_dcm2nii)
        # job_dcm2nii.add_child(job_stop) - Can I force this requirement on the MASTER?
        dagman.build_submit()

    #write conversion lists to file
    print('\n\n NIfTI conversion COMPLETE: Please check')
    outputTxt = os.path.join(st.creds.dataDir,'derivatives','processing_logs','connect_dcm2niix',st.creds.project + '_dcm2nii_' + now + '_updated_files.log')
    if not os.path.isdir(os.path.dirname(outputTxt)):
        os.makedirs(os.path.dirname(outputTxt))

    with open(outputTxt,'a+') as txtFile:
        txtFile.writelines("%s\n" % l for l in ls_updatedFiles)
    print('\t' + outputTxt)

    outputTxt = os.path.join(st.creds.dataDir,'derivatives','processing_logs','connect_dcm2niix',st.creds.project + '_dcm2nii_' + now + '_existing_files.log')
    with open(outputTxt,'w') as txtFile:
        txtFile.writelines("%s\n" % l for l in ls_existingFiles)
    print('\t' + outputTxt)
    

if __name__ == '__main__':
    main()
