6.4.1.	Synchronize Raw Files on AWS S3 Bucket to Local Disk
The following example command line input gives an example of synchronizing all of the raw data (including additional files in each directory containing at least one DICOM image). 
~$ kaas _syncs3.py -p single_exp -r IMA --progress --raw  -a
