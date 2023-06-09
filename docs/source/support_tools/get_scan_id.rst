
.. _get_scan_id_python:

get_scan_id.py
===============

This function is currently used by :ref:`connect_create_raw_nii.py <connect_create_raw_nii_python>`.

.. py:function:: get_scan_id(inDir, basename)
    
    Search the metadata accompanying a sourcedata NIfTI file (found in the accompanying JSON sidecar) using the Project's scan_id JSON file
    within the Project's 'code' directory (found :ref:`Scan Identification`).

    get_scan_id(inDir, basename)

    :param inDir: Required fullpath to sourcedata sub-directory containing NIfTI file
    :param basename: Required basename of the sourcedata NIfTI file
    :type inDir: str
    :type basename: str
    :raise Error: Any error occurs.
    :return: scan name created from get_bids_filename found in bids_commands.py, bids directory as identified in the Project's scan_id JSON file within the Project's 'code' directory
    :rtype: str, str