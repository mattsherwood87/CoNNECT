
.. _db_query:

Database Query
======================

The Project's MySQL tables can be queried a multitude of ways. It is important to be sure

**OPTIONAL** Update the Project's MySQL Database Tables prior to a query

The code below will update both searchTable and searchSourceTable.

.. code-block:: shell-session

    $ connect_neuro_db_update.py -p 2022-001 --progress 



Simple Query
------------

Simple queries can be performed using many of the default inputs.

.. code-block:: shell-session

    $ connect_neuro_db_query.py -p 2022-001 -r nii.gz

The above code will return the fullpath to any filenames containing 'nii.gz' in the Project's searchTable (project directories excluding sourcedata).


Simple Query - Modified Search Column
------------

It may be advantageous to search columns other than filename to refine the query results. This code performs the same search as simple query above, 
except now it will return the fullpath to any filename including the path contains 'nii.gz'.

.. code-block:: shell-session

    $ connect_neuro_db_query.py -p 2022-001 -r nii.gz -w fullpath


Simple Query - Additional Inclusionary Terms
------------

Additional inclusionary terms can help refine query results by allowing additional terms to identify data from particular subjects, sessions, runs, etc.

.. code-block:: shell-session

    $ connect_neuro_db_query.py -p 2022-001 -r nii.gz --opt-inclusion rawdata

This code performs the same search as simple query above, except now it will only return the fullpath to filenames that contain nii.gz AND rawdata. Since filenames
are not likely to have rawdata in the name, but rather the path, a better solution would be to search the fullpath column of the table:

.. code-block:: shell-session

    $ connect_neuro_db_query.py -p 2022-001 -r nii.gz --opt-inclusion rawdata -w fullpath


Simple Query - Multiple Inclusionary Terms
------------

Many inclusionary terms can be provided by supplying these terms to --opt-inclusion:

.. code-block:: shell-session

    $ connect_neuro_db_query.py -p 2022-001 -r nii.gz -w fullpath --opt-inclusion rawdata sub-001 

This code performs the same search as above except now it will only return the fullpath to filenames that contain nii.gz AND rawdata AND sub-001. 


Simple Query - Multiple Exclusionary Terms
------------

Similar to inclusionary search terms, many exclusionary terms can be provided by supplying these terms to --opt-exclusion:

.. code-block:: shell-session

    $ connect_neuro_db_query.py -p 2022-001 -r nii.gz -w fullpath --opt-inclusion rawdata sub-001 --opt-exlusion run-02 run-03

This code performs the same search as above except now it will only return the fullpath to filenames that contain nii.gz AND rawdata AND sub-001 AND do NOT contain run-02 OR run-03. 


Simple Query - searchSourceTable
------------

This code performs the same search as simple query above except utilizing the searchSourceTable to return fullpath to filenames in the Project's sourcedata directory containing nii.gz.

.. code-block:: shell-session

    $ connect_neuro_db_query.py -p 2022-001 -r nii.gz --source





