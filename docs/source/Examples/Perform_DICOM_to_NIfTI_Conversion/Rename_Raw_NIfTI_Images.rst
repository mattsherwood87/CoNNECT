6.4.5.	Rename Raw NIfTI Images
DICOM conversion uses tags in the DICOM headers to create the filenames of the resultant NIfTI images. These can be long and hard to separate. The code below renames these raw files into a user-friendly format.
~$ kaas_cp_raw_nii.py -m -i /mnt/ss_rhb1/scratch/AFRL-Single_Exposure/raw_data/ --progress
NOTE: Requires *_scan_id.py and *_get_rawdcm_identifiers.py inside of the projects sub-directory of the project_specific_functions directory to describe how to extract subject and session identifiers from the raw dicom filepath.
