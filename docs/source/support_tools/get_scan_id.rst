
get_scan_id.py
===============

Data collected and produced for each project will follow `BIDS specifications <https://bids-specification.readthedocs.io/en/stable/>`__ to ensure community standards are upheld, to improve 
data integrity and conformity, and to improve data consistency and data processing optimization.



.. py:function:: get_scan_id.py(inDir, basename)

    test

   :param kind: Optional "kind" of ingredients.
   :type kind: list[str] or None
   :raise lumache.InvalidKindError: If the kind is invalid.
   :return: The ingredients list.
   :rtype: list[str]