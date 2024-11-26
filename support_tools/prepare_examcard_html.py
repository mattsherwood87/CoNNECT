#!/resshare/wsuconnect/python3_venv/bin/python
# the command above ^^^ sets python 3.10.10 as the interpreter for this program

# Created by Matthew Sherwood (matt.sherwood@wright.edu, matthew.sherwood.7.ctr@us.af.mil)
# Created on 24 April 2024
#
# 



def prepare_examcard_html() -> list:
    """
    Prepares the html header for the examcard html file when converting examcards from txt to html.
    """
    newD = []
    newD.append('<!DOCTYPE html>')
    newD.append('<html>')
    newD.append('<head>')
    newD.append('<style>')

    newD.append('footer {')
    newD.append('font-size: 9px;')
    # newD.append('color: #f00;')
    newD.append('text-align: center;')
    newD.append('}')

    newD.append('header {')
    newD.append('font-size: 9px;')
    # newD.append('color: #f00;')
    newD.append('text-align: center;')
    newD.append('}')

    newD.append('@page {')
    newD.append('size: 8.5in 11in; margin: 0.5in 0.5in 0.5in 0.5in;')
    newD.append('}')
    # newD.append('@media screen {')
    # newD.append('footer {')
    # newD.append('display: none; }')
    # newD.append('}')
    newD.append('.tab {')
    newD.append('display: inline-block;')
    newD.append('margin-left: 2em;')
    newD.append('}')

    newD.append('@media print {')
    newD.append('table {')
    newD.append('page-break-inside: avoid; empty-cells: hide; }')
    newD.append('.pagebreak {')
    newD.append('page-break-before: always; }')
    newD.append('footer {')
    newD.append('position: fixed; bottom: 0; }')
    newD.append('header {')
    newD.append('position: fixed; top: 0; overflow: avoid; text-align: center; }')
    newD.append('.content-block, p {')
    newD.append('page-break-inside: avoid;')
    newD.append('position: relative;')
    newD.append('width: 100%;')
    # newD.append('top:1em;   //match size of header')
    newD.append('left:0px;')
    newD.append('right:0px; }')
    newD.append('html, body {')
    newD.append('width: 8.5in; height: 11in; }')

    newD.append('.hidden-print {')
    newD.append('display: none; }')
    newD.append('}')
    # newD.append('table { border: none; border-collapse: collapse; }')
    # newD.append('td { border: 1px solid black; }')
    # newD.append('td table { border: none; }')
    # newD.append('.border-none {')
    # newD.append('border-collapse: collapse;')
    # newD.append('border: none;')
    # newD.append('width: 100%; cellspacing: 0; cellpadding: 2; align: Left;')
    # newD.append('}')

    newD.append('.border-none td {')
    newD.append('border: 1px solid black;')
    newD.append('}') 

    newD.append('body {')
    newD.append('font-size: 10px; font-family: arial;')
    newD.append('}')
    newD.append('</style>')
    newD.append('</head>')
    newD.append('<body>')
    newD.append('<button class="hidden-print" onClick="window.print()">Print</button>')

    newD.append('<header><font face="arial" size="+1">Wright State University | Center of Neuroimaging and Neuro-Evaluation of Cognitive Technology<br></br></font></header>')
    
                            
    return newD