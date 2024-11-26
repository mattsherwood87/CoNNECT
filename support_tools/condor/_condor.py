# condor.py

# Copywrite Matthew Sherwood (matt.sherwood@wright.edu, matthew.sherwood.7.ctr@us.af.mil)
# Created on 22 Jan 2021
#
# Modified on 15 Nov 2024 - implement docker within condor jobs

import os,sys
from pycondor import Job

#local import
REALPATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
sys.path.append(REALPATH)
# print(REALPATH)

#versioning
VERSION = '2.0.1'
DATE = '15 Nov 2024'


FSLDIR = os.environ["FSLDIR"]
FREESURFERDIR = os.environ["FREESURFER_HOME"]


# ******************* CREATE PYTHON JOB ********************
def create_bin_condor_job(jobName: str,exeName: str,machineNames: list,submit: str,error: str,output: str,log:str,dagman: str,docker: bool = False, docker_image: str = 'wsuconnect/neuro', docker_mount_if: str = None, request_cpus: int = 1, request_memory: str = '5g'):
    """
    Creates a pycondor job object to implement a binary from /usr/bin.     

    :param jobName: name for the parallel htcondor job
    :type jobName: str

    :param exeName: helper_function executable name
    :type exeName: str

    :param machineNames: list of machine names to to execute jobs on
    :type machineNames: list

    :param submit: fullpath to condor submit file
    :type submit: str

    :param error: fullpath to condor error file
    :type error: str

    :param output: fullpath to condor output file
    :type output: str

    :param log: fullpath to condor log file
    :type log: str

    :param dagman: pointer to created pycondor Dagman object
    :type dagman: pycondor.Dagman

    :param docker: flag to execute job using a docker container (default False), defaults to False
    :type docker: bool, optional

    :param docker_image: docker image for docker execution, defaults to 'wsuconnect/neuro'
    :type docker_image: str, optional

    :param docker_mount_if: docker share to mount (see credentials.json), defaults to None
    :type docker_mount_if: str, optional

    :param request_cpus: number of cpus to allocate to docker container, defaults to 1
    :type request_cpus: int, optional

    :param request_memory: memory in bytes to allocate to docker container, defaults to '5g'
    :type request_memory: str, optional

    :return: pointer to a configured pycondor Job object 
    :rtype: pycondor.Job
    """

    #create machine requirements string
    reqs = ''
    if machineNames:
        for c in range(len(machineNames)):
            if c > 0:
                reqs += ' || '
            reqs += 'Machine == "' + machineNames[c] + '"'
    extraLines = ['stream_output = True','RunAsOwner = True']

    #create job
    # print(os.path.join(REALPATH,'helper_functions',exeName))
    if not docker:
        job_out = Job(name=jobName, executable=os.path.join('/usr','bin',exeName), submit=submit, error=error, output=output, log=log, dag=dagman, getenv=False, extra_lines=extraLines, requirements=reqs, universe='vanilla')
    else:
        extraLines.append('docker_image = ' + docker_image)
        if docker_mount_if == 'resshare19':
            extraLines.extend(["+MOUNT_RESSHARE19 = true", "+MOUNT_RESSHARE20 = false", "+MOUNT_RESSHARE21 = false"])
        elif docker_mount_if == 'resshare20':
            extraLines.extend(["+MOUNT_RESSHARE19 = false", "+MOUNT_RESSHARE20 = true", "+MOUNT_RESSHARE21 = false"])
        elif docker_mount_if == 'resshare21':
            extraLines.extend(["+MOUNT_RESSHARE19 = false", "+MOUNT_RESSHARE20 = false", "+MOUNT_RESSHARE21 = true"])

        job_out = Job(name=jobName, executable=os.path.join('/usr','bin',exeName), submit=submit, error=error, output=output, log=log, dag=dagman, getenv=False, extra_lines=extraLines, requirements=reqs, universe='docker',request_cpus=request_cpus,request_memory=request_memory)

    
    
    return job_out


