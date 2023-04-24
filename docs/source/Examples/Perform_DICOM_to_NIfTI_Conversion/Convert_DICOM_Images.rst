6.4.3.	Convert DICOM Images
The following example command line details an example of converting DICOM images to NIfTI. 
~$ kaas_dcm2nii.py -p single_exp -s --progress
Table 24. Description of kaas_dcm2nii.py arguments in the example.
NOTE: The “-s” option should only be supplied with the above option or when additional core resources are already active (i.e., in the event of a large number requiring conversion). To skip this, simply do NOT include the “-s” flag. 
NOTE: The resultant NIfTI files will be output into a “raw_data” directory within the project’s scratch directory.
NOTE: Requires *_get_dir_identifiers.py inside of the projects sub-directory of the project_specific_functions directory to describe how to extract subject and session identifiers from the raw dicom filepath
