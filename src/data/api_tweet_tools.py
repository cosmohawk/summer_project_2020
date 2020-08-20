import sys
import time
import datetime
import tqdm

import pandas as pd
import tweepy

def request_user_timeline(api, user, api_delay=0, kwargs=None):
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
    TL_tweets : list

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

def wrangle_tweets_into_df(tweet_list):
    '''

    '''
    user_data = []
    ents_data = []
    for tweet in tweet_list: # First, separate out the nested information
        user_data.append(vars(tweet.pop('user')))
        ents_data.append(tweet.pop('entities'))
    # Create temporary dataframes
    tmp_tweet_df = pd.DataFrame(tweet_list)
    rt_data = [vars(retweet) if hasattr(retweet, __dict__) else {} for retweet in list(tmp_tweet_df['retweeted_status'.values])]
    tmp_user_df = pd.DataFrame(user_data)
    tmp_ents_df = pd.DataFrame(ents_data)
    tmp_rt_df = pd.DataFrame(rt_data)
    # Edit and prune tweet data
    tmp_tweet_df.drop(['id_str', 'in_reply_to_status_id_str', 'in_reply_to_user_id_str', 'favorited', 'retweeted', 'retweeted_status'], 1, inplace=True) # drop columns that duplicate info
    tmp_tweet_df.rename(columns={'id':'tweet_id', 'created_at':'tweet_created_at', 'full_text':'text'}, inplace=True) # rename tweet id column
    #Edit and prune user data
    tmp_user_df.drop(tmp_user_df.columns.difference(['id','name', 'screen_name']), 1, inplace=True) # drop user info we don't want
    tmp_user_df.rename(columns={'id':'user_id'}, inplace=True) # rename user id col
    # Edit and prune entities data
    tmp_ents_df['hashtags'] = tmp_ents_df['hashtags'].apply(lambda x : [hashtag['text'] for hashtag in x]) # turn hashtags into list of strings
    tmp_ents_df['user_mentions'] = tmp_ents_df['user_mentions'].apply(lambda x : [usr['screen_name'] for usr in x])
    tmp_ents_df.rename(columns={'user_mentions':'mentions'}, inplace=True)
    # Edit and prune RT data
    tmp_rt_df['rt_user_id'] = tmp_rt_df['user'].apply(lambda x : x.id if hasattr(x, 'id') else None)
    tmp_rt_df['rt_screen_name'] = tmp_rt_df['user'].apply(lambda x : x.screen_name if hasattr(x, 'screen_name') else None)
    tmp_rt_df['rt_text'] = tmp_rt_df['full_text']
    tmp_rt_df.drop(tmp_rt_df.columns.difference(['id', 'rt_user_id', 'rt_screen_name', 'rt_text']), 1, inplace=True)
    tmp_rt_df.rename(columns={'id':'rt_id'}, inplace=True)
    # Concatenate Dataframes
    tweet_df = pd.concat([tmp_user_df, tmp_tweet_df, tmp_ents_df, tmp_rt_df], axis=1, sort=False)

    return tweet_df

def batch_request_user_timeline(api, user_list, filepath, chunk_size=500, kwargs={'count':200}):
    '''
    Function to sample the most recent tweets (up to 200) from the timelines of a
    list of users.  

    Params
    ------
    api : tweepy.API instance
        The API authorisation hook used to make the requests.
    user_list : list
        A list of user screen-names to request tweets from.
    filepath : str
        The location to store csv file outputs.
    chunk_size : int
        The number of users to collect in each subset of data.
    kwargs : dict
        The keyword arguments to be passed to `request_user_timeline()`
        See that function for details.
    '''
    N = len(user_list)

    with tqdm(total=N, desc='User timelines') as pbar: # Create Progress bar
        j=0
        while j*chunk_size < N: # Iterate over chunks until complete
            tweets = []
            for i, user in enumerate(user_list[j*chunk_size:(j+1)*chunk_size]):
                results = request_user_timeline(api, user, kwargs=kwargs)
                for tweet in results:
                    tweet.pop('author')
                tweets.extend(results)
                pbar.update(1)
            tweet_df = wrangle_tweets_into_df()
            full_path = filepath + 'user_timelines_subset_' + str(j) + '.csv'
            tweet_df.to_csv(full_path, index=False)
            j += 1
