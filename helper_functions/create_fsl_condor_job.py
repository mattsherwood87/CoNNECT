#!/resshare/general_processing_codes/python3_venv/bin/python
# the command above ^^^ sets python 3.11.11 as the interpreter for this program

# Created by Matthew Sherwood (matt.sherwood@wright.edu, matthew.sherwood.7.ctr@us.af.mil)
# Created on 22 Jan 2021
#

import os
from pycondor import Job

#versioning
VERSION = '1.0.1'
DATE = '22 Jan 2021'


FSLDIR = os.environ["FSLDIR"]


# ******************* QUERY OUTPUT DIRECTORIES FOR NIFTIS ********************
def create_fsl_condor_job(jobName,exeName,machineNames,submit,error,output,log,dagman):
    """
    Creates a condor job for fsl commands. 

    create_fsl_condor_job(jobName,exeName,machineNames,submit,error,output,log,dagman)

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
    for c in range(len(machineNames)):
        if c > 0:
            reqs += ' || '
        reqs += 'Machine == "' + machineNames[c] + '"'
    extraLines = ['stream_output = True']

    #create job
    job_out = Job(name=jobName, executable=os.path.join(FSLDIR,'bin',exeName), submit=submit, error=error, output=output, log=log, dag=dagman, getenv=True, extra_lines=extraLines, requirements=reqs, universe='vanilla')
    
    return job_out

    






