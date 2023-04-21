4.5.	Python Helper Functions
4.5.1.	asl_2d_flirt.py
Python helper function to perform registration between asl and structural images (and asl and standard images if structural registration results are found). This function operates under the following steps:
i.	Look for structural image on the AWS S3 bucket, and on local s3 and scratch directories
ii.	Confirm registration has not already been completed
iii.	Extract center volume of 4D ASL input data
iv.	Register center volume with structural image via FLIRT
v.	Compute inverse transform
vi.	Create registration overlay image using ASL center volume (example_asl2highres.png)
vii.	If structural to standard registration is found, complete the additional steps below
viii.	Concatenate ASL to structural registration with structural to standard to form ASL to standard registration
ix.	Compute inverse transform
x.	Apply transform to ASL center volume 
xi.	Create registration overlay image using ASL center volume (example_asl2standard.png)
4.5.2.	compute_cbf.py
Custom class to mimic nipype FSL interface for FSL’s oxford_asl. This function is not currently in the nipype interface. Command line arguments are placed in the classes ‘inputs’ subclass. The class has the function run() to run the resultant command line in the classes cmdline variable. Inputs align with the command line arguments that can be obtained via ‘oxford_asl --more'.
4.5.3.	convert_dicoms.py
Function to convert raw DICOM images to NIfTI format. Results will be placed in a subject/session specific directory within the project’s scratch directory. This will also copy any RDA, P-files, LOG, TXT, or DAT files that are also found in the raw DICOM directory. DICOM conversion is completed via dcm2niix using the nipype interface option for dcm2niix.
4.5.4.	create_fsl_condor_job.py
Function to create a condor job for FSL command line functions (those that are within $FSLDIR/bin).
4.5.5.	create_mysql_connection.py
Function to create a connection to the MySQL database on the master using pymysql python package.
4.5.6.	create_python_condor_job.py
Function to create a condor job for python commands in the /mnt/ss_rhb1/scratch/python directory.
4.5.7.	flirt_pngappend.py
Function to run pngappend to create registration overlay images typically produced from running FLIRT from packages like FEAT. 
4.5.8.	fsl_roi.py
Simple function to run fsl_roi command line argument.
4.5.9.	query_commands.py
This helper has several commands described briefly below.
i.	query_file
This function will return the local file path to a queried file. First, the AWS S3 bucket is searched for a specified file. If the file is found, then the local s3 synchronized mount is queried for the file’s existence and if it is not found, it will be downloaded if synchronize is provided as an option. If the file is not on the AWS S3 bucket, then the local scratch directory is queried for the file. If the file is found in any of these paths, the full local path to the file is returned. Otherwise, the resultant output is None.
ii.	sql_query_files
This function will return thea list of the full AWS S3 path to files matching the input search criteria.
iii.	sql_query_dir_check
This function will determine if the supplied AWS S3 directory contains any files. If the supplied directory is empty, the output will be False; otherwise it will return True.
iv.	sql_query_dirs
Function to query the MySQL table for files matching input search criteria and returns a list of the directories containing any matching files.
v.	sql_query
Function to query the mysql database/table and return a single column from the table. First, a connection to mysql using pymysql package is created then the MySQL table is queried and the desired column is output. The results are filtered via any inclusion and exclusion search characteristics and the remaining list is returned.
vi.	sql_mutiple_query
Same function as sql_query but will return multiple columns
4.5.10.	query_mod_time.py
Queries the localModTime from the AWS S3 Metadata for a specified file. If the mod time on the local disk is equivalent to that on the bucket, this function will return a value of None.
4.5.11.	struc_flirt.py
Python helper function to perform registration between structural and standard images. This function operates under the following steps:
i.	Perform BET if not skipped
ii.	Confirm registration has not already been completed
iii.	Register structural image with standard template via FLIRT
iv.	Compute inverse transform
v.	Create registration overlay image (highres2standard.png)
