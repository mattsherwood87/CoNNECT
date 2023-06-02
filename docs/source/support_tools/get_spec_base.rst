.. _get_spec_base_python:

get_spec_base.py
===============

.. py:function:: get_spec_base(inDir, basename)
    
    Get metadata from a MRS file.
    
    This program returns the Project credentials into the custom specBase class (**NEEDS REFERENCE**), which should be imported prior to calling get_spec_base().

    get_spec_base(specFile)

    :param specFile: Required path to a MRS file
    :type specFile: str
    :raise Error: Any error occurs
    :return: None
    :rtype: None