# ******************* QUERY OUTPUT DIRECTORIES FOR NIFTIS ********************
def create_freesurfer_condor_job(jobName: str,exeName: str,machineNames: list,submit: str,error: str,output: str,log:str,dagman: str,docker: bool = False, docker_image: str = 'wsuconnect/neuro', docker_mount_if: str = None, request_cpus: int = 1, request_memory: str = '5g'):
    """
    Creates a pycondor job object to implement FreeSurfer functions. 

    :param jobName: name for the parallel htcondor job
    :type jobName: str

    :param exeName: helper_function executable name
    :type exeName: str

    :param machineNames: list of machine names to to execute jobs on
    :type machineNames: list

    :param submit: fullpath to condor submit file
    :type submit: str

    :param error: fullpath to condor error file
    :type error: str

    :param output: fullpath to condor output file
    :type output: str

    :param log: fullpath to condor log file
    :type log: str

    :param dagman: pointer to created pycondor Dagman object
    :type dagman: pycondor.Dagman

    :param docker: flag to execute job using a docker container (default False), defaults to False
    :type docker: bool, optional

    :param docker_image: docker image for docker execution, defaults to 'wsuconnect/neuro'
    :type docker_image: str, optional

    :param docker_mount_if: docker share to mount (see credentials.json), defaults to None
    :type docker_mount_if: str, optional

    :param request_cpus: number of cpus to allocate to docker container, defaults to 1
    :type request_cpus: int, optional

    :param request_memory: memory in bytes to allocate to docker container, defaults to '5g'
    :type request_memory: str, optional

    :return: pointer to a configured pycondor Job object 
    :rtype: pycondor.Job
    """

    #create machine requirements string
    reqs = ''
    for c in range(len(machineNames)):
        if c > 0:
            reqs += ' || '
        reqs += 'Machine == "' + machineNames[c] + '"'
    extraLines = ['stream_output = True', 'RunAsOwner = True']

    #create job
    if not docker:
        job_out = Job(name=jobName, executable=os.path.join(FREESURFERDIR,'bin',exeName), submit=submit, error=error, output=output, log=log, dag=dagman, getenv=True, extra_lines=extraLines, requirements=reqs, universe='vanilla')
    else:
        extraLines.append('docker_image = ' + docker_image)
        if docker_mount_if == 'resshare19':
            extraLines.extend(["+MOUNT_RESSHARE19 = true", "+MOUNT_RESSHARE20 = false", "+MOUNT_RESSHARE21 = false"])
        elif docker_mount_if == 'resshare20':
            extraLines.extend(["+MOUNT_RESSHARE19 = false", "+MOUNT_RESSHARE20 = true", "+MOUNT_RESSHARE21 = false"])
        elif docker_mount_if == 'resshare21':
            extraLines.extend(["+MOUNT_RESSHARE19 = false", "+MOUNT_RESSHARE20 = false", "+MOUNT_RESSHARE21 = true"])

        FREESURFERDIR = '/opt/freesurfer-7.4.1'
        job_out = Job(name=jobName, executable=os.path.join(FREESURFERDIR,exeName), submit=submit, error=error, output=output, log=log, dag=dagman, getenv=False, extra_lines=extraLines, requirements=reqs, universe='docker',request_cpus=request_cpus,request_memory=request_memory)
    
    return job_out


