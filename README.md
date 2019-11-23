# Disttributed Deadlock Detection and Resolution based on hardware clock
This is an implementation of Jean Mayo and Phil kearn's paper on distributed deadlock detection and resolution. This detection algorithm is token based and works on single resource model.

# How to run
To simulate just run .py file with input file as a command line argument.  
For example:  python aos_proj_1.py 3_deadlock.txt

# Input file format
Input file will be in the below format  
line 1 : #no_of_process #no_of_resources  
line 2 : process_id resource_id  
line 3: ...  
..........  
