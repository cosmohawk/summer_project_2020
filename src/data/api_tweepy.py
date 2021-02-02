import sys
import json
import tweepy

def connect_API(keys_file):
    '''
    Load twitter API credentials and return a tweepy API instance with which to
    make API calls.

    Parameters
    ----------
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