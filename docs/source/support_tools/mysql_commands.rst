
mysql_commands.py
===============

Data collected and produced for each project will follow `BIDS specifications <https://bids-specification.readthedocs.io/en/stable/>`__ to ensure community standards are upheld, to improve 
data integrity and conformity, and to improve data consistency and data processing optimization.


sql_multiple_query
------------------

.. py:function:: sql_multiple_query(*args,**kwargs)
    
    test

    :param database: Optional "kind" of ingredients.
    :param searchtable: REQUIRED
    :type database: string
    :type searchtable: string
    :raise lumache.InvalidKindError: If the kind is invalid.
    :return: The ingredients list.
    :rtype: list[str]

sql_query
---------


