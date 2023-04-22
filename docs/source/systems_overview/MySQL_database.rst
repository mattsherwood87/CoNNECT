MySQL Database
--------------


MySQL databases will be maintained on the master to index files in the AWS S3 buckets. A database will exist for each AWS S3 bucket. These databases and tools therein are local to only the master and, thus, core nodes do not have the ability to query or update. Different tables for independent projects within the same funding source exist in the database.
MySQL can be accessed through the command line “mysql --login-path=client”. Each table contains the elements describe in Table 1 (except raw file tables which only contain the fullpath and filename elements), which can be queried very quickly. This will optimize file searching, AWS S3 synchronization, and data processing.
Table 1. List of the columns (including descriptions) for the tables in each mysql database. Each project (level 3 or 2 in Figure 2) will have its own table in the bucket’s database.
Currently, there is one database for the kbrcloud-mri-general AWS S3 bucket. That database, s3_mri_general, contains tables for the projects described in Table 2. Any ‘-‘ are illegal characters and generally replaced with an underscore (‘_’).

.. list-table:: The main database for each project <searchTable>.
   :widths: 25 25 50
   :header-rows: 1

   * - Column Heading
     - Column Description
     - Char Size
   * - fullpath
     - Full path to the local file, including filename and extension
     - 255
   * - filename
     - Filename and extension, excluding the path
     - 255
   * - basename
     - Filename, excluding extension and path. NULL if no basename
     - 255
   * - extension
     - Extension, excluding filename and path. NULL if no extension
     - 255