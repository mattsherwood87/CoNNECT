#!/resshare/general_processing_codes/python3_venv/bin/python
# the command above ^^^ sets python 3.10.9 venv as the interpreter for this program

# Created by Matthew Sherwood (matt.sherwood@wright.edu, matthew.sherwood.7.ctr@us.af.mil)
# Created on 28 FEB 2024
#
# Modified on 

import os
import sys
import argparse
from glob import glob as glob
from nipype.interfaces import fsl

# REALPATH = os.path.dirname(os.path.realpath(__file__))
REALPATH = os.path.join('/resshare','general_processing_codes')
sys.path.append(REALPATH)


#versioning
VERSION = '1.0.0'
DATE = '28 FEB 2024'

parser = argparse.ArgumentParser('feat_full_firstlevel.py: perform first level FEAT fMRI analysis')
FSLDIR = os.environ["FSLDIR"]

# s3 = boto3.resource('s3')
#

def parse_arguments():

    #input options for main()
    parser.add_argument('DATADIR')
    parser.add_argument('SUBNAME')
    parser.add_argument('SESNUM')
    parser.add_argument('FEATDESIGNDIR')
    parser.add_argument('FEATOUTPUTDIR')
    parser.add_argument('DESIGNBASENAME')
    parser.add_argument('--reference',action='store',dest='REFERENCE',default=None)
    parser.add_argument('--step2-design-basename',action='store',dest='STEP2DESIGNBASENAME',default=None)
    parser.add_argument('--struc-reg-matrix',action='store',dest='STRUCREGMATRIX',default=None)
    parser.add_argument('--progress',action='store_true',dest='progress',default=False)
    options = parser.parse_args()
    return options


