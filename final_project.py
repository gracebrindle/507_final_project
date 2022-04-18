import csv
import requests
import json
import TwitterKeys
from requests_oauthlib import OAuth1
from collections import deque
from pyvis.network import Network
import networkx as nx

# Open CSV files
with open("/Users/gracebrindle/Desktop/si507/final_project/politician_dataset.csv", newline='') as f:
    reader = csv.reader(f)
    politician_data = list(reader) 

with open("/Users/gracebrindle/Desktop/si507/final_project/senate_sponsorship_analysis.csv", newline='') as f:
    reader = csv.reader(f)
    senate_data = list(reader) 

with open("/Users/gracebrindle/Desktop/si507/final_project/house_sponsorship_analysis.csv", newline='') as f:
    reader = csv.reader(f)
    house_data = list(reader) 

# Initialize global variables
bearer_token = TwitterKeys.Bearer_Token
client_key = TwitterKeys.API_Key
client_secret = TwitterKeys.API_Key_Secret
access_token = TwitterKeys.Access_Token
access_token_secret = TwitterKeys.Access_Token_Secret
oauth = OAuth1(client_key,
            client_secret=client_secret,
            resource_owner_key=access_token,
            resource_owner_secret=access_token_secret)

CACHE_FILENAME = "/Users/gracebrindle/Desktop/si507/final_project/cache.json"
CACHE_DICT = {}

class_dict_by_name = {}
class_dict_by_id = {}

class Politician:
    def __init__(self, name="No Name", twitter_username="No username", account_id = "No ID", sex="Unknown", birthplace="United States of America", age="Unknown", political_party="Unknown"):
         self.name = name
         self.twitter_username = twitter_username
         self.account_id = account_id
         self.sex = sex
         self.birthplace = birthplace
         self.age = age
         self.political_party = political_party


# Loop through the data and create a Politician object for each row of data
for politician in politician_data[1:]:
    new_politician = Politician(politician[0], politician[1], politician[3], politician[4], politician[5], politician[7], politician[9])
    # Append the Politician class to a dictionary
    class_dict_by_name[new_politician.name] = new_politician.account_id
    class_dict_by_id[new_politician.account_id] = new_politician

def bearer_oauth(r):
    """
    Method required by bearer token authentication.
    """
    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2RecentSearchPython"
    return r

def open_cache():
    ''' opens the cache file if it exists and loads the JSON into
    the CACHE_DICT dictionary.
    if the cache file doesn't exist, creates a new cache dictionary
    Parameters
    ----------
    None

    Returns
    -------
    The opened cache
    '''
    try:
        cache_file = open(CACHE_FILENAME, 'r')
        cache_contents = cache_file.read()
        cache_dict = json.loads(cache_contents)
        cache_file.close()
    except:
        cache_dict = {}

    return cache_dict

def save_cache(cache_dict):
    ''' saves the current state of the cache to disk

    Parameters
    ----------
    cache_dict: dict
        the dictionary to save
    
    Returns
    -------
    None
     '''
    dumped_json_cache = json.dumps(cache_dict)
    fw = open(CACHE_FILENAME,"w")
    fw.write(dumped_json_cache)
    fw.close()

def construct_unique_key(baseurl, params):
    ''' constructs a key that is guaranteed to uniquely and 
    repeatably identify an API request by its baseurl and params
    Parameters
    ----------
    baseurl: string
        The URL for the API endpoint

    params: dictionary
        A dictionary of param: param_value pairs

    Returns
    -------
    string
        the unique key as a string
    '''
    param_strings = []
    connector = '_'
    for k in params.keys():
        param_strings.append(f'{k}_{params[k]}')
    param_strings.sort()
    unique_key = baseurl + connector +  connector.join(param_strings)
    return unique_key

def make_request(baseurl, params):
    '''Make a request to the Web API using the baseurl and params

    Parameters
    ----------
    baseurl: string
        The URL for the API endpoint

    params: dictionary
        A dictionary of param: param_value pairs

    Returns
    -------
    string
        the results of the query as a Python object loaded from JSON
    '''
    response = requests.get(baseurl, params=params, auth=oauth)
    print(response.status_code)
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    return response.json()

def make_request_with_cache(baseurl, params, cache_dict):
    '''Check the cache for a saved result for this baseurl+params
    combo. If the result is found, return it. Otherwise send a new 
    request, save it, then return it.

    Parameters
    ----------
    baseurl: string
        The URL for the API endpoint

    params: dictionary
        A dictionary of param: param_value pairs

    Returns
    -------
    string
        the results of the query as a Python object loaded from JSON
    '''
    request_key = construct_unique_key(baseurl, params)
    if request_key in cache_dict.keys():
        print("cache hit!", request_key)
        return cache_dict[request_key]
    else:
        print("cache miss!", request_key)
        cache_dict[request_key] = make_request(baseurl, params)
        save_cache(cache_dict)
        return cache_dict[request_key]

