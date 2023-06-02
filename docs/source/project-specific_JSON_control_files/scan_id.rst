
.. _scan_id_json:

Scan Identification JSON Control File
======================

Scan Identification parameters can be found in “<project_identifier>_scan_id.json". This file contains the inputs described in :numref:`scan_id_json_table` and :numref:`sequence_dict_items`

**Sample scan_id JSON file**

* :download:`**Sample scan_id JSON file** <../_sample_docs/sample_T1w_bet_input.json>`


.. _scan_id_json_table:

.. list-table:: Available Keys in the scan identification JSON file.
    :widths: 30 15 15 40
    :header-rows: 1

    * - **Key Name**
      - **Required?**
      - **Data Type**
      - **Description**
    * - ``__general_comment__``
      - OPTIONAL
      - string
      - free text to provide a brief description
    * - <sequence1_unique_name>
      - REQUIRED
      - dictionary
      - scan identification parameters for sequence 1
    * - <sequence2_unique_name>
      - REQUIRED
      - dictionary
      - scan identification parameters for sequence 2
    * - <sequenceN_unique_name>
      - REQUIRED
      - dictionary
      - scan identification parameters for sequence N


|

**Sequence Identification Parameters**

.. _sequence_dict_items:

.. list-table:: Description of the keys in the sequence dictionaries.
    :widths: 30 15 15 40
    :header-rows: 1

    * - **Key Name**
      - **Required Level**
      - **Data Type**
      - **Description**
    * - json_header
      - REQUIRED
      - dictionary
      - Search criteria to identify NIfTI images unique to this sequence. See :numref:`json_search_keys`
    * - bids_labels
      - REQUIRED
      - dictionary
      - A bids filename dictionary as explained in **NEEDS REFERENCE**, **EXCLUDING** extension key
    * - BidsDir
      - Required
      - string
      - BIDS rawdata sub-directory to move the NIfTI image and associated files

|

**json_header search keys**

Common MRI metadata fields can be found in the `BIDS online specification <https://bids-specification.readthedocs.io/en/stable/04-modality-specific-files/01-magnetic-resonance-imaging-data.html#common-metadata-fields>`__.
The specified metadata fields can be used as keys in the json_header dictionary to identify this sequence from the other acquired 
images as inclusionary criteria. These key-value pairs will be compared to the JSON sidecar accompanying the source NIfTI image 
that is created following dicom-to-nifti conversion completed either in connect_pacs_dicom_grabber or connect_dcm2nii. The values 
can either be an integer, string, or list[string].

.. note:: Exclusion criteria can be defined by preceding the keys below with "Not" (e.g., "NotProtocolName").