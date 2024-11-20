#!/resshare/wsuconnect/python3_venv/bin/python
# the command above ^^^ sets python 3.10.9 as the interpreter for this program

# Created by Matthew Sherwood (matt.sherwood@wright.edu, matthew.sherwood.7.ctr@us.af.mil)
# Created on 19 June 2023
#
# Last Modified on 

# ******* IMPORTS ***********
from cmath import inf
import os
import argparse
import shutil
import datetime
# import numpy as np
# import math
import time


# ******* LOCAL IMPORTS ******


# ******* GLOBAL INFO *******
#versioning
VERSION = '1.0.0'
DATE = '19 June 2023'

#GLOBALS
REALPATH = os.path.dirname(os.path.realpath(__file__))

# ******************* PARSE COMMAND LINE ARGUMENTS ********************
parser = argparse.ArgumentParser()
parser.add_argument('-v', '--version', action="store_true", dest="version", help="Display the current version")



# ******************* MAIN ********************
def main():
    """
    The entry point of this program.
    """

    #input and output locations
    inLogPath = os.path.join('C:\\','Users','connect_usr','Desktop')
    outLogPath = os.path.join('W:\\','tmp_beh_logs')
    print(inLogPath)
    print(outLogPath)

    outputLog = os.path.join(inLogPath,'connect_exp_log_grabber_p1.txt')
    if os.path.isfile(outputLog):
        f = open(outputLog,'r+')
        l = f.readlines()
        # l.insert(0,d + '\n')
        # f.seek(0) #get to the first position
        # f.writelines(l)
        f.close()
        
    else:
        l = []
	



    for root, dirs, files in os.walk(inLogPath, topdown=True):
    # for path in Path(dcmPath).rglob('*'):
        for filename in files:
            if not filename + '\n' in l:
                try:
                    if '.log' in filename or '.csv' in filename and not 'inputs' in root:
                        print(filename)
                        shutil.copyfile(os.path.join(root,filename),os.path.join(outLogPath,filename))
                        
                        if os.path.isfile(outputLog):
                            f = open(outputLog,'r+')
                            l2 = f.readlines()
                            l2.insert(0,filename + '\n')
                        else:
                            f = open(outputLog,'x')
                            l2 = [filename + '\n']
                            
                        f.seek(0) #get to the first position
                        f.writelines(l2)
                        f.close()
                            
                except OSError as e:
                    print(e)

            else:
                print('file ' + filename + ' skipped')                


if __name__ == '__main__':
    main()