def search_following(account_id):
    '''Retrieve a list of a user's friends from the Twitter API. 
    Sets the base URL and parameters for the search and creates a request.

    Parameters
    ----------
    account_id: string
        the ID number for the politician's Twitter account

    Returns
    -------
    string
        the results of the query as a Python object loaded from JSON
    '''
    CACHE_DICT = open_cache()
    baseurl = "https://api.twitter.com/1.1/friends/ids.json"
    params = {'user_id': account_id}
    results = make_request_with_cache(baseurl, params, CACHE_DICT)
    return results

def prompt():
    '''Prompt the user to enter the name of a politician and search

    Parameters
    ----------
    None

    Returns
    -------
    None'''
    
    print(" ")
    politician = input("Please enter the name of the American politician you would like to search or 'exit' to quit: ")

    if politician == "exit":
        exit()
    
    else:
        create_network(politician)

# Search for the network of a particular politician
def search(politician):
    '''Finds the input politician in the dataset and returns necessary objects

    Parameters
    ----------
    politician: string
        name of the politician to search

    Returns
    -------
    friend_objects
        list of accounts (Politician objects) that the politician follows on Twitter
        
    politician_object
        the Politician object that is connected to the input politician'''
    
    # Verify that the politician is in the dataset
    if politician in class_dict_by_name:

        print("")
        print("Commencing search for " + politician + "...")
        print("")

        # Fetch a list of friends from the Twitter API using the account ID
        politician_id = class_dict_by_name[politician]
        politician_object = class_dict_by_id[politician_id]
        print("Twitter account located: " + politician_id)
        friend_results = search_following(str(politician_id))

        # Filter the friends by accounts that are in the dataset
        friend_ids = []
        for account_id in friend_results["ids"]:
            if str(account_id) in class_dict_by_id:
                friend_ids.append(account_id)

        # Convert the friend IDs into objects and store them in a list
        friend_objects = []
        for id in friend_ids:
            friend_objects.append(class_dict_by_id[str(id)])
        
        print("")
        print(politician + " follows:")
        for friend in friend_objects:
            print(friend.name + ", " + friend.political_party)

        return friend_objects, politician_object
        
    else:
        print("")
        print("Error: Could not locate the politician's Twitter account. Please re-enter the politician's name")
        print("")
        prompt()

def create_network(politician):
    visited_set = set()
    queue = deque()
    count = 0 

    friend_objects, politician_object = search(politician)
    queue.append(politician_object)
    network = Network(height='750px', width='100%', bgcolor='#222222', font_color='white', heading="Twitter Network of American Politician " + politician_object.name)
    network.repulsion(node_distance=500, spring_length=200)
    # *** TO DO **** 
    # Add arrows to edges going in the direction of 'to'
    # Change color of edge when selected to something more visible
    # Change color of edges to white
    # Add ideology scale and state
    # Differentiate primary politicians from friends (node border?)

    while queue and count < 15:
        count += 1
        current_politician = queue.popleft()
        friend_objects, politician_object = search(current_politician.name)

        if current_politician.political_party == "Democratic Party" or "California Democratic Party" or "Utah Democratic Party" or "Minnesota Democratic-Farmer-Labor Party" or "Maine Democratic Party":
            central_node_color = "blue"
        elif current_politician.political_party == "Republican Party" or "Republican Party of Iowa" or "Oregon Republican Party" or "Colorado Republican Party" or "California Republican Party":
            central_node_color = "red"
        else:
            central_node_color = "yellow"


        network.add_node(current_politician.account_id,
                        label=current_politician.name,
                        color=central_node_color,
                        borderWidth='3px',
                        title='<h1>' + current_politician.name+'</h1>' + 
                                '<ul>' + 
                                '<li>Twitter username: '+ current_politician.twitter_username + '</li>'
                                '<li>Party: ' + current_politician.political_party + '</li>'
                                '<li>Age: ' + current_politician.age + '</li>'
                                '<li>Gender: ' + current_politician.sex + '</li>')
    
        visited_set.add(current_politician.account_id)

        for object in friend_objects:
            if object.political_party == "Democratic Party":
                node_color = "blue"
            elif object.political_party == "Republican Party":
                node_color = "red"
            else:
                node_color = "yellow"

            if object.account_id not in visited_set:
                network.add_node(object.account_id, 
                                label=object.name, 
                                color=node_color,
                                title='<h1>' + object.name+'</h1>' + 
                                '<ul>' + 
                                '<li>Twitter username: '+ object.twitter_username + '</li>'
                                '<li>Party: ' + object.political_party + '</li>'
                                '<li>Age: ' + object.age + '</li>'
                                '<li>Gender: ' + object.sex + '</li>')

                queue.append(object)

            network.add_edge(current_politician.account_id, object.account_id)

    for node in network.nodes:
        # node['size'] = str(len(network.neighbors(node['id'])) * 10) + 'px',
        node['title'] += "<br>Neighbors: <ul>"
        for neighbor in network.neighbors(node['id']):
            node['title'] += '<li>' + class_dict_by_id[neighbor].name + '</li>'
        node['title'] += "</ul>"

    print(network)
    network.show('/Users/gracebrindle/Desktop/si507/final_project/' + politician + '_twitter_network.html')

def main():
    prompt()
    
    
if __name__ == "__main__":
    main()