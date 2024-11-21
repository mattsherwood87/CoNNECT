#!/resshare/wsuconnect/python3_venv/bin/python
# the command above ^^^ sets python 3.10.9 venv as the interpreter for this program

# Created by Matthew Sherwood (matt.sherwood@wright.edu, matthew.sherwood.7.ctr@us.af.mil)
# Created on 10 July 2023
#
# Modified on 

import os
import sys
import argparse

REALPATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(REALPATH)


#versioning
VERSION = '1.0.0'
DATE = '10 July 2023'

# 

#input argument parser
parser = argparse.ArgumentParser('connect_neuro_db_query.py: Query tables in the MySQL databases to search the AWS S3 bucket for specific files.')
parser.add_argument('-i','--in-dir', required=True,action='store', dest="INDIR", help="input directories to copy", default=None)
   


# *******************  MAIN  ********************    
def remove_dirs(INDIR: str): 
    """
    This function moves or copies input (source) directories to a single output directory.

    copy_dirs(OUTDIR,INDIR,move=False)

    :param INDIR: fullpath to input (source) directory(ies)
    :type INDIR: str

    :raises Exception: generic error from attenpted deletion
    """    
    try:
        os.system('rm -rf ' + INDIR)


    except Exception as e:
        print("Error Message: {0}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        return


if __name__ == '__main__':
    """
    The entry point of this program for command-line utilization.
    """

    options = parser.parse_args()
    remove_dirs(options.INDIR)