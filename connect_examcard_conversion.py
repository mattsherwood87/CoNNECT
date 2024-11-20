#!/resshare/general_processing_codes/python3_venv/bin/python
# the command above ^^^ sets python 3.10.10 as the interpreter for this program

# Created by Matthew Sherwood (matt.sherwood@wright.edu, matthew.sherwood.7.ctr@us.af.mil)
# Created on 23 April 2024
#
# v2.0.0 on 1 April 2023 - 

import os
import sys
import datetime
import argparse
import re
from glob import glob as glob


REALPATH = os.path.realpath(__file__)
sys.path.append(os.path.dirname(REALPATH))
from helper_functions.prepare_examcard_html import prepare_examcard_html
from helper_functions.read_credentials import *
from classes.creds import *

# GLOBAL INFO
#versioning
VERSION = '1.0.0'
DATE = '23 April 2024'

#input argument parser
parser = argparse.ArgumentParser(os.path.basename(REALPATH) + ' - Create ExamCard Tables')

# ******************* PARSE COMMAND LINE ARGUMENTS ********************
def parse_arguments():
    
    requiredNamed = parser.add_argument_group('required arguments')
    requiredNamed.add_argument('-p','--project', action="store", dest="PROJECT", help="load the selected projects examcards from scanorder.txt: " + ' '.join(creds.projects), default=None)
    # parser.add_argument('-r','--raw', action="store_true", dest="RAW", help="Command line argument to update the raw_data table for the selected project (default FALSE)", default=False)
    parser.add_argument('-v', '--version', help="Display the current version", action="store_true", dest="version")
    parser.add_argument('-i', '--in-dir', help="Use a specific directory rather than a project directory", action="store", default=None, dest="INDIR")
    parser.add_argument('--progress', help="Show progress (default FALSE)", action="store_true", dest="progress", default=False)
    options = parser.parse_args()

    #determine the search table and search string
    if not options.PROJECT in creds.projects:
        if not options.INDIR:
            if not options.version:
                print("ERROR: user must define a project using [-p|--project <project>]\n\n")
                parser.print_help()
            sys.exit()

    return options


# ******************* SORT REQUESTED TABLES ********************
def evaluate_args(options):

    #print version if selected
    if options.version:
        print(os.path.basename(REALPATH) + ' version {0}.'.format(VERSION)+" DATED: "+DATE)


