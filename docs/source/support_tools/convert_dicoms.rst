
.. _convert_dicoms_python:

convert_dicoms.py
===============


.. py:function:: convert_dicoms(source_singleDir, progress)
    
    This function converts sourcedata DICOM images (or any DICOM images in source_singleDir) to NIfTI images, and stores the output NIfTI (and JSON/TXT sidecars) in the parent folder.

    convert_dicoms(source_singleDIr, progress)

    :param source_singleDir: REQUIRED String or pathlike object of a directory containing DICOM images.
    :param progress: OPTIONAL operate in verbose mode (default False) 
    :type source_singleDir: str or None or Pathlike object
    :type progress: bool
    :raise Error: If path does not exist.
    :return: None
    :rtype: None


convert_dicoms.py also supports execution via command-line:

.. code-block:: shell-session

    $ ./convert_dicoms.py <source_singleDir> --progress