# ******************* QUERY OUTPUT DIRECTORIES FOR NIFTIS ********************
def create_fsl_condor_job(jobName: str,exeName: str,machineNames: list,submit: str,error: str,output: str,log:str,dagman: str,docker: bool = False, docker_image: str = 'wsuconnect/neuro', docker_mount_if: str = None, request_cpus: int = 1, request_memory: str = '5g'):
    """
    Creates a pycondor job object to implement FSL functions. 

    :param jobName: name for the parallel htcondor job
    :type jobName: str

    :param exeName: helper_function executable name
    :type exeName: str

    :param machineNames: list of machine names to to execute jobs on
    :type machineNames: list

    :param submit: fullpath to condor submit file
    :type submit: str

    :param error: fullpath to condor error file
    :type error: str

    :param output: fullpath to condor output file
    :type output: str

    :param log: fullpath to condor log file
    :type log: str

    :param dagman: pointer to created pycondor Dagman object
    :type dagman: pycondor.Dagman

    :param docker: flag to execute job using a docker container (default False), defaults to False
    :type docker: bool, optional

    :param docker_image: docker image for docker execution, defaults to 'wsuconnect/neuro'
    :type docker_image: str, optional

    :param docker_mount_if: docker share to mount (see credentials.json), defaults to None
    :type docker_mount_if: str, optional

    :param request_cpus: number of cpus to allocate to docker container, defaults to 1
    :type request_cpus: int, optional

    :param request_memory: memory in bytes to allocate to docker container, defaults to '5g'
    :type request_memory: str, optional

    :return: pointer to a configured pycondor Job object 
    :rtype: pycondor.Job
    """

    #create machine requirements string
    reqs = ''
    for c in range(len(machineNames)):
        if c > 0:
            reqs += ' || '
        reqs += 'Machine == "' + machineNames[c] + '"'
    extraLines = ['stream_output = True', 'RunAsOwner = True']

    #create job
    if not docker:
        job_out = Job(name=jobName, executable=os.path.join(FSLDIR,'bin',exeName), submit=submit, error=error, output=output, log=log, dag=dagman, getenv=True, extra_lines=extraLines, requirements=reqs, universe='vanilla')
    else:
        extraLines.append('docker_image = ' + docker_image)
        if docker_mount_if == 'resshare19':
            extraLines.extend(["+MOUNT_RESSHARE19 = true", "+MOUNT_RESSHARE20 = false", "+MOUNT_RESSHARE21 = false"])
        elif docker_mount_if == 'resshare20':
            extraLines.extend(["+MOUNT_RESSHARE19 = false", "+MOUNT_RESSHARE20 = true", "+MOUNT_RESSHARE21 = false"])
        elif docker_mount_if == 'resshare21':
            extraLines.extend(["+MOUNT_RESSHARE19 = false", "+MOUNT_RESSHARE20 = false", "+MOUNT_RESSHARE21 = true"])

        FSLDIR = '/opt/fsl-6.0.4'
        job_out = Job(jobName, executable=os.path.join(FSLDIR,exeName), submit=submit, error=error, output=output, log=log, dag=dagman, getenv=False, extra_lines=extraLines, requirements=reqs, universe='docker',request_cpus=request_cpus,request_memory=request_memory)
    
    return job_out


# ******************* CREATE PYTHON JOB ********************
def create_python_condor_job(jobName: str,exeName: str,machineNames: list,submit: str,error: str,output: str,log:str,dagman: str,docker: bool = False, docker_image: str = 'wsuconnect/neuro', docker_mount_if: str = None, request_cpus: int = 1, request_memory: str = '5g'):
    """
    Creates a pycondor job object to implement python functions from support_tools. 

    :param jobName: name for the parallel htcondor job
    :type jobName: str

    :param exeName: helper_function executable name
    :type exeName: str

    :param machineNames: list of machine names to to execute jobs on
    :type machineNames: list

    :param submit: fullpath to condor submit file
    :type submit: str

    :param error: fullpath to condor error file
    :type error: str

    :param output: fullpath to condor output file
    :type output: str

    :param log: fullpath to condor log file
    :type log: str

    :param dagman: pointer to created pycondor Dagman object
    :type dagman: pycondor.Dagman

    :param docker: flag to execute job using a docker container (default False), defaults to False
    :type docker: bool, optional

    :param docker_image: docker image for docker execution, defaults to 'wsuconnect/neuro'
    :type docker_image: str, optional

    :param docker_mount_if: docker share to mount (see credentials.json), defaults to None
    :type docker_mount_if: str, optional

    :param request_cpus: number of cpus to allocate to docker container, defaults to 1
    :type request_cpus: int, optional

    :param request_memory: memory in bytes to allocate to docker container, defaults to '5g'
    :type request_memory: str, optional

    :return: pointer to a configured pycondor Job object 
    :rtype: pycondor.Job
    """

    #create machine requirements string
    reqs = ''
    if machineNames:
        for c in range(len(machineNames)):
            if c > 0:
                reqs += ' || '
            reqs += 'Machine == "' + machineNames[c] + '"'
    extraLines = ['stream_output = True', 'RunAsOwner = True']

    #create job
    # print(os.path.join(REALPATH,'helper_functions',exeName))
    if not docker:
        job_out = Job(name=jobName, executable=os.path.join(REALPATH,'support_tools',exeName), submit=submit, error=error, output=output, log=log, dag=dagman, getenv=True, extra_lines=extraLines, requirements=reqs, universe='vanilla')
    else:
        extraLines.append('docker_image = ' + docker_image)
        if docker_mount_if == 'resshare19':
            extraLines.extend(["+MOUNT_RESSHARE19 = true", "+MOUNT_RESSHARE20 = false", "+MOUNT_RESSHARE21 = false"])
        elif docker_mount_if == 'resshare20':
            extraLines.extend(["+MOUNT_RESSHARE19 = false", "+MOUNT_RESSHARE20 = true", "+MOUNT_RESSHARE21 = false"])
        elif docker_mount_if == 'resshare21':
            extraLines.extend(["+MOUNT_RESSHARE19 = false", "+MOUNT_RESSHARE20 = false", "+MOUNT_RESSHARE21 = true"])

        job_out = Job(jobName, executable=os.path.join(REALPATH,'support_tools',exeName), submit=submit, error=error, output=output, log=log, dag=dagman, getenv=False, extra_lines=extraLines, requirements=reqs, universe='docker',request_cpus=request_cpus,request_memory=request_memory)
    
    return job_out


