import csv
import requests
import os
import json
import TwitterKeys
from requests_oauthlib import OAuth1
from collections import deque

# Open CSV files
with open("/Users/gracebrindle/Desktop/si507/final_project/politician_dataset.csv", newline='') as f:
    reader = csv.reader(f)
    data = list(reader) 

# Initialize global variables
class_dict = {}
bearer_token = TwitterKeys.Bearer_Token

class Politician:
    def __init__(self, name="No Name", twitter_username="No username", account_id = "No ID", sex="Unknown", birthplace="United States of America", age="Unknown", political_party="Unknown"):
         self.name = name
         self.twitter_username = twitter_username
         self.account_id = account_id
         self.sex = sex
         self.birthplace = birthplace
         self.age = age
         self.political_party = political_party 

    # Searches for who a politician follows (aka their "friends")
    def search_following(self):
        search_url = "https://api.twitter.com/1.1/friends/ids.json"
        params = self.account_id
        response = requests.get(search_url, auth=bearer_oauth, params=params)
        print(response.status_code)
        if response.status_code != 200:
            raise Exception(response.status_code, response.text)
        return response.json()

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

def bearer_oauth(r):
    """
    Method required by bearer token authentication.
    """
    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2RecentSearchPython"
    return r

def main():
    prompt(class_dict)
    
if __name__ == "__main__":
    main()