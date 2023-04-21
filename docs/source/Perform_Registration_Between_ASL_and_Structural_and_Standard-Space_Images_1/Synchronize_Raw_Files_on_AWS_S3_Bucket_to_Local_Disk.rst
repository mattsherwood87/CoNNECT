6.6.	Perform Registration Between ASL and Structural and Standard-Space Images
Registration between ASL and structural/standard-space templates are critical for group analyses.
1.1.1.	Synchronize Raw Files on AWS S3 Bucket to Local Disk
It may be necessary to synchronize the The following example command line input gives an example of synchronizing all of the raw data (including additional files in each directory containing at least one DICOM image). 
~$ kaas _syncs3.py -p single_exp -r ASL_RESTING.nii.gz --progress
NOTE: The search string ‘ASL_RESTING.nii.gz’ is identified in the single_exp_flirt_input.json file within the processing_scripts sub-directory of the project’s scratch directory.
