import csv
import requests
import json
import TwitterKeys
from requests_oauthlib import OAuth1
from collections import deque

# Open CSV files
with open("/Users/gracebrindle/Desktop/si507/final_project/politician_dataset.csv", newline='') as f:
    reader = csv.reader(f)
    data = list(reader) 

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

cache_filename = "cache.json"
cache_dict = {}

class_dict = {}

def bearer_oauth(r):
    """
    Method required by bearer token authentication.
    """
    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2RecentSearchPython"
    return r

def open_cache():
    ''' opens the cache file if it exists and loads the JSON into
    the FIB_CACHE dictionary.

    if the cache file doesn't exist, creates a new cache dictionary

    Parameters
    ----------
    None

    Returns
    -------
    The opened cache
    '''
    try:
        cache_file = open(cache_filename, 'r')
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
    The dictionary to save
    
    Returns
    -------
    None
     '''
    dumped_json_cache = json.dumps(cache_dict)
    fw = open(cache_filename,"w")
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

def make_request_with_cache(baseurl, params):
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
    Sets the base URL and parameters for the search and calls the make_request_with_cache function

    Parameters
    ----------
    account_id: string
        The URL for the API endpoint

    Returns
    -------
    string
        the results of the query as a Python object loaded from JSON
    '''
    baseurl = "https://api.twitter.com/1.1/friends/ids.json"
    params = {'account_id': account_id}
    results = make_request_with_cache(baseurl, params)
    return results

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
for politician in data[1:]:
    new_politician = Politician(politician[0], politician[1], politician[3], politician[4], politician[5], politician[7], politician[9])
    # Append the Politician class to a dictionary
    class_dict[new_politician.name] = new_politician

# Prompt the user to search for a politician
def prompt(class_dict):
    
    print(" ")
    politician = input("Please enter the name of the American politician you would like to search or 'exit' to quit: ")

    if politician == "exit":
        exit()
    
    else:
        search(politician, class_dict)

# # Implement a breadth-first search function
def search(politician, class_dict):

    if politician in class_dict:

        print("")
        print("Commencing search...")
        print("")

        # Fetch a list of friends from the Twitter API using the account ID
        friend_list = class_dict[politician].search_following()
        politician_friend_list = []

        # Include only other politicians in the list of results
        for friend in friend_list:
            if friend in class_dict:
                politician_friend_list.append(friend)
        
    else:
        print("")
        print("Error: Could not locate the politician's Twitter account. Please re-enter the politician's name")
        print("")
        prompt(class_dict)

def main():
    prompt(class_dict)
    cache_dict = open_cache()
    
if __name__ == "__main__":
    main()