#!/resshare/wsuconnect/python3_venv/bin/python
# the command above ^^^ sets python 3.10.10 as the interpreter for this program

# Created by Matthew Sherwood (matt.sherwood@wright.edu, matthew.sherwood.7.ctr@us.af.mil)
# Created on 29 Dec 2020
#
# Modified on 1 May 2023
# Modified on 20 Oct 2021 - update to local mount of s3 bucket
# Modified on 11 Jan 2021 - add utilization of instance_ids.json

import os
import sys
import argparse

REALPATH = os.path.dirname(os.path.realpath(__file__))
sys.path.append(REALPATH)
import support_tools as st


#versioning
VERSION = '2.0.0'
DATE = '1 May 2023'

# 
lastSubjectName = ''
lastSessionNum = ''

#input argument parser
parser = argparse.ArgumentParser('connect_neuro_db_query.py: Query tables in the MySQL databases to search the AWS S3 bucket for specific files.')

# ******************* PARSE COMMAND LINE ARGUMENTS ********************
def parse_arguments():

    #parser.add_argument('-h','--help', action="store_true", dest="FLAGHELP")
    requiredNamed = parser.add_argument_group('required arguments')
    requiredNamed.add_argument('-p','--project', action="store", dest="PROJECT", help="search the selected table: " + ' '.join(st.creds.projects), default=None, required=True)
    requiredNamed.add_argument('-r','--regex', action="store", dest="REGEXSTR", help="search string (no wildcards, matches if the search string appears anywhere in the field specified by -w|--where)", default=None, required=True)
    parser.add_argument('-c','--col', action="store", dest="RETURNCOL", help="column to return: fullpath (default), filename, basename, extension, modDate, modTime", default='fullpath')
    parser.add_argument('-w','--where', action="store", dest="SEARCHCOL", help="column to search: fullpath, filename (default), basename, extension, modDate, modTime", default='filename')
    parser.add_argument('-o','--orderby', action="store", dest="ORDERBY", help="column to sort query results by: fullpath (default), filename, basename, extension, modDate, modTime", default='fullpath')
    parser.add_argument('--progress', action="store_true", dest="progress", help="show progress (default FALSE)", default=False)
    parser.add_argument('--source', action="store_true", dest="source", help="search sourcedata table (default FALSE)", default=False)
    parser.add_argument('-v', '--version', action="store_true", dest="version", help="Display the current version")
    # parser.add_argument('-s', '--sync', action="store_true", dest="SYNC", help="Sync the files to the local filesystem")
    parser.add_argument('--opt-inclusion', nargs='+', dest="inclusion", help="optional additional matching search string(s) to filter results. multiple inputs accepted through space delimiter", default=None)
    parser.add_argument('--opt-exclusion', nargs='+', dest="exclusion", help="optional exclusion search string(s) to filter results. multiple inputs accepted through space delimiter", default=None)
    
    parser.add_argument('--opt-or-inclusion', nargs='+', dest="or_inclusion", help="optional additional OR matching search string(s) to filter results. multiple inputs accepted through space delimiter", default=None)
    options = parser.parse_args()

    #determine the search table and search string
    if not options.PROJECT in st.creds.projects:
        if not options.version:
            print("ERROR: user must define a project using [-p|--project <project>]\n\n")
            parser.print_help()
        sys.exit()

    return options


# ******************* EVALUATE INPUT ARGUMENTS ********************
def evaluate_args(options):
    
    #print version if selected
    if options.version:
        print('connect_neuro_db_query.py version {0}.'.format(VERSION)+" DATED: "+DATE)

    #check for search string
    if options.REGEXSTR == None:
        print('ERROR: user must specify a search string (-r|--regex)\n')
        parser.print_help()

    
    if options.source:
        st.creds.searchTable = st.creds.searchSourceTable



# *******************  MAIN  ********************    
def main():
    """
    The entry point of this program.
    """
    options = parse_arguments()
    st.read_credentials(options.PROJECT)
    evaluate_args(options)
    
    fullpath = st.mysql_commands.sql_query(database=st.creds.database,searchtable=st.creds.searchTable,regex=options.REGEXSTR,searchcol=options.SEARCHCOL,returncol=options.RETURNCOL,orderby=options.ORDERBY,progress=options.progress,inclusion=options.inclusion,exclusion=options.exclusion,orinclusion=options.or_inclusion)

    #print list 
    print(*fullpath, sep ='\n') 
    #return fullpath


if __name__ == '__main__':
    main()