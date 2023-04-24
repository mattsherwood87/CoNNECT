6.6.4.	Upload Results to AWS S3 Bucket
It is desirable to maintain the files on the AWS S3 bucket. These files will be used for all future processing. The following describes the function to upload the results of the above step:
~$ kaas_s3_upload.py -p single_exp --dir /mnt/ss_rhb1/scratch/AFRL-Single_Exposure/processed_data --progress
NOTE: This function will also copy the files to the local s3 synchronized directory to eliminate the need for future downloads from the AWS S3 bucket. This can be bypassed with the option --skip-copy.
