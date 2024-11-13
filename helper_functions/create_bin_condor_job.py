#!/resshare/general_processing_codes/python3_venv/bin/python
# the command above ^^^ sets python 3.6.9 as the interpreter for this program

# Created by Matthew Sherwood (matt.sherwood@wright.edu, matthew.sherwood.7.ctr@us.af.mil)
# Created on 22 Jan 2021
#

import os,sys
from pycondor import Job

#local import
REALPATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(REALPATH)
# print(REALPATH)

#versioning
VERSION = '1.0.1'
DATE = '22 Jan 2021'


# ******************* CREATE PYTHON JOB ********************
def create_bin_condor_job(jobName,exeName,machineNames,submit,error,output,log,dagman):
    """
    Creates a condor job for python helper functions. 

    create_python_condor_job(jobName,exeName,machineNames,submit,error,output,log,dagman)

    Arguments:

        jobName (str): name for the parallel htcondor job

        exeName (str): helper_function executable name

        machineNames (list): list of machine names to to execute jobs on

        submit (str): fullpath to output submit file

        error (str): fullpath to output error file

        output (str): fullpath to output output file

        log (str): fullpath to output log file

        dagman (pycondor.Dagman): already created pycondor Dagman object

    Returns:
        pycondor.Job: configured pycondor Job object
    """

    #create machine requirements string
    reqs = ''
    if machineNames:
        for c in range(len(machineNames)):
            if c > 0:
                reqs += ' || '
            reqs += 'Machine == "' + machineNames[c] + '"'
    extraLines = ['stream_output = True','RunAsOwner = True','docker_image = wsuconnect/neuro']

    #create job
    # print(os.path.join(REALPATH,'helper_functions',exeName))
    # job_out = Job(name=jobName, executable=os.path.join('/usr','bin',exeName), submit=submit, error=error, output=output, log=log, dag=dagman, getenv=False, extra_lines=extraLines, requirements=reqs, universe='docker',request_cpus=1,request_memory='20g')
    job_out = Job(name=jobName, executable=os.path.join('/resshare/general_processing_codes/helper_functions',exeName), submit=submit, error=error, output=output, log=log, dag=dagman, getenv=False, extra_lines=extraLines, requirements=reqs, universe='docker',request_cpus=1,request_memory='20g')

    
    
    return job_out

    