# ******************* CREATE PYTHON JOB ********************
def create_python_venv_condor_job(jobName: str,exeName: str,machineNames: list,submit: str,error: str,output: str,log:str,dagman: str,docker: bool = False, docker_image: str = 'wsuconnect/neuro', docker_mount_if: str = None, request_cpus: int = 1, request_memory: str = '5g'):
    """
    Creates a pycondor job object to implement python functions from wsuconnect/python3_venv. 

    :param jobName: name for the parallel htcondor job
    :type jobName: str

    :param exeName: helper_function executable name
    :type exeName: str

    :param machineNames: list of machine names to to execute jobs on
    :type machineNames: list

    :param submit: fullpath to condor submit file
    :type submit: str

    :param error: fullpath to condor error file
    :type error: str

    :param output: fullpath to condor output file
    :type output: str

    :param log: fullpath to condor log file
    :type log: str

    :param dagman: pointer to created pycondor Dagman object
    :type dagman: pycondor.Dagman

    :param docker: flag to execute job using a docker container (default False), defaults to False
    :type docker: bool, optional

    :param docker_image: docker image for docker execution, defaults to 'wsuconnect/neuro'
    :type docker_image: str, optional

    :param docker_mount_if: docker share to mount (see credentials.json), defaults to None
    :type docker_mount_if: str, optional

    :param request_cpus: number of cpus to allocate to docker container, defaults to 1
    :type request_cpus: int, optional

    :param request_memory: memory in bytes to allocate to docker container, defaults to '5g'
    :type request_memory: str, optional

    :return: pointer to a configured pycondor Job object 
    :rtype: pycondor.Job
    """

    #create machine requirements string
    reqs = ''
    if machineNames:
        for c in range(len(machineNames)):
            if c > 0:
                reqs += ' || '
            reqs += 'Machine == "' + machineNames[c] + '"'
    extraLines = ['stream_output = True', 'RunAsOwner = True']

    #create job
    # print(os.path.join(REALPATH,'helper_functions',exeName))
    if not docker:
        job_out = Job(name=jobName, executable=os.path.join(REALPATH,'python3_venv','bin',exeName), submit=submit, error=error, output=output, log=log, dag=dagman, getenv=True, extra_lines=extraLines, requirements=reqs, universe='vanilla')
    else:
        extraLines.append('docker_image = ' + docker_image)
        if docker_mount_if == 'resshare19':
            extraLines.extend(["+MOUNT_RESSHARE19 = true", "+MOUNT_RESSHARE20 = false", "+MOUNT_RESSHARE21 = false"])
        elif docker_mount_if == 'resshare20':
            extraLines.extend(["+MOUNT_RESSHARE19 = false", "+MOUNT_RESSHARE20 = true", "+MOUNT_RESSHARE21 = false"])
        elif docker_mount_if == 'resshare21':
            extraLines.extend(["+MOUNT_RESSHARE19 = false", "+MOUNT_RESSHARE20 = false", "+MOUNT_RESSHARE21 = true"])

        job_out = Job(jobName, executable=os.path.join(REALPATH,'python3_venv',exeName), submit=submit, error=error, output=output, log=log, dag=dagman, getenv=False, extra_lines=extraLines, requirements=reqs, universe='docker',request_cpus=request_cpus,request_memory=request_memory)
    
    return job_out


    






