#!/resshare/general_processing_codes/python3_venv/bin/python
# the command above ^^^ sets python 3.10.10 as the interpreter for this program

# Created by Matthew Sherwood (matt.sherwood@wright.edu, matthew.sherwood.7.ctr@us.af.mil)
# Created on 16 Sept 2021
#
# v2.0.0 on 1 April 2023 - simplify code

import os

def get_bids_filename(*args, **kwargs):
    """
    return bids compliant filename from input labels

    get_bids_filename(subject=SUBJECT,session=SESSION,task=TASK,acquisition=ACQUISITION,run=RUN,process=PROCESS,resolution=RESOLUTION,space=SPACE,description=DESCRIPTION,suffix=SUFFIX,extension=EXTENSION)

    Args:
        subject (str): subject identifier

        session (str): session identifier

        task (str): task identifier

        acquisition (str): acquisition identifier

        run (str): run identifier

        process (str): process

        resolution (str): resolution

        space (str): space

        description (str): description

        suffix (str): scan suffix

        extension (str): extension


    Returns:
        str: BIDS-compliant filename
    """
    sub = kwargs.get('subject',None)
    ses = kwargs.get('session',None)
    acq = kwargs.get('acquisition',None)
    task = kwargs.get('task',None)
    dir = kwargs.get('direction',None)
    run = kwargs.get('run',None)
    proc = kwargs.get('process',None)
    res = kwargs.get('resolution',None)
    space = kwargs.get('space',None)
    desc = kwargs.get('description',None)
    suffix = kwargs.get('suffix',None)
    ext = kwargs.get('extension',None)

    filename = str()
    if sub:
        filename = 'sub-' + sub

    for k in ['ses','acq','task','dir','run','proc','res','space','desc']:
        if eval(k) is not None:
            filename = filename + '_' + k + '-' + eval(k)

    if suffix is not None:
        filename = filename + '_' + suffix

    if ext is not None:
        filename = filename + '.' + ext

    return filename


def get_bids_labels(IN_FILE):
    """
    Get bids compliant filename labels from a file

    get_bids_labels(IN_FILE)

    Args:
        IN_FILE (str): fullepath to a BIDS-compliant file

    Returns:
        dict: bids filename labels
    """

    labels = {}
    
    filename = os.path.basename(IN_FILE)

    #see if there is an extension
    idx = filename.find('.')
    if idx != -1:
        baseFilename = filename[:idx]
        labels['extension'] = filename[idx+1:]
    else:
        baseFilename = filename
        labels['extension'] = None


    d = {'acq':'acquisition', 'task':'task', 'dir':'direction', 'run':'run', 'proc':'process','res':'resolution','space':'space','desc':'description'}
    for k in ['task','acq','run','proc','res','space','desc']:
        if k + '-' in baseFilename:
            labels[d[k]] = baseFilename.split(k + '-')[1].split('_')[0]

    #get last item, suffix
    labels['suffix'] = baseFilename.split('_')[-1]

    return labels