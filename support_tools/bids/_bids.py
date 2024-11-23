# functions.py
# the command above ^^^ sets python 3.10.10 as the interpreter for this program

# Created by Matthew Sherwood (matt.sherwood@wright.edu, matthew.sherwood.7.ctr@us.af.mil)
# Created on 16 Sept 2021
#
# v2.0.0 on 1 April 2023 - simplify code

import os as _os

def get_bids_filename(subject: str=None, session: str=None, acquisition: str=None, task: str=None, direction: str=None, run: str=None, process: str=None, resolution: str=None, space: str=None, description: str=None, suffix: str=None, extension: str=None) -> str:
    """
    return bids compliant filename from input labels

    get_bids_filename(subject=SUBJECT,session=SESSION,acquisition=ACQUISITION,task=TASK,direction=DIRECTION,run=RUN,process=PROCESS,resolution=RESOLUTION,space=SPACE,description=DESCRIPTION,suffix=SUFFIX,extension=EXTENSION)

    :param subject: subject identifier, defaults to None
    :type subject: str, optional

    :param session: session identifier, defaults to None
    :type session: str, optional

    :param acquisition: acquisition identifier, defaults to None
    :type acquisition: str, optional

    :param task: task identifier, defaults to None
    :type task: str, optional

    :param direction: direction identifier, defaults to None
    :type direction: str, optional

    :param run: run identifier, defaults to None
    :type run: str, optional

    :param process: process identifier, defaults to None
    :type process: str, optional

    :param resolution: resolution identifier, defaults to None
    :type resolution: str, optional

    :param space: space identifier, defaults to None
    :type space: str, optional

    :param description: description identifier, defaults to None
    :type description: str, optional

    :param suffix: suffix identifier, defaults to None
    :type suffix: str, optional

    :param extension: file externsion, defaults to None
    :type extension: str, optional

    :return: BIDS-compliant filename
    :rtype: str
    """  

    d_keyId = {'session':'ses', 
               'acquisition': 'acq',
               'task': 'task',
               'direction': 'dir',
               'run': 'run',
               'process': 'proc',
               'resolution': 'res',
               'space': 'space',
                'description': 'desc'
               }

    filename = str()
    if subject:
        filename = 'sub-' + subject

    for k in ['session','acquisition','task','direction','run','process','resolution','space','description']:
        if eval(k) is not None:
            filename = filename + '_' + d_keyId[k] + '-' + eval(k)

    if suffix is not None:
        filename = filename + '_' + suffix

    if extension is not None:
        filename = filename + '.' + extension

    return filename


def get_bids_labels(IN_FILE: str) -> dict:
    """
    Get bids compliant filename labels from a file

    get_bids_labels(IN_FILE)

    :param IN_FILE: BIDS-compliant filename or filepath
    :type IN_FILE: str

    :return: bids filename labels
    :rtype: dict
    """

    labels = {}
    
    filename = _os.path.basename(IN_FILE)

    #see if there is an extension
    idx = filename.find('.')
    if idx != -1:
        baseFilename = filename[:idx]
        labels['extension'] = filename[idx+1:]
    else:
        baseFilename = filename
        labels['extension'] = None


    d_keyId = {'acq':'acquisition',
               'task':'task', 
               'dir':'direction', 
               'run':'run', 
               'proc':'process',
               'res':'resolution',
               'space':'space',
               'desc':'description'
               }
    for k in ['task','acq','run','proc','res','space','desc']:
        if k + '-' in baseFilename:
            labels[d_keyId[k]] = baseFilename.split(k + '-')[1].split('_')[0]

    #get last item, suffix
    labels['suffix'] = baseFilename.split('_')[-1]

    return labels