# *******************  MAIN  ********************    
def main():
    """
    The entry point of this program.
    """
    options = parse_arguments()
    evaluate_args(options)

    print('Creating ExamCard tables on ' + datetime.datetime.today().strftime('%Y%m%d @ %H:%M:%S'))


    #create tables
    read_credentials(options.PROJECT)

    if options.PROJECT:
        ecardDir = os.path.join(creds.dataDir,'ExamCards')
    else:
        ecardDir = options.INDIR


    # setup HTML headers
    newD = prepare_examcard_html()
      


    # inFiles = glob(os.path.join(ecardDir, '*.txt'))
    if not os.path.isfile(os.path.join(ecardDir,'scanorder.txt')):
        print('ERROR: cannot find scanorder.txt in  examcard directory - ' + ecardDir)
        return
    f = open(os.path.join(ecardDir,'scanorder.txt'), 'r') 
  
    # reading the file 
    data = f.read() 
    
    # replacing end splitting the text  
    # when newline ('\n') is seen. 
    pgbreak_flag = False
    ls_inFiles = data.split('\n')

    newD.append('<div>')
    newD.append('<p>')

    #newD.append('<div id="page" class="page" style = "background-color:#FFFFFF; height: 100%; width: 100%;">')
    # newD.append('<div class="header">')
    # # newD.append('<font face="Arial"><h1>' + seq + '</h1> </font>')
    # newD.append('</div>')

    #newD.append('<table style="width: 8.5in; height: 9in;">')
    newD.append('<table width="60%" border="1" cellspacing="0" cellpadding="2" align="Left" bordercolor="#000000">')
    # newD.append('<table width="100%" border="0" cellspacing="0" cellpadding="2" align="Left">')
    # newD.append('<table class="border-none">')


    newD.append('<colgroup>')
    newD.append('<col span="1" style="width: 30%;">')
    newD.append('<col span="1" style="width: 70%;">')
    newD.append('</colgroup>')

    newD.append('<br>')
    newD.append('<br>')
    newD.append('<tr>')
    newD.append('<td><font size="2">Sequence Number</td>')
    newD.append('<td><font size="2">Sequence Name</td>')
    newD.append('</tr>')
    c = 1
    for inFile in ls_inFiles:
        if not inFile:
            continue

        

        newD.append('<tr>')
        newD.append('<td><font size="2">' + str(c) + '</td>')
        newD.append('<td><font size="2">' + inFile.split('.')[0] + '</td>')
        newD.append('</tr>')
        c += 1

    newD.append('</table>')
    newD.append('</font>')

    newD.append('</p>')
    newD.append('</div>')

    c = 1
    for inFile in ls_inFiles:
        if not inFile: 
            continue



        d_dict = {'inf_t': [],'inf_c': [],'inf_v': [],
                'geo_t': [],'geo_c': [],'geo_v': [],
                'con_t': [],'con_c': [],'con_v': [],
                'mot_t': [],'mot_c': [],'mot_v': [],
                'dyn_t': [],'dyn_c': [],'dyn_v': [],
                'pro_t': [],'pro_c': [],'pro_v': []
                }  
        seq = os.path.basename(inFile).split('.')[0].replace('_',' ')

        if options.progress:
            print('Processing sequence: ' + seq)

        #continue header
        # if pgbreak_flag:
        newD.append('<div class="pagebreak"> </div>')
        # else:
            # pgbreak_flag = True


        # newD.append('<section>'10
        # newD.append('<h2><font face="arial" size="+1">Wright State University | Center of Neuroimaging and Neuro-Evaluation of Cognitive Technology</font></h2>')
        # newD.append('</section>')
        newD.append('<div>')
        newD.append('<p>')

        #newD.append('<div id="page" class="page" style = "background-color:#FFFFFF; height: 100%; width: 100%;">')
        # newD.append('<div class="header">')
        # # newD.append('<font face="Arial"><h1>' + seq + '</h1> </font>')
        # newD.append('</div>')

        #newD.append('<table style="width: 8.5in; height: 9in;">')
        newD.append('<table width="100%" border="1" cellspacing="0" cellpadding="2" align="Left" bordercolor="#000000">')
        # newD.append('<table width="100%" border="0" cellspacing="0" cellpadding="2" align="Left">')
        # newD.append('<table class="border-none">')


        newD.append('<colgroup>')
        newD.append('<col span="1" style="width: 20%;">')
        newD.append('<col span="1" style="width: 12.33%;">')
        newD.append('<col span="1" style="width: 1%;">')
        newD.append('<col span="1" style="width: 20%;">')
        newD.append('<col span="1" style="width: 12.33%;">')
        newD.append('<col span="1" style="width: 1%;">')
        newD.append('<col span="1" style="width: 20%;">')
        newD.append('<col span="1" style="width: 13.33%;">')
        newD.append('</colgroup>')
        #newD.append('<font face="arial" size="1">')

        #newD.append('<table width="90%" border="1" cellspacing="0" cellpadding="2" align="Left" bordercolor="#000000">')

  
        # reading the file 
        f = open(os.path.join(ecardDir,inFile), 'r') 
        data = f.read() 
        
        # replacing end splitting the text  
        # when newline ('\n') is seen. 
        ls_data = data.split('\n')


        # Parse the input file
        strCat = 'geo'
        skipLines = 0
        for k in ls_data:
            if not k:
                continue
            if skipLines > 0:
                k2 = k.strip()
                k2 = k2.replace('\t','')
                k2 = k2.replace(';','')
                k2 = k2.replace('"','')
                if not '=' in k2:
                    continue
                skipLines -= 1
                # print('WARNING: ' + k)
                continue


            # reformat data into two-column list [key, value]
            k = k.strip()
            k = k.replace('\t','')
            k = k.replace(';','')
            k = k.replace('"','')
            if not '=' in k:
                continue
            a = k.split(' =')

            
            if ('Stack Offc.' in a[0] or "Ang." in a[0]) or 'VOI offc' in a[0] or 'VOI ang' in a[0] or 'Shim  Size' in a[0] or "Offc." in a[0]and not 'Angio' in a[0]:
                skipLines = 2
                # print('WARNING: ' + a[0])
                continue
            elif a[0] in ['EX_single_scan_id','Coil 1  (exclude)','compacted','compacted coils','compacted conns','stacks channels','clinical modes','Patient weight [kg]','SmartSelect','Coil 1 (exclude)',
                          'Large table movement','Patient position','Patient body position','Patient orientations','Patient body orientation','SAR allow first level','Patient pregnancy','Patient WB SAR [W/kg]',
                          'Patient Head SAR [W/kg]','Patient max. dB/dt [T/s]','Max slewrate [T/m/s]','Max. B1+rms [uT]','2nd VOI lat. offc. (mm)','2nd VOI offc. axis','IF_info_seperator','Free rotatable']:
                continue
            elif 'EX_GEO' in a[0]:
                continue

            k = k.strip()
            k = k.replace('\t','')
            k = k.replace(';','')
            k = k.replace('"','')
            a = k.split(' =')
            a[0].rstrip()

            if a[0] in ['(mm)','(ms)','P (mm)','A (mm)','F (mm)','(pixels)','AP (mm)','FH (mm)','RL (mm)','slices','Slices','slice gap','slice orientation',
                        'fold-over direction','fat shift direction','Modified SE','MB Factor','MB Shift','partial echo','shifted echo','factor',
                        'oversample factor','technique','3D view','shot mode','startup echoes','profile order','turbo direction','DRIVE',
                        '3D non-select','partial echoes','strength','offset','dyn scans','dyn scan times','fov time mode','dummy scans',
                        'immediate subtraction','fast next scan','synch. ext. device','dyn stabilization','prospect. motion corr.',
                        'label type','label distance (mm)','label location','label duration','post label delay (ms)','normalized',
                        'phases','start at dyn.','interval (dyn)','images','calculated images','frequency offset','offset (Hz)',
                        'orientation','type','resuse memory','delay','PSIR','echo time (ms)','refocusing pulses','fid reduction',
                        'angle (deg.)','gradient expert mode','gradient overplus','directional resolution','modified SE','SMART',
                        'acquire during delay','dual','power','ultrashort','fid reduction extra strong','Offc. AP (P=+mm)','RL (L=+mm)',
                        'FH (H=+mm)','reuse memory','radial axis','radial angle (deg)']:
                a[0] = '<span class="tab"></span>' + a[0]
            
            elif 'P reduction' in a[0] or 'S reduction' in a[0]:
                a[0] = '<span class="tab"></span>' + a[0]

            elif a[0] in ['gap (mm)']:
                a[0] = '<span class="tab"></span><span class="tab"></span>' + a[0]


            # print(a[0] + '\t=\t' + a[1])
            if 'Uniformity' in a[0] and not 'correction' in a[0]:
                strCat = 'geo'
            elif 'Scan type' in a[0]:
                strCat = 'con'
            elif 'Cardiac synchronization' in a[0]:
                strCat = 'mot'
                d_dict[strCat + '_c'].append(strCat)
                d_dict[strCat + '_t'].append('test')
                d_dict[strCat + '_v'].append('test')
            elif ('Manual start' in a[0] or "Contrast enh." in a[0]) and not 'dyn' in strCat:
                strCat = 'dyn'
                d_dict[strCat + '_c'].append(strCat)
                d_dict[strCat + '_t'].append('test')
                d_dict[strCat + '_v'].append('test')
            elif ('Preparation phases' in a[0] or 'Images' in a[0]) and not 'pro' in strCat:
                strCat = 'pro'
                d_dict[strCat + '_c'].append(strCat)
                d_dict[strCat + '_t'].append('test')
                d_dict[strCat + '_v'].append('test')
            elif 'Total scan duration' in a[0]:
                strCat = 'inf'

            
            # print(a[0] + '\t' + strCat)
            d_dict[strCat + '_c'].append(strCat)
            d_dict[strCat + '_t'].append(a[0])
            d_dict[strCat + '_v'].append(a[1])





        # write values to table
        stopFlag = False
        ci = 0
        cg = 0
        cp = 0
        cm = 0
        cc = 0
        cd = 0
        ciFlag = True
        cgFlag = True
        ccFlag = True
        cmFlag = False
        cpFlag = False
        cdFlag = False

        # newD.append('INFO PAGE\t\tGEOMETRY\t\tCONTRAST')
        newD.append('<br>')
        newD.append('<br>')
        newD.append('<tr>')
        newD.append('<td colspan="8" style="border: none; border-collapse: collapse; font-weight:bold; text-align: center"> <font size="5">' + str(c) + ', ' +  seq + '</td>')
        newD.append('</tr>')
        c += 1
        # newD.append('<h1>' + seq + '</h1>')
        newD.append('<tr>')
        newD.append('<td bgcolor="#046A38" colspan="2" style="font-weight:bold; text-align: center; vertical-align: middle;"> <font color="#FFFFFF" size="2">INFO PAGE</td>')
        newD.append('<td></td>')
        newD.append('<td bgcolor="#046A38" colspan="2" style="font-weight:bold; text-align: center; vertical-align: middle;"> <font color="#FFFFFF" size="2">GEOMETRY</td>')
        newD.append('<td></td>')
        newD.append('<td bgcolor="#046A38" colspan="2" style="font-weight:bold; text-align: center; vertical-align: middle;"> <font color="#FFFFFF" size="2">CONTRAST</td>')
        newD.append('</tr>')
        while not stopFlag:
            newD.append('<tr>')
            strOut=''
            if ciFlag:
                strOut += d_dict['inf_t'][ci] + '\t' + d_dict['inf_v'][ci] + '\t'
                newD.append('<td>' + d_dict['inf_t'][ci] + '</td>')
                newD.append('<td>' + d_dict['inf_v'][ci] + '</td>')
                newD.append('<td></td>')
                ci += 1
                if ci == len(d_dict['inf_t']):
                    ciFlag = False
                    cpFlag = True

            elif cpFlag:
                if cp == 0 and ci == len(d_dict['inf_t']):
                    # strOut += 'POST/PROC\t\t'
                    newD.append('<td bgcolor="#046A38" colspan="2" style="font-weight:bold; text-align: center; vertical-align: middle;"> <font color="#FFFFFF" size="2">POST/PROC</td>')
                    newD.append('<td></td>')
                    ci = 1000
                    cp += 1
                else:
                    # strOut += d_dict['pro_t'][cp] + '\t' + d_dict['pro_v'][cp] + '\t'
                    newD.append('<td>' + d_dict['pro_t'][cp] + '</td>')
                    newD.append('<td>' + d_dict['pro_v'][cp] + '</td>')
                    newD.append('<td></td>')
                    cp += 1
                    if cp == len(d_dict['pro_t']):
                        cpFlag = False
            elif not ciFlag and not cpFlag:
                # strOut += '\t\t'
                newD.append('<td></td>')
                newD.append('<td></td>')
                newD.append('<td></td>')

            if cgFlag:
                # strOut += d_dict['geo_t'][cg] + '\t' + d_dict['geo_v'][cg] + '\t'
                newD.append('<td>' + d_dict['geo_t'][cg] + '</td>')
                newD.append('<td>' + d_dict['geo_v'][cg] + '</td>')
                newD.append('<td></td>')
                cg += 1
                if cg == len(d_dict['geo_t']):
                    cgFlag = False
                    cmFlag = True

            elif cmFlag:
                if cm == 0 and cg == len(d_dict['geo_t']):
                    # strOut+= 'MOTION\t\t'
                    newD.append('<td bgcolor="#046A38" colspan="2" style="font-weight:bold; text-align: center; vertical-align: middle;"> <font color="#FFFFFF" size="2">MOTION</td>')
                    newD.append('<td></td>')
                    cg = 1000
                    cm += 1
                else:
                    # strOut += d_dict['mot_t'][cm] + '\t' + d_dict['mot_v'][cm] + '\t'
                    newD.append('<td>' + d_dict['mot_t'][cm] + '</td>')
                    newD.append('<td>' + d_dict['mot_v'][cm] + '</td>')
                    newD.append('<td></td>')
                    cm += 1
                    if cm == len(d_dict['mot_t']):
                        cmFlag = False
                        cdFlag = True
                # strOut += '\t\t'

            elif cdFlag:
                if cd == 0 and cm == len(d_dict['mot_t']):
                    # strOut += 'DYN/ANG\t\t'
                    newD.append('<td bgcolor="#046A38" colspan="2" style="font-weight:bold; text-align: center; vertical-align: middle;"> <font color="#FFFFFF" size="2">DYN/ANG</td>')
                    newD.append('<td></td>')
                    cm = 1000
                    cd += 1
                else:
                    # strOut += d_dict['dyn_t'][cd] + '\t' + d_dict['dyn_v'][cd] + '\t'
                    newD.append('<td>' + d_dict['dyn_t'][cd] + '</td>')
                    newD.append('<td>' + d_dict['dyn_v'][cd] + '</td>')
                    newD.append('<td></td>')
                    cd += 1
                    if cd == len(d_dict['dyn_t']):
                        cdFlag = False
            elif not cgFlag and not cmFlag and not cdFlag:
                # strOut += '\t\t'
                newD.append('<td></td>')
                newD.append('<td></td>')
                newD.append('<td></td>')


            if ccFlag:
                # strOut += d_dict['con_t'][cc] + '\t' + d_dict['con_v'][cc] + '\t'
                newD.append('<td>' + d_dict['con_t'][cc] + '</td>')
                newD.append('<td>' + d_dict['con_v'][cc] + '</td>')
                cc += 1
                if cc == len(d_dict['con_t']):
                    ccFlag = False

            newD.append('</tr>')
            if not ciFlag and not cgFlag and not ccFlag and not cmFlag and not cdFlag and not cpFlag:
                stopFlag = True

        newD.append('</table>')
        newD.append('</font>')

        newD.append('</p>')
        newD.append('</div>')


    newD.append('<footer>Created by connect_examcard_conversion.py on ' + datetime.datetime.today().strftime('%B %d, %Y @ %H:%M:%S') + '</footer>')





    newD.append('</body>')
    newD.append('</html>')

    with open(os.path.join(ecardDir, 'examcard.html'), 'w') as f:
        for line in newD:
            f.write(f"{line}\n")

    # os.system('wkhtmltopdf --enable-local-file-access -O Portrait ' + os.path.join(ecardDir, 'examcard.html') + ' ' + os.path.join(ecardDir, 'examcard.pdf'))
    



if __name__ == '__main__':
    main()



