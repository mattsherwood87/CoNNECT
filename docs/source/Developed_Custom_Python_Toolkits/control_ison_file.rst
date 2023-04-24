There are many custom toolkits that have been developed to provide broad processing capabilities across projects, MRI scanners, imaging parameters, and processing specifications. 
These toolkits utilize a common JSON architecture to describe such parameters. Some of these JSON files solely describe input parameters for processing functions while others detail
custom inputs, and others are a combination of these. 

Each JSON file is detailed in the python functions described below.


Project Credentials File
------------------------

A single JSON file describes various parameters for each project/program. This file is ‘credentials.json’ and is located in the main code directory on the mounted centralized storage (/resshare/general_processing_codes). 
The main structure of JSON files are the definition of keys associated values. The keys serve as a search tool to gain access to the value it contains within python or other programming languages.
In general, the values for each key can be Booleans, strings, integers or floats, lists, or arrays. The table below outlines the keys and their associated descriptions for a project in the credentials file. Each project in the
credentials file should be defined as their own key titled by their respective protocol number prescribed by their IRB of record. For pilot studies, a short name may be used in place of the IRB number.

.. _credentials_table:

.. list-table:: Key descriptions for the credentials.json file.
   :widths: 25 50 25
   :header-rows: 1

   * - **Key**
     - **Description**
   * - description
     - Text used to give a short description of the project
   * - title
     - Full project title
   * - database
     - MySQL database for the associated main and source tables described in :doc:`the MySQL section of this document </cluster_computing/MySQL_database.rst>`
   * - dataDir
     - Local directory within the mounted centralized storage's 'projects' folder where data shall be located.
   * - dicom_id
     - Unique string within the DICOM filenames to help identify DICOMS within the PACS and souredata directories
