import numpy as np
import pandas as pd
import pathlib

def hindex(citations):
    '''
    Function 

    Params
    ------
    

    Returns
    -------
    
    '''
    citations = sorted(citations, reverse=True)
    for idx, item in enumerate(citations, 1):
        if item < idx:
            break
    return idx - 1




def loop_csv_H_index(fp):
    '''
    Function 

    Params
    ------
    

    Returns
    -------
    
    '''
    df_like_count = pd.DataFrame()
    hdict = {}

    count = 0
    for path in pathlib.Path(fp).iterdir():
        if path.is_file():
            count += 1
            
    for csv_n in np.arange(0,count):
        df = pd.read_csv(fp + '/edu_user_timelines_subset_' + str(csv_n) + '.csv')
        df_like_count = pd.concat([df_like_count,df.groupby('screen_name')[['retweet_count', 'like_count']].sum()])
        df['retweets&likes'] = df['retweet_count'] + df['like_count']
        for user_name in list(df['screen_name'].unique()):
            like_list = list(df[df['screen_name']==user_name]['retweets&likes'].values)
            h= hindex(like_list)
            hdict[user_name]=h
    hdict = {k: v for k, v in sorted(hdict.items(), key=lambda item: item[1], reverse=True)}
    hdict_df = pd.DataFrame(hdict.items(), columns = ['screen_name', 'h-index_like&retweets'])
    
    return hdict