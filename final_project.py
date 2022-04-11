import csv
import requests
import os
import json
import TwitterKeys
from requests_oauthlib import OAuth1

# Open CSV files
with open("/Users/gracebrindle/Desktop/si507/final_project/politician_dataset.csv", newline='') as f:
    reader = csv.reader(f)
    data = list(reader) 

data_dict = {}

# Store data in a dictionary with Twitter account ID as the key
for politician in data[1:]:
    data_dict[politician[3]] = politician[0], politician[1], politician[4], politician[5], politician[6], politician[7], politician[9]

bearer_token = TwitterKeys.Bearer_Token

def bearer_oauth(r):
    """
    Method required by bearer token authentication.
    """
    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2RecentSearchPython"
    return r

# Searches for who a user follows (aka their "friends")
def search_following(account_id):
    search_url = "https://api.twitter.com/1.1/friends/ids.json"
    params = account_id
    response = requests.get(search_url, auth=bearer_oauth, params=params)
    print(response.status_code)
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    return response.json()

def main():
    json_response = search_following('18189966')
    print(json.dumps(json_response, indent=4, sort_keys=True))
    
if __name__ == "__main__":
    main()