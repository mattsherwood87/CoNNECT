2.3.3.	Caution
---------------
It is critical in the submit description file that you specify the requirement to not operate on the neuro master machine “ip-10-100-30-11” to eliminate jobs from running on the master. Running jobs on the master will cause the master to become inoperable until the jobs finish, which is not ideal. Condor commands for the SGE-style method have been altered to include this requirement.
This is handled appropriately through the instance_ids.json file, which prescribes specific IP addresses of core machines to handle project-specific analyses. The jobs are restricted to run on only the machines specified in this file
