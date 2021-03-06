# Overview

This program visualizes a network for a given American politician 
based on who that politician follows on Twitter.

# Packages
The program uses the following packages:
- csv
- json
- requests
- deque
- Pyvis

# API Authentication
The program uses the Twitter API with oAuth to conduct the search. To run 
the program, the user should have a separate file called TwitterKeys.py 
with each of the keys necessary for authentication. They should use the 
following variable names:

1. Bearer_Token
2. API_Key 
3. API_Key_Secret
4. Access_Token
5. Access_Token_Secret

The program will automatically import this file and correctly assign the 
variables to their proper values. 

# Instructions
1. Create the TwitterKeys.py file if you have not already

2. Run the final_project.py program using command line

3. The program will prompt you to enter the name of a politician. Please 
enter the first and last name of the relevant politician in title case 
(e.g. Joe Biden)

4. Once the search is complete, the program will download an HTML file with the results to a local 
directory. It will create an HTML file for each search.

5. Open the HTML file in your browser to see the graph.

# Parameters and Limitations
1. The politician must be in the dataset to return a graph (see 
politician_dataset.csv for reference)

2. The Twitter API can only conduct 15 requests per 15 minute window. As a 
result, the program can only be run once every 15 minutes. 

3. Due to the requests limit, the program will only 
conducts a breadth-first search for the first 14 friends of a given 
politician.

4. Users may have to reset the file paths in the program to directories on their local computer.

# Data Structures
The data is represented as a graph using breadth-first search. Vertices consist of politiciansâ€™ Twitter accounts and the edges represent Twitter follows. To increase efficiency, the graph is limited to the accounts in the American politician dataset (approximately two thousand) and excludes other accounts. 

# Presentation
Politicians are color-coded by political party: Democrats are blue, 
Republicans are red, and third-party politicians are yellow. Edges are color-coded
based on the node they are coming from. 

Click on a node to learn more about the politician. Senators contain additional metadata including an ideology score and a leadership score. These two scores are based on an analysis completed by GovTrack and range from 0 (least conservative; least leadership) to 1 (most conservative, most leadership). 
