4.3.	Generalized Python Data Check Functions
As in manualling processing data, automated routines can fail for unknown reasons. Often, these can be hard to detect especially within larger datasets. Custom routines have been developed to create simple spreadsheets which identify data existence on a subject and session basis. In these spreadsheets, a ‘1’ represents the data was found and ‘0’ represents missing or unprocessed data. Simple conditional formatting can be applied in Excel or similar CSV-style cell editors to more easily identify missing datasets rapidly.
4.3.1.	kaas_raw_data_check.py
Creates a spreadsheet of the raw data described and parsed via the project-specific function “<project_identifier>_get_dir_identifiers.py”. Output is written to the “processing_logs” folder within the project’s scratch directory as “<project_identifier>_raw_data_check.csv”.
4.3.2.	kaas_processed_data_check.py
Creates a spreadsheet identifying which processed data exists, parsed via the file identifiers JSON file (see Section 5.2.2). Output is written to the “processing_logs” folder within the project’s scratch directory as “<project_identifier>_processed_data_check.csv”.
