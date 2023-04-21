6.2.	Query a Database/Table
The mysql databases and accompanying tables can be queried using kaas_neuro_db_query.py. These databases ONLY contain information on files in the s3 bucket specified. Furthermore, the databases are only updated daily so recent changes to the bucket require an update prior to query if you wish you have these changes appear in the query (see Section 4.1). The commands below demonstrate various uses of the function.
To perform a simple query of NIfTI files on the AFRL-Single_Exposure table:
~$ kaas_neuro_db_query.py -r nii.gz -p single_exp 
The above command will search for the text “nii.gz” appearing anywhere in the filename. To restrict this search to files with the extension nii.gz, include the where (-w | --where) option to search the extension column:
~$ kaas_neuro_db_query.py -r nii.gz -p single_exp -w extension
To further restrict the search criteria, you may want to limit results to appear in specific directories, such as “processed_data”:
~$ kaas_neuro_db_query.py -r nii.gz -p single_exp -w extension --opt-inclusion processed_data
To further restrict the search criteria, you may want to limit results to contain additional search text such as a scan type (i.e., flair):
~$ kaas_neuro_db_query.py -r nii.gz -p single_exp -w extension --opt-inclusion processed_data flair
You may add as many additional search refinements as you wish, just space-delimit the inputs to --opt-inclusion and --opt-exclusion. Finally, you may want to exclude results containing specific text such as std or highres:
~$ kaas_neuro_db_query.py -r nii.gz -p single_exp -w extension --opt-inclusion processed_data flair --opt-exclusion std highres
The above commands can be modified to include flags to show the version (-v | --version) and progress (--progress), as well as commands to synchronize the results to the local drive. The above examples print the results to the command line; however, storing these to a command-line variable may also be advantageous. This can be done through the following commands to save and print the results:
~$ results=$(kaas_neuro_db_query.py -r nii.gz -p single_exp -w extension --opt-inclusion processed_data flair --opt-exclusion std highres)
~$ echo $results
Or to print the results in a little easier to read format, replace spaces with new lines:
~$ echo $results | tr ‘ ‘ ‘\n’
