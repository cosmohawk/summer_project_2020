import numpy as np
import pandas as pd

import os

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




def loop_csv_H_index(src_dir,dest_dir, keyword):
	if not os.path.exists(dest_dir):
		os.makedirs(dest_dir)
	df_like_count = pd.DataFrame(columns= ['retweet_count','like_count'])
	hdict = {}
	files = [file for file in os.listdir(src_dir) if os.path.isfile(os.path.join(src_dir, file))]# build list of files to iterate through
	for file in files:
		df = pd.read_csv(os.path.join(src_dir, file), low_memory=False)
		df_no_rt = df.rt_id.isnull()
		df_like_count = pd.concat([df_like_count,df[df_no_rt].groupby('screen_name')[['retweet_count', 'like_count']].sum()])
		df['retweets&likes'] = df[df_no_rt]['retweet_count'] + df[df_no_rt]['like_count']
		for user_name in list(df['screen_name'].unique()):
			like_list = list(df[df['screen_name']==user_name]['retweets&likes'].values)
			h= hindex(like_list)
			hdict[user_name]=h
	hdict = {k: v for k, v in sorted(hdict.items(), key=lambda item: item[1], reverse=True)}
	hdict_df = pd.DataFrame(hdict.items(), columns = ['screen_name', 'h-index_like&retweets'])
	hdict_df.to_csv(os.path.join(dest_dir, keyword + '_h_index_users.csv'), index=False)
	df_like_count.index.name = 'screen_name'
	df_like_count.to_csv(os.path.join(dest_dir, keyword + '_like_rt_count_users.csv'), index=True)
	#return hdict_df
	#return df_like_count#hdict_df.to_csv(os.path.join(dest_dir, keyword + '_h_index_users.csv'), index=False)