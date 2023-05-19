
get_scan_id.py
===============

.. py:function:: get_scan_id(inDir, basename)
    
    Get metadata from a sourcedata NIfTI file using the Project's scan_id JSON file within the Project's 'code' directory.

    get_scan_id(inDir, basename)

    :param inDir: Required fullpath to sourcedata sub-directory containing NIfTI file
    :param basename: Required basename of the sourcedata NIfTI file
    :type inDir: str
    :type basename: str
    :raise Error: Any error occurs.
    :return: scan name, bids directory as identified in the Project's scan_id JSON file within the Project's 'code' directory
    :rtype: str, str