
.. _flirt_json:

FLIRT JSON Control File
==============================================

FLIRT parameters can be found in “<project_identifier>_<input-datatype>_flirt_input.json” (see :numref:`input_data_types` for a list of 
available input data types). The available parameters are provided in :numref:`flirt_json_table`.

.. seealso:: 
  flirt.py also supports the execution of brain extraction, controlled through its own `JSON file <https://connect-tutorial.readthedocs.io/en/latest/project-specific_JSON_control_files/index.html#brain-extraction-bet>`__


**Sample FLIRT JSON control files**

* :download:`T1w <../_sample_docs/sample_struc_flirt_input.json>` (or available `here <https://connect-tutorial.readthedocs.io/en/latest/_downloads/deea14e11e9fd8c4bdd03b583289ef30/sample_struc_flirt_input.json>`__)
* :download:`ASL <../_sample_docs/sample_asl_flirt_input.json>` (or available `here <https://connect-tutorial.readthedocs.io/en/latest/_downloads/821452cbbc736702b5b4f252387be3a9/sample_asl_flirt_input.json>`__)
* :download:`3D APTw <../_sample_docs/sample_apt_flirt_input.json>` (or available `here <https://connect-tutorial.readthedocs.io/en/latest/_downloads/7fdc5c6fc48c2cff03a9b55bdf29ada9/sample_apt_flirt_input.json>`__)

.. _flirt_json_table:

.. list-table:: Available Keys in the FLIRT JSON control file.
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
   * - fslroi
     - OPTIONAL
     - boolean
     - perform fslroi to extract a single volume from input 4D image. Extracts the center volume unless the 'volume' key of the main_image_params
   * - bet
     - OPTIONAL
     - boolean
     - run brain extraction 
   * - inclusion_list
     - OPTIONAL
     - list[string]
     - list of strings for option search inclusion criteria
   * - exclusion_list
     - OPTIONAL
     - list[string]
     - list of strings for option search exclusion criteria
   * - main_image_params
     - OPTIONAL
     - dictionary
     - parameters as described in :numref:`FLIRT_main_image`
   * - reference_image_params
     - OPTIONAL
     - dictionary
     - parameters as described in :numref:`FLIRT_ref_image`
   * - flirt_params
     - REQUIRED
     - dictionary
     - FLIRT parameters as described in `Our FLIRT input Table <https://connect-tutorial.readthedocs.io/en/latest/project-specific_JSON_control_files/flirt_table.html>`__
   * - secondary_image_params
     - OPTIONAL
     - dictionary
     - parameters as described in :numref:`FLIRT_sec_image`
   * - standard_reference_params
     - OPTIONAL
     - dictionary
     - parameters as described in :numref:`FLIRT_std_image`

Required Input Image Parameters
-------------------------

**main_image_params** 

These keys are used to identify the main input image for registration.

.. _FLIRT_main_image:

.. list-table:: Main image input dictionary keys. 
   :widths: 30 15 15 40
   :header-rows: 1

   * - **Key Name**
     - **Required?**
     - **Data Type**
     - **Description**
   * - input_bids_labels
     - REQUIRED
     - dictionary
     - A bids filename dictionary as explained in **NEEDS REFERENCE**
   * - output_bids_location
     - REQUIRED
     - string
     - bids derivatives sub-folder (derivatives -> sub-XXX -> ses-YYY - > output_bids_location)
   * - output_matrix_base
     - REQUIRED
     - string
     - base element for the output registration matrix (highres in highres2standard.mat)
   * - output_bids_labels
     - REQUIRED
     - dictionary
     - A bids filename dictionary as explained in **NEEDS REFERENCE**
   * - output_json_values
     - REQUIRED
     - dictionary
     - Key-value pairs to additionally insert into the JSON sidecar accompanying input-to-reference transformed image
   * - volume
     - OPTIONAL
     - integer
     - volume to extract using fslroi. Must specify 'fslroi' as true

|
**reference_image_params** 

These keys are used to identify the reference image for registration.

.. _FLIRT_ref_image:

.. list-table:: Reference image input dictionary keys.
   :widths: 30 15 15 40
   :header-rows: 1

   * - **Key Name**
     - **Required?**
     - **Data Type**
     - **Description**
   * - type
     - REQUIRED
     - string
     - Type of reference: std or bids
   * - input_bids_location
     - OPTIONAL
     - string
     - Input bids location: rawdata or derivatives (required if type bids)
   * - input_bids_labels
     - OPTIONAL
     - dictionary
     - A bids filename dictionary as explained in **NEEDS REFERENCE** (required if type bids)
   * - output_bids_labels
     - OPTIONAL
     - dictionary
     - Supplemental bids filename dictionary as explained in **NEEDS REFERENCE** (required if type bids)
   * - output_matrix_base
     - OPTIONAL
     - string
     - base element for the output registration matrix (highres in highres2standard.mat) (required if type bids)
   * - output_json_values
     - OPTIONAL
     - dictionary
     - Supplemental key-value pairs to additionally insert into the JSON sidecar accompanying input-to-reference transformed image (required if type bids)
   
|
FLIRT Parameters
----------------

**flirt_params**

These parameters contains most of the inputs described in the nipype python extension manual for `FSL FLIRT 
<https://nipype.readthedocs.io/en/0.12.1/interfaces/generated/nipype.interfaces.fsl.preprocess.html#flirt>`__. See a table of our specific inputs :ref:`HERE 
<flirt_params_file>`.




Optional Parameters
-------------------

**secondary_image_params** 

These keys should be defined if the user would like to apply the registered output to a secondary image.

.. _FLIRT_sec_image:

.. list-table:: Secondary image input dictionary keys. 
   :widths: 30 15 15 40
   :header-rows: 1

   * - **Key Name**
     - **Required?**
     - **Data Type**
     - **Description**
   * - input_bids_labels
     - REQUIRED
     - dictionary
     - A bids filename dictionary as explained in **NEEDS REFERENCE**
   * - output_matrix_base
     - REQUIRED
     - string
     - base element for the output registration matrix
   * - output_bids_labels
     - REQUIRED
     - dictionary
     - Supplemental bids filename dictionary as explained in **NEEDS REFERENCE**

|
**standard_reference_params** 

These keys should be defined if the user would like to register input to a standard reference image (either )

.. _FLIRT_std_image:

.. list-table:: Standard reference image input dictionary keys.
   :widths: 30 15 15 40
   :header-rows: 1

   * - **Key Name**
     - **Required?**
     - **Data Type**
     - **Description**
   * - file
     - REQUIRED
     - string
     - Standard reference filename located within the FSL standard data directory
   * - type
     - REQUIRED
     - string
     - type of input file: FSL **CURRENTLY UNUSED**
   * - output_matrix_suffix
     - REQUIRED
     - string
     - suffix for the output registration matrix (standard in highres2standard.mat)
   * - output_bids_labels
     - REQUIRED
     - dictionary
     - Supplemental bids filename dictionary as explained in **NEEDS REFERENCE**
   * - output_json_values
     - REQUIRED
     - dictionary
     - Supplemental key-value pairs to additionally insert into the JSON sidecar accompanying input-to-standard transformed image

     