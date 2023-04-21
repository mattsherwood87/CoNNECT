6.1.	Update a Database/Table
The mysql databases and accompanying tables can be updated using kaas_neuro_db_update.py. This function is set to update the tables daily at 3am (EST - 5hrs). The commands below specify different ways to utilize this function.
The command below will update all the tables for the “general” database (i.e., kbrcloud-mri-general):
~$ kaas_neuro_db_update.py -all
The command below will update the table for the AFRL-Single_Exposure project. The database will be determined from instance_ids.json:
~$ kaas_neuro_db_update.py -p single_exp
The above commands can be modified to include flags to show the version (-v | --version) and progress (--progress).
