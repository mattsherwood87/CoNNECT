7.	Helpful MySQL Commands
These helpful commands can be executed on the master node:
7.1.	Login to MySQL
~$ mysql --login-path=client <database>
7.2.	Exit MySQL
mysql> exit
7.3.	Create Database
mysql> CREATE DATABASE <database_name>;
7.4.	Create Table
mysql> CREATE TABLE <table_name> (<column1_name> <column1_size> <column2_name> <column2_size>);
where size can be char(255), char(48), char(10), char(8), etc.
Alternatively, tables can be copied:
mysql> CREATE TABLE <new_table_name> AS SELECT * FROM <old_table_name>;
7.5.	List All Tables in Database
mysql> SHOW tables;
7.6.	Retrieve ALL Columns from a Table
mysql> SELECT * FROM <table_name>;
7.7.	Retrieve ALL Columns from a Table Matching String
mysql> SELECT * FROM <table_name> WHERE <column> REGEXP “<search_string>”;
7.8.	Determine Last Update Time
SELECT UPDATE_TIME FROM information_schema.tables WHERE TABLE_SCHEMA = 's3_mri_general' AND TABLE_NAME = 'AFRL_Single_Exposure_raw_files';
