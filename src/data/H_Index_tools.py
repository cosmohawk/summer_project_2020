import numpy as np
import pandas as pd

import os

def hindex(citations):
	'''
	Function that calculates an H-Index based on number of retweets and likes for each tweet. 
	The range of values of the H-Index will vary based on the maximum number of tweets dowloaded for each user. 
	For example, if we set the n_tweets to 200, a user that has 200 tweets that have been retweeted and liked 200 times or more will have 
	an H-Index of 199. A user without likes or retweets will have an H-Index of 0.

	Parameters
	------
	citations : list
		A list of the sum of likes and retweets per tweet per user.

	Returns
	-------
	idx : int
		H-Index value
	'''
	citations = sorted(citations, reverse=True)
	for idx, item in enumerate(citations, 1):
		if item < idx:
			break
	return idx - 1




def loop_csv_H_index(src_dir, dest_dir, keyword):
	'''
	Function that loops through the friends tweets downloaded with the API and calculate the H-Index for each user. 
	Retweets originally tweeted by other users are not used in the H-Index calculation

	Parameters
	------
	src_dir : str
		File path where all the friends tweets are stored
	dest_dir : str
		File path where the like&retweet dataframe count will be stored
	keyword : str
		Initial keyword used to search for journalists

	Returns
	-------
	df_like_count : DataFrame object
		Sum of likes and retweets for each user
	hdict_df : DataFrame object
		Dataframe of screen_name and H-Index
	'''
	if not os.path.exists(dest_dir):
		os.makedirs(dest_dir)
	df_like_count = pd.DataFrame(columns= ['retweet_count','like_count'])
	hdict = {}
	files = [file for file in os.listdir(src_dir) if os.path.isfile(os.path.join(src_dir, file))]# build list of files to iterate through
	for file in files:
		df = pd.read_csv(os.path.join(src_dir, file), low_memory=False)
		df_no_rt = df.rt_id.isnull()
		df_like_count = pd.concat([df_like_count,df[df_no_rt].groupby('screen_name')[['retweet_count', 'like_count']].sum()])
		df['retweets_likes'] = df[df_no_rt]['retweet_count'] + df[df_no_rt]['like_count']
		for user_name in list(df['screen_name'].unique()):
			like_list = list(df[df['screen_name']==user_name]['retweets_likes'].values)
			h= hindex(like_list)
			hdict[user_name]=h
	hdict = {k: v for k, v in sorted(hdict.items(), key=lambda item: item[1], reverse=True)}
	hdict_df = pd.DataFrame(hdict.items(), columns = ['screen_name', 'h_index_like_retweets'])
	hdict_df.to_csv(os.path.join(dest_dir, keyword + '_h_index_users.csv'), index=False)
	df_like_count.index.name = 'screen_name'
	df_like_count.to_csv(os.path.join(dest_dir, keyword + '_like_rt_count_users.csv'), index=True)