6.7.	Quantify Cerebral Perfusion
---------------------------------
Quantified cerebral perfusion (CBF) from ASL sequences may or may not be performed directly on the scanner. It may be desirable to perform quantification offline in either case. The following steps outline the procedures to quantify cerebral perfusion from either 2D or 3D ASL (pASL or pcASL).
1.1.1.	Synchronize Raw Files on AWS S3 Bucket to Local Disk
------------------------------------------------------------
It may be necessary to synchronize the The following example command line input gives an example of synchronizing all of the raw data (including additional files in each directory containing at least one DICOM image). 
~$ kaas _syncs3.py -p single_exp -r ASL_RESTING.nii.gz --progress
NOTE: The search string ‘ASL_RESTING.nii.gz’ is identified in the single_exp_flirt_input.json file within the processing_scripts sub-directory of the project’s scratch directory.
