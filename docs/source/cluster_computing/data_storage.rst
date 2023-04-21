2.4.	Data Storage
2.4.1.	File Share
A file share has been created in /mnt/ss_rhb1. Any documents or directories created here will be backed up daily but will also be available on the master and any core nodes.
NOTE: processing should be conducted in the /mnt/ss_rhb1/scratch directory. The processed files should be uploaded to the s3 bucket and removed following the completion of the processing.
2.4.2.	AWS S3 Buckets
The kbrcloud AWS S3 buckets are mounted at /mnt/ss_rhb1. Currently, the only bucket accessible is kbrcloud-mri-general mounted at /mnt/ss_rhb1/s3-mri-general. 
NOTE: This directory needs to be synchronized with aws manually. This is quite time-consuming, but more robust, custom synchronization tools have been developed. Tools have also been developed to upload files and directories to the AWS S3 bucket.
Each funding source/contract identifier and/or cost list will have a different AWS S3 bucket. For ease of use, it would be preferential to have a common directory structure across the AWS S3 buckets (Figure 2). If applied, the general structure laid out in this document will aid the development of more broad processing programs.
The raw data folder should contain subject-specific directories containing raw DICOM images (or equivalent) scans and any other behavioral data. This directory should also contain raw dicom files converted to NIfTI. The dcm2niix tool should be used for conversions (https://www.nitrc.org/plugins/mwiki/index.php/dcm2nii:MainPage).
