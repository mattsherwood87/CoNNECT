2.3.	HTCondor Clustering
-------------------------
The system is comprised of the following list of hardware components. Details of each component are supplied.
2.3.1.	Introduction
Condor is a clustering software developed by the University of Wisconsin. Condor allows jobs to be submitted using a submit description file. Details on a submit description file can be found at:
https://research.cs.wisc.edu/htcondor/manual/v7.7/condor_submit.html#:~:text=The%20submit%20description%20file%20is%20the%20only%20command%2Dline%20argument,at%20least%20one%20queue%20command.
Condor also allows jobs to be submitted using a SGE-style method through condor_qsub. This function has been slightly modified to restrict execution from occurring on the master by adding the IP address to the requirements list.
2.3.2.	Condor Setup on the Master
HTCondor has already been setup on the neuro master and each core node. However, the link between the master and the cores are established via IP addresses. If the master IP address changes, it is critical to modify the setup files on the master as well as the cores to point to the new IP address of the master. The instructions below specify how to adapt HTCondor to the new IP address.
i.	Open 00debconf from the condor configuration directory
sudo nano /etc/condor/config.d/00debconf
ii.	Modify the master IP address
The IP address for the master is the only full ip address in line 23 that begins with “ALLOW_NEGOTIATOR”. The IP address appears after “127.*,”.
