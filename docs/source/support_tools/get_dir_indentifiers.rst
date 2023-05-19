
get_dir_indentifiers.py
===============


.. py:function:: get_dir_indentifiers(singleDir)
    
    Get subject and session identifiers from a BIDS filepath

    get_dir_identifiers(singleDir)

    :param singleDir: Required BIDS-compliant filepath
    :type kind: str
    :raise Error: Any error occurs
    :return: subject identifier (XXX in sub-XXX), session identifier (YYY in ses-YYY)
    :rtype: str, str