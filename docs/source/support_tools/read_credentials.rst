
.. _read_creds_python:

read_credentials.py
===============

Data collected and produced for each project will follow `BIDS specifications <https://bids-specification.readthedocs.io/en/stable/>`__ to ensure community standards are upheld, to improve 
data integrity and conformity, and to improve data consistency and data processing optimization. 

|

A single JSON file describes various parameters for each project/program. This file is ‘credentials.json’ and is located in the main code directory on the mounted centralized storage 
(/resshare/general_processing_codes). The table below outlines the keys and their associated descriptions for a project in the credentials file. Each project in the credentials file 
should be defined as their own key titled by their respective protocol number prescribed by their IRB of record. For pilot studies, a short name may be used in place of the IRB number.

.. _credentials_main_table:

.. list-table:: Key descriptions for the credentials.json file.
   :widths: 25 15 50
   :header-rows: 1

   * - **Key**
     - **Data Type**
     - **Description**
   * - projects
     - list[string]
     - List of all project identifiers (these are referred to as <project_identifier>)
   * - <project_identifier>
     - dictionary
     - Dictionary identifying key elements of each project described in :numref:`credentials_secondary_table`

|

.. _credentials_secondary_table:

.. list-table:: Dictionary keys for the <project_identifier> elements.
   :widths: 25 15 50
   :header-rows: 1

   * - **Key**
     - **Data Type**
     - **Description**
   * - description
     - string
     - Text used to give a short description of the project
   * - title
     - string
     - Full project title
   * - database
     - string
     - MySQL database for the associated main and source tables described in :ref:`the MySQL section of this document <mysql_db>`
   * - dataDir
     - string
     - Local directory within the mounted centralized storage's 'projects' folder where data shall be located.
   * - dicom_id
     - string
     - Unique string within the DICOM filenames to help identify DICOMS within the PACS and souredata directories
   * - searchSourceTable
     - string
     - MySQL table identifying files within the project's sourcedata directory
   * - searchTable
     - string
     - MySQL table identifying files within the project's directory (excluding sourcedata)

|
.. py:function:: read_credentials(inDir, basename)
    
    Read the credential file (credentials.json) from the general_processing_codes directory.

    This program returns the Project credentials into the custom creds class (**NEEDS REFERENCE**), which should be imported prior to calling read_credentials()

    read_credentials(project)

    :param project: <project_identifier>. This should correspond to the projects IRB protocol number.
    :type project: string
    :raise Error: if credentials.json is not found
    :return: None
    :rtype: None

