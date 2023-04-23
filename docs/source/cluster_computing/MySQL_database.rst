MySQL Database
**************

A CoNNECT MySQL database has been implemented on the master to index files in each project's directory. These databases and tools 
therein are local to only the master and, thus, core nodes do not have the ability to query or update. Different tables must be established
for each independent project.

MySQL can be accessed through the command line:

.. code-block:: bash
   mysql --login-path=client 
   
Each project will have two tables: one main table containing all files except source files and one source table containing files within 
the BIDS sourcedata directory. The main table (referred to in the project's credentials as searchTable) contains the elements described 
in :numref: `mysql_data_table`. The sourcedata table contains the elements described in :numref: `mysql_sourcedata_table`. 

MySQL allows efficent queries of files contained within a project's directories. This will optimize file searching and data processing.
Any ‘-‘ are illegal characters in the table name and are generally replaced with an underscore (‘_’).

.. _mysql_data_table:
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

.. _mysql_sourcedata_table:
.. list-table:: The main database for each project <searchSourceTable>.
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