#!/resshare/general_processing_codes/python3_venv/bin/python
# the command above ^^^ sets python 3.10.9 venv as the interpreter for this program

# Created by Matthew Sherwood (matt.sherwood@wright.edu, matthew.sherwood.7.ctr@us.af.mil)
# Created on 10 July 2023
#
# Modified on 

import os
import sys
import argparse
import shutil

# REALPATH = os.path.dirname(os.path.realpath(__file__))
REALPATH = os.path.join('/resshare','general_processing_codes')
sys.path.append(REALPATH)


#versioning
VERSION = '1.0.0'
DATE = '10 July 2023'

# 
lastSubjectName = ''
lastSessionNum = ''

#input argument parser
parser = argparse.ArgumentParser('connect_neuro_db_query.py: Query tables in the MySQL databases to search the AWS S3 bucket for specific files.')

# ******************* PARSE COMMAND LINE ARGUMENTS ********************
def parse_arguments():

    #parser.add_argument('-h','--help', action="store_true", dest="FLAGHELP")
    requiredNamed = parser.add_argument_group('required arguments')
    requiredNamed.add_argument('-o','--out-dir', action="store", dest="OUTDIR", help="destination directory to copy inputs to", default=None, required=True)
    requiredNamed.add_argument('-i','--in-dir', nargs='+', dest="INDIR", help="input directories to copy. multiple inputs accepted through space delimiter", default=None, required=True)
    parser.add_argument('-m','--move', action='store_true', dest='MOVE', help='move files instead of copy',default=False)
    options = parser.parse_args()

    return options


# *******************  MAIN  ********************    
def copy_dirs(OUTDIR: str,INDIR: list,*args,**kwargs): 
    """
    This function moves or copies input (source) directories to a single output directory.

    copy_dirs(OUTDIR,INDIR,move=False)

    Arguments:

        OUTDIR (str): fullpath to an output (destination) directory

        INDIR (list or str): fullpath to input (source) directory(ies)
            
        move (BOOL): OPTIONAL flag to perform a move instead of a copy

    Returns:
        None
    """
    try:
        moveFiles = kwargs.get('move',False)
        if type(INDIR) == list:
            for inDir in INDIR:
                if moveFiles:
                    if not os.path.isdir(os.path.dirname(OUTDIR)):
                        os.makedirs(OUTDIR)
                    os.system('mv ' + inDir + ' ' + OUTDIR)
                    # shutil.rmtree(inDir)
                    # shutil.move(inDir,OUTDIR)
                else:
                    if not os.path.isdir(OUTDIR):
                        os.makedirs(OUTDIR)
                    print('cp -RL ' + inDir + ' ' + OUTDIR)
                    os.system('cp -RL ' + inDir + ' ' + OUTDIR)


        else:
            if moveFiles:
                shutil.move(INDIR,OUTDIR)
            else:
                os.system('cp -RL ' + inDir + ' ' + OUTDIR)


    except Exception as e:
        print("Error Message: {0}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        return


if __name__ == '__main__':

    options = parse_arguments()
    copy_dirs(options.OUTDIR,options.INDIR,move=options.MOVE)