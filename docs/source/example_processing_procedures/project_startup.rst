
.. _project_startup:

Project Startup
======================

Modify credentials JSON control file
------------------------------------

Edit the credentials.json file located at /resshare/general_processing_code

#. Add 2022-001 to the "projects" key
#. Create a new key titled 2022-001
#. Add the elements from `Dictionary keys for the <project_identifier> elements <https://connect-tutorial.readthedocs.io/en/latest/support_tools/index.html#read-credentials-py>`_ to the 2022-001 dictionary


Create MySQL tables
-------------

Create the Project's MySQL tables

.. code-block:: shell-session
  
  $ connect_create_project_db.py -p 2022-001


Create a scan ID JSON control file
-----------------------------------

Create the Project's :ref:`scan ID JSON file <scan_id_json>` in the Project's **code** directory

   .. note::
      You may want to first collect a set of Pilot mri data and transmit to the CoNNECT NPC via PACS after you have
      completed the previous steps, then evaluate the JSON sidecar files in the sourcedata directory after DICOM conversion to select unique 
      key/value pairs for each NIfTI image. This DICOM-to-NIfTI conversion should be completed automatically upon data transfer as part of the 
      pacs-grabber service; however, creation of the BIDS-formatted rawdata will fail as this requires the Project's scan ID JSON file.





