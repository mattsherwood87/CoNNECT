:topic: Project-Specific JSON Control Files

***********************************
Project-Specific JSON Control Files
***********************************

.. toctree:: 
  :hidden:
  :titlesonly:

  brain_extraction
  flirt


The CoNNECT custom developed support tools utilize JSON control files from each project's **CODE** bids directory. The files are named as <project_identifier>_<data_type>_<process>_input.json. 
Data types are specified in :numref:`input_data_types` and available processes are flirt and bet. 


.. _input_data_types:

.. list-table:: Data types.
   :widths: 25 75
   :header-rows: 1

   * - **Data Type**
     - **Source Image Description**
   * - struc
     - T1-weighted image
   * - asl
     - arterial spin labeling or cerebral blood flow image
   * - apt
     - amide proton transfer-weighted source or MTRasym image
   * - flair
     - T2 FLAIR image
   * - T2
     - T2 or T2* image




.. include:: brain_extraction.rst
.. include:: flirt.rst

