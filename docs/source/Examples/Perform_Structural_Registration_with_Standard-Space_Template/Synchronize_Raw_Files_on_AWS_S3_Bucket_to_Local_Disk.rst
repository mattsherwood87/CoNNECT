Registration between structural and a standard-space template is critical for many analysis in order to transform all image spaces into a common standard template. The structural to standard registration will likely be concatenated to futher registrations as using this will likely reduce any registration errors than may be introduced in other low-resolution formats.
1.1.1.	(OPTIONAL) Synchronize Raw Files on AWS S3 Bucket to Local Disk
It may be necessary to synchronize the The following example command line input gives an example of synchronizing all of the raw data (including additional files in each directory containing at least one DICOM image). 
~$ kaas _syncs3.py -p single_exp -r AXIAL_T1.nii.gz --progress
NOTE: The search string ‘AXIAL_T1.nii.gz’ is identified in the single_exp_flirt_input.json file within the processing_scripts sub-directory of the project’s scratch directory.
