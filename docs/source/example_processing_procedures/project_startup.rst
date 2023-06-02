
.. _project_startup:

Project Startup
======================


#. Edit the credentials.json file located at /resshare/general_processing_code
  #. Add the 2022-001 to the "projects" key
  #. Create a new key titled 2022-001
  #. Add the elements in :numref:`credentials_secondary_table` to the 2022-001 dictionary


#. Create the Project's :ref:`scan ID JSON file <scan_id_json>` in the Project's **code** directory

#. Create the Project's MySQL tables

   .. code-block:: shell-session
    
    $ connect_create_project_db.py -p 2022-001

#. Create the Project's Scan ID JSON control file

   .. note::
      You may want to first collect a set of Pilot mri data and transmit to the CoNNECT NPC via PACS after you have
      completed the previous steps, then evaluate the JSON sidecar files in the sourcedata directory after DICOM conversion to select unique 
      key/value pairs for each NIfTI image. This DICOM-to-NIfTI conversion should be completed automatically upon data transfer as part of the 
      pacs-grabber service; however, creation of the BIDS-formatted rawdata will fail as this requires the Project's scan ID JSON file.




