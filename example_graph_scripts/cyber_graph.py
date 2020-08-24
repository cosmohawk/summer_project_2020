## Example script to use graphdb library
## make sure input files are in the correct directory, i.e. the neo4j import directory
## AJH 2020

import numpy as np
import pandas as pd
import graphdb_dev as gdb

# start with an empty graph
graph = gdb.get_graph(new_graph=True) 

# load in tweet information
print('Loading in tweets and drawing (Tweet) nodes')
fn_tweets = 'standardised_cyber_tweets_19082020.csv'
gdb.load_tweets(fn_tweets ,graph) 

# lowd in user information
print('Loading in user information and drawing (Person) nodes')
fn_users = 'cyber_user_profiles_tst.csv'
gdb.load_users(fn_users ,graph)

# draw edges between users and their tweets
print('Drawing [POSTS] edges')
gdb.get_posts(graph)

# load in friend information
print('Loading in friends info and drawing [FOLLOWS] edges')
fn_friends = 'cyber_journalist_friends_2_0.csv'
gdb.load_friends(fn_friends,graph)

# load in mentions information
print('Loading in mentions and drawing [MENTIONS] edges')
fn_mentions = 'twint_cyber_16082020_mentions.csv'
gdb.load_mentions(fn_mentions,graph)

# run Page rank using follower and mention edges
print('ruuning page rank')
nodelist = ['Person','Tweet']
edgelist = ['FOLLOWS','MENTIONS']
page_rank_friends_mentions = gdb.run_pagerank(nodelist,edgelist,graph)

# when testing, sometimes n_followers is empty, in which case give it a random integer
not_strings = [type(n)!=str for n in page_rank_friends_mentions['n_followers']]
page_rank_friends_mentions['n_followers'][not_strings]=np.random.randint(1,500000,len(not_strings))

# get a weighted random sample of users
n_sample = 20
fields = ['rank']
exponents = [2]
sample = gdb.get_multiple_weighted_sample(page_rank_friends_mentions,n_sample,fields,exponents)

# print sample
print(sample)


