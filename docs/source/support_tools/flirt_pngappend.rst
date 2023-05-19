
flirt_pngappend.py
========


.. py:function:: flirt_pngappend(IN_FILE,REF_FILE,OUT_FILE)
    
    Creates a registration overlay image (PNG). This tool is utilized by :doc:`flirt.py <flirt.rst>`.

    Top row contains a background image of IN_FILE in REF_FILE space overlaid with the edges of REF_FILE (in red).
    Bottom row contains a background image of REF_FILE overlaid with the edges of IN_FILE in REF_FILE space (in red).

    flirt_pngappend(IN_FILE, IN_FILE, OUT_FILE)

    :param IN_FILE: REQUIRED String or pathlike object to an input NIfTI file transformed to the space of REF_FILE.
    :param REF_FILE: REQUIRED String or pathlike object to a reference NIfTI file.
    :param OUT_FILE: REQUIRED String or pathlike object to the output PNG file that will be created
    :type IN_FILE: str or None or Pathlike object
    :type REF_FILE: str or None or Pathlike object
    :type OUT_FILE: str or None or Pathlike object
    :raise Error: If any error occurs.
    :return: None
    :rtype: None

