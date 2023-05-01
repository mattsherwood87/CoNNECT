
convert_dicoms.py
-----------------

Data collected and produced for each project will follow `BIDS specifications <https://bids-specification.readthedocs.io/en/stable/>`__ to ensure community standards are upheld, to improve 
data integrity and conformity, and to improve data consistency and data processing optimization.



.. py:function:: convert_dicoms.py(source_singleDir, progress)
    
    test

    :param source_singleDir: REQUIRED String or pathlike object of a directory containing DICOM images.
    :param progress: OPTIONAL operate in verbose mode (default False) 
    :type source_singleDir: str or None or Pathlike object
    :type progress: bool
    :raise Error: If path does not exist.
    :return: None
    :rtype: None