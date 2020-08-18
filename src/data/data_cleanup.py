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