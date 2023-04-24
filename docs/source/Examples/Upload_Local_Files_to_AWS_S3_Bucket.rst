6.3.	Upload Local Files to AWS S3 Bucket
Uploading data from the local disk to the s3 bucket is simple with kaas_s3_upload.py. To upload a single file to the s3 bucket, use the following:
~$ kaas_s3_upload.py -p single_exp -f /local/path/to/file
In the above example, the local filepath MUST be in the scratch directory, and the scratch directory portion of the string (“/mnt/ss_rhb1/scratch”) is replaced by the s3 bucket name (i.e., kbrcloud-mri-general). The program will also copy the file to the local synchronized s3 directory (i.e., /mnt/ss_rhb1/s3-mri-general/path/to/file). If you wish to not copy the file, please include the --skip-copy argument:
~$ kaas_s3_upload.py -p single_exp -f /local/path/to/file --skip-copy

To upload a file from a different directory, please specify the output directory to skip the replacement. Notice in this case, you must know the name of the AWS S3 bucket, therefore it is not advantageous to use this method. Also, the file(s) will not be copied to the local synchronized s3 directory. NOTE: the output directories will be created on the AWS S3 bucket if they do not exist.
~$ kaas_s3_upload.py -p single_exp -f /local/path/to/file -o kbrcloud-mri-general/path/to/output/dir
It may be advantageous to upload files from a directory (and all subdirectories). If this is desired, use the following example: 
~$ kaas_s3_upload.py -p single_exp --dir /local/path/to/dir
All files will, by default, be copied to the local synchronized s3 directory. If desired, you can specify the output directory if needed. You may also specify multiple files or directories returned from a query. Using the last example in Section 4.2, you would do the following:
~$ kaas_s3_upload.py -p single_exp -f $results
Or by specifying each file separately using a space-delimited list:
~$ kaas_s3_upload.py -p single_exp -f /local/path/to/file1 /local/path/to/file2
The above commands can be modified to include flags to show the version (-v | --version) and progress (--progress) to print additional information to the command window (or for logging).
