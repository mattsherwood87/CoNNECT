#!/resshare/wsuconnect/python3_venv/bin/python
# the command above ^^^ sets python 3.6.9 as the interpreter for this program

# Created by Matthew Sherwood (matt.sherwood@us.kbr.com, matthew.sherwood.7.ctr@us.af.mil)
# Created on 22 Jan 2021
#
# Last modified on 2 Jan 2021

# import sys
import os
import argparse

import datetime



VERSION = '1.0.1'
DATE = '22 Jan 2021'

FSLDIR = os.environ["FSLDIR"]



parser = argparse.ArgumentParser()
    #input options for main()
parser.add_argument('in_file', help='fullpath to the input NIfTI image in reference space')
parser.add_argument('reference', help='fullpath to the reference space NIfTI image')
parser.add_argument('out_file', help='fullpath to output png to contain the overlay images')


# ******************* python utilization ********************
def flirt_pngappend(in_file: str,reference: str,out_file: str):
    """
    Creates a registration overlay image (PNG). 
    
    Top row contains a background image of in_file in reference space overlaid with the edges of reference
    Bottom row contains a background image of reference overlaid  with the edges of in_file in reference space

    :param in_file: fullpath to the input NIfTI image in reference space
    :type in_file: str

    :param reference: fullpath to the reference space NIfTI image
    :type reference: str

    :param out_file: fullpath to output png to contain the overlay images
    :type out_file: str
    """
    now = datetime.datetime.now()
    nowStr = now.strftime("%Y%m%d%H%M%S%f")  

    #create unique temporary folder
    baseDir = os.path.join(os.path.dirname(in_file),'tmp-' + nowStr)
    if not os.path.isdir(baseDir):
        os.makedirs(baseDir)

    inputStr = ('slicer' + 
               ' ' + in_file + 
               ' ' + reference + 
               ' -s 2 -x 0.35 ' + os.path.join(baseDir,'sla.png') + 
               ' -x 0.45 ' + os.path.join(baseDir,'slb.png') + 
               ' -x 0.55 ' + os.path.join(baseDir,'slc.png') + 
               ' -x 0.65 ' + os.path.join(baseDir,'sld.png') + 
               ' -y 0.35 ' + os.path.join(baseDir,'sle.png') + 
               ' -y 0.45 ' + os.path.join(baseDir,'slf.png') + 
               ' -y 0.55 ' + os.path.join(baseDir,'slg.png') + 
               ' -y 0.65 ' + os.path.join(baseDir,'slh.png') + 
               ' -z 0.35 ' + os.path.join(baseDir,'sli.png') + 
               ' -z 0.45 ' + os.path.join(baseDir,'slj.png') + 
               ' -z 0.55 ' + os.path.join(baseDir,'slk.png') + 
               ' -z 0.65 ' + os.path.join(baseDir,'sll.png'))
    os.system(inputStr)

    inputStr = ('pngappend' + 
               ' ' + os.path.join(baseDir,'sla.png') + 
               ' + ' + os.path.join(baseDir,'slb.png') + 
               ' + ' + os.path.join(baseDir,'slc.png') + 
               ' + ' + os.path.join(baseDir,'sld.png') + 
               ' + ' + os.path.join(baseDir,'sle.png') + 
               ' + ' + os.path.join(baseDir,'slf.png') + 
               ' + ' + os.path.join(baseDir,'slg.png') + 
               ' + ' + os.path.join(baseDir,'slh.png') + 
               ' + ' + os.path.join(baseDir,'sli.png') + 
               ' + ' + os.path.join(baseDir,'slj.png') + 
               ' + ' + os.path.join(baseDir,'slk.png') + 
               ' + ' + os.path.join(baseDir,'sll.png') +
               ' ' + os.path.join(baseDir,'tmp1.png'))
    os.system(inputStr)
    
    os.system(('slicer' + 
               ' ' + reference + 
               ' ' + in_file + 
               ' -s 2 -x 0.35 ' + os.path.join(baseDir,'sla.png') + 
               ' -x 0.45 ' + os.path.join(baseDir,'slb.png') + 
               ' -x 0.55 ' + os.path.join(baseDir,'slc.png') + 
               ' -x 0.65 ' + os.path.join(baseDir,'sld.png') + 
               ' -y 0.35 ' + os.path.join(baseDir,'sle.png') + 
               ' -y 0.45 ' + os.path.join(baseDir,'slf.png') + 
               ' -y 0.55 ' + os.path.join(baseDir,'slg.png') + 
               ' -y 0.65 ' + os.path.join(baseDir,'slh.png') + 
               ' -z 0.35 ' + os.path.join(baseDir,'sli.png') + 
               ' -z 0.45 ' + os.path.join(baseDir,'slj.png') + 
               ' -z 0.55 ' + os.path.join(baseDir,'slk.png') + 
               ' -z 0.65 ' + os.path.join(baseDir,'sll.png')))
    os.system(('pngappend' + 
               ' ' + os.path.join(baseDir,'sla.png') + 
               ' + ' + os.path.join(baseDir,'slb.png') + 
               ' + ' + os.path.join(baseDir,'slc.png') + 
               ' + ' + os.path.join(baseDir,'sld.png') + 
               ' + ' + os.path.join(baseDir,'sle.png') + 
               ' + ' + os.path.join(baseDir,'slf.png') + 
               ' + ' + os.path.join(baseDir,'slg.png') + 
               ' + ' + os.path.join(baseDir,'slh.png') + 
               ' + ' + os.path.join(baseDir,'sli.png') + 
               ' + ' + os.path.join(baseDir,'slj.png') + 
               ' + ' + os.path.join(baseDir,'slk.png') + 
               ' + ' + os.path.join(baseDir,'sll.png') + 
               ' ' + os.path.join(baseDir,'tmp2.png')))

    os.system('pngappend' + ' ' + os.path.join(baseDir,'tmp1.png') + ' - ' + os.path.join(baseDir,'tmp2.png') + ' ' + out_file)

    #remove intermediate files
    fileList = ['a','b','c','d','e','f','g','h','i','j','k','l']
    for v in fileList:
        os.remove(os.path.join(baseDir,'sl' + v + '.png'))
    os.remove(os.path.join(baseDir,'tmp1.png'))
    os.remove(os.path.join(baseDir,'tmp2.png'))
    os.removedirs(baseDir)



if __name__ == '__main__':
    """
    The entry point of this program for command-line utilization.
    """
    options = parser.parse_args()
    #if options.SUB:
    #    MATH = '-'
    #elif options.ADD:
    #    MATH = '+'
    flirt_pngappend(options.in_file,options.reference,options.out_file)

    


