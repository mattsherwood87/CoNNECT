
Data Management
===============

Centralized Storage
-------------------

Centralized storage has been made available.


File Share
----------

A file share has been created in /resshare. Any documents or directories created here will be backed up daily but will also be 
available on the master and any core nodes.


Data Organization
-----------------

Data collected and produced for each project will follow `BIDS specifications <https://bids-specification.readthedocs.io/en/stable/>`__ to ensure community standards are upheld, to improve 
data integrity and conformity, and to improve data consistency and data processing optimization.

.. note:: Insert BIDS overview, etc including filename structure table here


For example, bids format should follow this structure:
_sub-_ses-_acq-_run-_task-_desc-_.ext


.. _get_bids_filename_table:

.. list-table:: Available Keys for compliant get_bids_filename from input labels. 
   :widths: 30 15 55
   :header-rows: 1

   * - **Entity**
     - **Label Prefix**
     - **Description**
   * - task
     - task
     - A set of structured activities performed by the participant. No two tasks should have the same name.
   * - acquisition
     - acq
     - Data acquisition is a continuous uninterupted block of time during which the MRI was acquiring data.
   * - run
     - run
     - An uniterupted repition that has the same acquisition parameters and task.
   * - process
     - proc
     - Name of process that generated the outputs.
   * - resolution
     - res
     - The acq-<label> entity cooresponds to a custom label the user may use to distinguish a different set of parameters used for acquiring the same modality. 
       For example <acq-highres> or <acq-lowres>.
   * - space
     - space
     - Useful for describing the source of tranforms from an input image to a target space.
   * - description
     - desc
     - Describing acronyms within labeling code.
   * - suffix
     - NA
     - A filename consists of a chain of entity instances and a suffix all separated by underscores, and an extension.
   * - extension
     - ext
     - The extension depends on the inaging modality and the data format, and can convey further details of the file's content.
     



