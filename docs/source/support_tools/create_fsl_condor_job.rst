
create_fsl_condor_job.py
===============

.. py:function:: create_fsl_condor_job(inDir, basename)
    
    Creates an HTCondor job for FSL commands.

    create_fsl_condor_job(jobName, exeName, machineNames, submit, error, output, log, dagman)

    :param jobName: Required name for the parallel htcondor job
    :param exeName: FSL executable name
    :param machineNames: list of machine names to execute jobs
    :param submit: fullpath to output submit file
    :param error: fullpath to output submit file
    :param output: fullpath to output submit file
    :param log: fullpath to output submit file
    :param dagman: Pycondor Dagman object
    :type jobName: str
    :type exeName: str
    :type machineNames: list[str]
    :type submit: str
    :type error: str
    :type output: str
    :type log: str
    :type dagman: str
    :raise Error: any encountered error
    :return: pycondor Job object
    :rtype: pycondor.Job