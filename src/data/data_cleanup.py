import sys

import pandas as pd

def twint_mentions_to_df(twint_df):
    '''
    Function to search through twint tweet data for user mentions
    and return a dataframe containing a tweet id and mentioned username
    in each row.
    
    Params
    ------
    twint_df : Pandas DataFrame

    Returns
    -------
    tweet_mentions : Pandas DataFrame
        
    '''
    mentions = []
    temp_ids = twint_df['id'].values
    temp_mentions = twint_df['mentions'].values
    for i in range(len(temp_ids)):
        temp_list = list(temp_mentions[i].strip('][').replace("'","").split(', '))
        for mention in temp_list:
            if len(mention)>0:
                mentions.append([temp_ids[i], mention])
            
    tweet_mentions = pd.DataFrame(mentions, columns=['tweet_id', 'mentions'])
    return tweet_mentions

############################################################################################################################

def standard_tweet_dataset_setup(filename):
    #tweets_standard = name_of_the_array
    filename = pd.DataFrame(columns = [#tweet info
                                                'tweet_id', 
                                                'conversation_id', 'in_reply_to_status_id',
                                                'reply_to', 'in_reply_to_user_id', 'in_reply_to_screen_name',
                                                'user_id', 'screen_name',
                                                'tweet_created_at', 
                                                'text',
                                                'replies_count', 'retweets_count', 'likes_count', 
                                                'hashtags', 
                                                'retweet_text','topics']) #'favourite_count',
                                                #user info
                                               #'user_id', 'screen_name',  'name', 'location', 
                                               #'user_description', 'user_friends_n', 
                                               #'user_followers_n', 'favourites_count', 'verified', 'statuses_count'])
    return filename


############################################################################################################################

def fill_standard_tweet_dataset_with_twint(standard_df, twint_df):
    # Start assigning the columns
    #tweet and conversation ID
    standard_df['tweet_id'] = twint_df['id']
    #conversation ID (twint) or in_reply_to_status_id (API)
    standard_df['conversation_id'] = twint_df['conversation_id']
    #reply to or reply to status_id
    standard_df['reply_to'] = twint_df['reply_to']
    #user id and it's screen_name
    standard_df['user_id'] = twint_df['user_id']
    standard_df['screen_name'] = twint_df['username']
    #date of tweet
    standard_df['tweet_created_at'] = twint_df['date'] + ' ' + twint_df['time']
    #Tweet text
    standard_df['text'] = twint_df['tweet']
    # Replies - RT - likes count
    standard_df['replies_count'] = twint_df['replies_count']
    standard_df['retweets_count'] = twint_df['retweets_count']
    standard_df['likes_count'] = twint_df['likes_count']
    #Hashtags
    standard_df['hashtags'] = twint_df['hashtags']
    
    
    # Check that the columns that contain strings have all lowercases
    standard_df['reply_to'] = standard_df['reply_to'].str.lower()
    standard_df['screen_name'] = standard_df['screen_name'].str.lower()
    standard_df['hashtags'] = standard_df['hashtags'].str.lower()
    
    return standard_df

############################################################################################################################

def fill_standard_tweet_dataset_with_API(standard_df, API_df):
    # Start assigning the columns
    #tweet ID 
    standard_df['tweet_id'] = API_df['tweet_id']
    #conversation ID (twint) or in_reply_to_status_id (API)
    standard_df['in_reply_to_status_id'] = API_df['in_reply_to_status_id']
    #reply to (twint) or in_reply_to_user_id/'in_reply_to_screen_name'
    standard_df['in_reply_to_user_id'] = API_df['in_reply_to_user_id']
    standard_df['in_reply_to_screen_name'] = API_df['in_reply_to_screen_name']
    #user id and screen_name
    standard_df['user_id'] = API_df['user_id']
    standard_df['screen_name'] = API_df['screen_name']
    #date of tweet
    standard_df['tweet_created_at'] = API_df['tweet_created_at']
    #Tweet text
    standard_df['text'] = API_df['text']
    # Replies - RT - likes count
    standard_df['retweets_count'] = API_df['retweet_count']
    standard_df['likes_count'] = API_df['favourite_count'] # check that likes and favourite are the same thing!!!!
    #Hashtags
    standard_df['hashtags'] = API_df['hashtags']
    # RT text
    standard_df['retweet_text'] = API_df['retweet_text']


    # Check that the columns that contain strings have all lowercases
    standard_df['in_reply_to_screen_name'] = standard_df['in_reply_to_screen_name'].str.lower()
    standard_df['screen_name'] = standard_df['screen_name'].str.lower()
    standard_df['hashtags'] = standard_df['hashtags'].str.lower()   
    
    return standard_df