import sys
import time
import json

import pandas as pd

import tweepy

def connect_API(keys_file):
    '''
    Load twitter API credentials and return a tweepy API instance with which to
    make API calls.

    Params
    ------
    keys_file : str
        The path to a `*.json` file containing the twitter API credentials to
        be used.  See the notebook `store_twitter_credentials_as_json.ipynb`
        for more.
        
    Returns
    -------
    api : tweepy API object
    '''
    with open(keys_file, 'r') as file:
        creds = json.load(file)

    # Use credentials to set up API access authorisation
    auth = tweepy.OAuthHandler(creds['CONSUMER_KEY'], creds['CONSUMER_SECRET'])
    auth.set_access_token(creds['ACCESS_TOKEN'], creds['ACCESS_SECRET'])
    api = tweepy.API(auth, wait_on_rate_limit=True)
    
    return api

def request_user_info(api, screen_name=None, user_id=None):
    '''
    Request user info from the twitter API using the `get_user` method based
    on either the user's twitter handle or ID number.  

    Params
    ------
    api : tweepy.api.API object
        The API object to be used to make the request.
    screen_name : str
        Twitter handle of user to request information about. One of 
        `screen_name` or `user_id` must be provided.
    user_id : int
        ID number of user to request information about. One of `screen_name` 
        or `user_id` must be provided.

    Returns
    -------
    user_info : tweepy.models.User object
        A tweepy object where user information is stored as attributes.
    '''
    if screen_name not None:
        search = {'screen_name': screen_name}
    elif: user_id not None:
        search = {'user_id': user_id}
    else:
        Exception('No user name or ID was provided.')
    
    user = api.get_user(**search)

    return user

def tweepy_user_to_dataframe(user):
    '''
    Take in a tweepy User object and parse the data contained within to return
    a single-row Pandas dataframe containing the same attributes as columns.

    Params
    ------
    user : tweepy.models.User object
        The tweepy user information  object to be parsed into a dataframe.

    Returns
    -------
    user_df : DataFrame object
        A Pandas dataframe with one row and columns for each attribute.
    '''
    user_dict = vars(user) # First discriminate the attributes of the object
    # from it's methods. Then 'pop' to remove potentially problematic attrs.
    for key in ['_api', '_json', 'entities']:
        user_dict.pop(key)

    # Make dataframe out of remaining attributes. Specifying `index=0` ensures
    # data is parsed as a single entry (row). 
    user_df = pd.DataFrame(user_dict, index=0)

    return user_df