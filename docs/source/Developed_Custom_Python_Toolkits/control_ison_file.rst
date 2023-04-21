There are many custom toolkits that have been developed to provide broad processing capabilities across projects, MRI scanners, imaging parameters, and processing specifications. 
These toolkits utilize a common JSON architecture to describe such parameters. Some of these JSON files solely describe input parameters for processing functions while others detail custom inputs, and others are a combination of these. 
Each JSON file is detailed in the python functions described below.
4.1.	Control JSON File
-----------------------
A single JSON file describe various parameters for each project/program. This file is ‘instance_ids.json’ and is located at ‘/mnt/ss_rhb1/scratch’. The main structure of a JSON file is the definition of a key and a value. The keys serve as a search tool to gain access to the value it contains. These values can be Booleans, strings, integers or floats, lists, or arrays. Table 5 outlines the keys and their associated descriptions.