# *******************  MAIN  ********************    
def feat_full_firstlevel(DATADIR: str, SUBNAME: str, SESNUM: str, FEATDESIGNDIR: str, FEATOUTPUTDIR: str, DESIGNBASENAME: str, *args, **kwargs): 
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
    progress = kwargs.get('progress',False) 
    refImage = kwargs.get('reference',None) 
    step2DesignBasename = kwargs.get('step2designbasename',None)
    strucRegMatrix = kwargs.get('strucregmatrix',None)


    

    try:

        if progress:
            print('SUBJECT: ' + SUBNAME + ' SESSION: ' + SESNUM)
            print('\trunning FEAT, output directory: ' + FEATOUTPUTDIR + ' with design ' + os.path.join(FEATDESIGNDIR,DESIGNBASENAME + '.fsf'))
        #run initial FEAT design
        os.system('feat ' + os.path.join(FEATDESIGNDIR,DESIGNBASENAME + '.fsf'))
        

        #do I need to insert custom registration?
        if not refImage or not os.path.isfile(strucRegMatrix):
            if progress:
                print('\tdone')
        else:
            if progress:
                print('\tfeat step 1 complete\n\n\tcopying structural registration to standard matrix: ' + strucRegMatrix)
            
            # replace highres2standard transform
            os.system('cp ' + strucRegMatrix + ' ' + os.path.join(FEATOUTPUTDIR,'reg','highres2standard.mat'))


            if progress:
                print('\tupdating feat with the new registration matrix')

            # update feat output with new transform
            os.system('updatefeatreg ' + FEATOUTPUTDIR + ' -gifs')


            if progress:
                print('\n\trunning feat step 2 (stats and post-stats) on: ' + FEATOUTPUTDIR + ' with design ' + os.path.join(FEATDESIGNDIR,step2DesignBasename + '.fsf'))

            # run feat stats/poststats again
            os.system('feat ' + os.path.join(FEATDESIGNDIR,step2DesignBasename + '.fsf'))
            if progress:
                print('\tdone\n')


        # compute percent signal change
        for statsFile in glob(os.path.join(FEATOUTPUTDIR,'stats','cope*')):
            if progress:
                print('\tcreating percent signal change image for ' + os.path.basename(statsFile).split('.')[0])
            argStr = ('fslmaths ' + 
                      statsFile + 
                      ' -mul 100 -div ' +
                      os.path.join(FEATOUTPUTDIR,'mean_func.nii.gz') + 
                      ' ' + os.path.join(FEATOUTPUTDIR,'stats','desc-percent-signal-change_' + os.path.basename(statsFile).split('.')[0] + '.nii.gz')
                      )
            os.system(argStr)

        # # #add some transform shit
        statsFiles = glob(os.path.join(FEATOUTPUTDIR,'stats','*'))
        ref = 'highres'
        applyxfm = fsl.ApplyXFM()
        applyxfm.inputs.reference = os.path.join(FEATOUTPUTDIR,'reg',ref + '.nii.gz')
        applyxfm.inputs.apply_xfm = True
        applyxfm.inputs.in_matrix_file = os.path.join(FEATOUTPUTDIR,'reg','example_func2' + ref + '.mat')
        if os.path.isfile(applyxfm.inputs.in_matrix_file):

            for statsFile in statsFiles:
                if not 'pe' in os.path.basename(statsFile) and not 'zstat' in os.path.basename(statsFile) and not 'tstat' in os.path.basename(statsFile):
                    continue

                applyxfm.inputs.in_file = statsFile
                applyxfm.inputs.out_file = os.path.join(FEATOUTPUTDIR,'reg_highres','stats','space-' + ref + '_' + os.path.basename(statsFile).split('.')[0] + '.nii.gz')

                if not os.path.isdir(os.path.join(FEATOUTPUTDIR,'reg_highres','stats')):
                    os.makedirs(os.path.join(FEATOUTPUTDIR,'reg_highres','stats'))

                if progress:
                    print('\tapplying transform ' + os.path.basename(applyxfm.inputs.in_matrix_file) + ' to ' + os.path.basename(applyxfm.inputs.in_file))
                applyxfm.run()


        ref = 'standard'
        applyxfm = fsl.ApplyXFM()
        applyxfm.inputs.reference = os.path.join(FEATOUTPUTDIR,'reg',ref + '.nii.gz')
        applyxfm.inputs.apply_xfm = True
        applyxfm.inputs.in_matrix_file = os.path.join(FEATOUTPUTDIR,'reg','example_func2' + ref + '.mat')
        if os.path.isfile(applyxfm.inputs.in_matrix_file):

            for statsFile in statsFiles:
                if not 'pe' in os.path.basename(statsFile) and not 'zstat' in os.path.basename(statsFile) and not 'tstat' in os.path.basename(statsFile):
                    continue

                applyxfm.inputs.in_file = statsFile
                applyxfm.inputs.out_file = os.path.join(FEATOUTPUTDIR,'reg_standard','stats',os.path.basename(statsFile))

                if not os.path.isdir(os.path.join(FEATOUTPUTDIR,'reg_standard','stats')):
                    os.makedirs(os.path.join(FEATOUTPUTDIR,'reg_standard','stats'))

                if not os.path.isfile(applyxfm.inputs.out_file):
                    if progress:
                        print('\tapplying transform ' + os.path.basename(applyxfm.inputs.in_matrix_file) + ' to ' + os.path.basename(applyxfm.inputs.in_file))
                    applyxfm.run()


    except Exception as e:
        print("Error Message: {0}".format(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        return


def main():
    """
    The entry point of this program.
    """
    options = parse_arguments()
    argsDict = {}
    if options.REFERENCE:
        argsDict['reference'] = options.REFERENCE
    if options.STEP2DESIGNBASENAME:
        argsDict['step2designbasename'] = options.STEP2DESIGNBASENAME
    if options.STRUCREGMATRIX:
        argsDict['strucregmatrix'] = options.STRUCREGMATRIX
    if options.progress:
        argsDict['progress'] = options.progress
    feat_full_firstlevel(options.DATADIR,options.SUBNAME,options.SESNUM,options.FEATDESIGNDIR,options.FEATOUTPUTDIR,options.DESIGNBASENAME,**argsDict)


if __name__ == '__main__':
    main()