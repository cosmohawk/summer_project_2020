## Example script to use graphdb library
## make sure input files are in the correct directory, i.e. the neo4j import directory
## AJH 2020

import numpy as np
import pandas as pd
import graphdb as gdb

# start with an empty graph
graph = gdb.get_graph(new_graph=True) 

# load in tweet and user information
fn_tweets = 'standardised_cyber_tweets.csv'
gdb.load_tweets(fn_tweets ,graph) 

# draw edges between users and their tweets
gdb.get_posts(graph)

# load in friend information
fn_friends = 'cyber_journalist_friends_2_0.csv'
gdb.load_friends(fn_friends,graph)

# load in mentions information
fn_mentions = 'twint_cyber_16082020_mentions.csv'
gdb.load_mentions(fn_mentions,graph)

# run Page rank using follower and mention edges
nodelist = ['Person','Tweet']
edgelist = ['FOLLOWS','MENTIONS']
page_rank_friends_mentions = gdb.run_pagerank(nodelist,edgelist,graph)

# get a weighted random sample of users
n_sample = 20
field = 'rank'
exponent = 2
sample = gdb.get_weighted_sample(page_rank_friends_mentions,n_sample,field,exponent)

# print sample
print(sample)
