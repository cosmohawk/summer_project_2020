import sys
import time
import json

import pandas as pd

import tweepy

def request_user_info(api, screen_name=None, user_id=None, api_delay=True):
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
    api_delay : bool
        If true, add a sleep delay to pace API requests within rate limits.
        Rate limit info for user profile requests is 900/15 mins

    Returns
    -------
    user_info : dict
        A python dict where user information is stored under named keys.
    '''
    # Go through and check whether ID or name has been provided
    if screen_name not None: 
        search = {'screen_name': screen_name}
    elif: user_id not None:
        search = {'user_id': user_id}
    else:
        Exception('No user name or ID was provided.')
    
    user = api.get_user(**search) # API call to get user info
    if api_delay:
        time.sleep(1)

    # Convert tweepy user object into dict that can be stored as json
    user_info = vars(user) 

    # eject keys which certainly provide no additional info
    for key in ['_api', '_json']: 
        user_info.pop(key)

    return user_info

def batch_pull_user_info(api, users_list, kwargs):
    '''
    Get user info for a set of users.  

    '''
    users_data = {}

    for user in users_list:
        users_data[user] = request_user_info(api, )

    return users_data

def save_user_info_to_json(user_data, filename):
    '''

    '''

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

    TODO:
    -----
    -Rework this function, and maybe move it completely, to work with dicts/
    json format
    -Abstract the selection of important attributes to the user level and 
    improve interactivity/customisation.
    '''
    user_dict = vars(user) # First discriminate the attributes of the object
    # from it's methods. Then 'pop' to remove potentially problematic attrs.
    for key in ['_api', '_json', 'entities']:
        user_dict.pop(key)

    # Make dataframe out of remaining attributes. Specifying `index=0` ensures
    # data is parsed as a single entry (row). 
    user_df = pd.DataFrame(user_dict, index=0)

    return user_df

