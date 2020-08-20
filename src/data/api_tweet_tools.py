import sys
import time
import datetime

import pandas as pd
import tweepy

def request_user_timeline(api, user, api_delay=0.15, kwargs=None):
    '''
    Function to make a single API request from a user's timeline.
    If no keywords are provided, the request will return tweepy defaults, which
    will be the 20 most recent tweets of the user.

    Params
    ------
    api : tweepy.api.API object
        The API object to be used to make the request.
    user : str or int
        Either the screen-name or user-ID for the user whose timeline is being
        requested.
    api_delay : float
         Value represents the delay in seconds added after each API request.
         Is used to pad the processing time to keep within the API rate limits.
    kwargs : dict or None
        A dictionary containing keyword arguments to be passed to the api method.
    
    Returns
    -------
    TL_tweets : list object

    TODO
    ----
    - Check if try/except gets stuck if the api throws an error. I think with
    current code iterating through the timeline would result in trying the same
    request over and over again. 
    '''
    if kwargs is None:
        # If None, turn kwargs into empty dict so code doesn't break when no
        # extra arguments are needed
        kwargs = {}
    
    TL_tweets = []

    try:
        tweets = api.user_timeline(user, **kwargs)
    except:
        Exception('API request threw an error, returned object could be empty.')
        tweets = []
    
    if api_delay>0:
        time.sleep(api_delay) # Allowed to make 900 requests per 15 minutes, or 1 per second
    
    for tweet in tweets:
        TL_tweets.append({key: vars(tweet)[key] for key in list(vars(tweet).keys())[2:]}) # parse tweets from object into list

    return TL_tweets

