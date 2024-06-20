1.1.1.	Perform Registration via FSL FLIRT
Registration is performed via FSL’s FLIRT algorithm. The command line below identifies how to perform registration:
~$ connect_flirt.py -p single_exp -s --progress --struc
Table 27. Description of kaas_dcm2nii.py arguments in the example.
NOTE: The “-s” option should only be supplied with the above option or when additional core resources are already active (i.e., in the event of a large number requiring conversion). To skip this, simply do NOT include the “-s” flag. 
NOTE: The kaas_flirt.py program utilizes nipype to execute FLIRT. Input options to the nipype interface are described in the project’s *_flirt_input.json file within the processing_scripts sub-directory in the project’s scratch directory. In addition to the FLIRT input options, this file contains search information for the structural images (using the key ‘struc_regexstr’) as well as additional inclusion (key ‘inclusionList’) and exclusion (key ‘exclusionList) search characteristics. The same file is also utilized for other registrations such as ASL, fMRI and DTI.
