
bids_commands.py
===============

get_bids_filename
------------------

.. py:function:: get_bids_filename(*args, **kwargs)
    
    Create a BIDS-compliant filename from the specified options.

    get_scan_id(subject=SUBJECT, session=SESSION, task=TASK, acquisition=ACQUISITION, run=RUN, process=PROCESS, resolution=RESOLUTION, space=SPACE, description=DESCRIPTION, suffix=SUFFIX, extension=EXTENSION)

    :param subject: Optional subject identifier
    :param session: Optional session identifier
    :param task: Optional BIDS description (task-ABC)
    :param acquisition: BIDS description (acq-ABC)
    :param run: Optional BIDS description (run-ABC)
    :param process: Optional BIDS description (proc-ABC)
    :param resolution: Optional BIDS description (res-ABC)
    :param space: Optional BIDS description (space-ABC)
    :param description: Optional BIDS description (desc-ABC)
    :param suffix: Optional BIDS suffix
    :param extension: Optional filename extension (do not begin with '.')
    :type subject: str
    :type session: str
    :type task: str
    :type acquisition: str
    :type run: str
    :type process: str
    :type resolution: str
    :type space: str
    :type description: str
    :type suffix: str
    :type extension: str
    :raise Error: Any error occurs.
    :return: BIDS compliant filename string
    :rtype: str


get_bids_labels
------------------

.. py:function:: get_bids_labels(IN_FILE)
    
    Get BIDS-compliant labels from specified filename

    get_bids_labels(IN_FILE)

    :param IN_FILE: Required fullpath or filename
    :type IN_FILE: str
    :raise Error: Any error occurs.
    :return: Dictionary containing extracted BIDS labels 
    :rtype: dict