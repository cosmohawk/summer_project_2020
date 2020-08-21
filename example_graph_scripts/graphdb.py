import numpy as np
import pandas as pd
from py2neo import Graph

def get_graph(new_graph=True):
    # load / declare the database
    # inputs: new_graph - if true then existing graph is cleared
    # outputs: graph - a py2neo graph object

    graph = Graph("bolt://localhost:7687", user="neo4j", password="tweetoftheday")
    graph.begin()

    if new_graph==True:
        graph.delete_all()

    return graph

def load_tweets_and_users(filename, graph):
    # function to load tweet information contained in a csv file into the graph database
    # inputs: filename - name of file containing tweet information
    # outputs: none

    # load in tweets and twitter user information
    query_string = '''
       LOAD CSV WITH HEADERS FROM "file:///'''+filename+'''" AS row
   
       CREATE (t:Tweet {tweet_id: row.tweet_id, conversation_id: row.conversation_id, user_id: row.user_id, 
       reply_to: row.reply_to, tweet_created_at_date: row.tweet_created_at_date, 
       tweet_created_at_time: row.tweet_created_at_time, text: row.text, replies_count: row.replies_count, 
       retweets_count: row.reteets_count, favourite_count: row.favourite_count, likes_count: row.likes_count,
       hashtags: row.hashtags, topics: row.topics})
   
       MERGE (p:Person {user_id: row.user_id, screen_name: toLower(row.screen_name), name: row.name, 
        user_description: row.user_description, user_friends_n: row.user_friends_n, user_followers_n: row.user_followers_n, 
       prof_created_at: row.prof_created_at, favourites_count: row.favourites_count, verified: row.verified, 
       statuses_count: row.statuses_count});
       '''
    # run cypher query
    graph.run(query_string)
    return

def load_tweets(filename, graph):
    # function to load tweet information contained in a csv file into the graph database
    # inputs: filename - name of file containing tweet information
    # outputs: none

    # load in tweets and twitter user information
    query_string = '''
       LOAD CSV WITH HEADERS FROM "file:///'''+filename+'''" AS row
   
       CREATE (t:Tweet {tweet_id: row.tweet_id, conversation_id: row.conversation_id, user_id: row.user_id, 
       reply_to: row.reply_to, tweet_created_at_date: row.tweet_created_at_date, 
       tweet_created_at_time: row.tweet_created_at_time, text: row.text, replies_count: row.replies_count, 
       retweets_count: row.reteets_count, favourite_count: row.favourite_count, likes_count: row.likes_count,
       hashtags: row.hashtags, topics: row.topics});
       '''
    # run cypher query
    graph.run(query_string)
    return


def load_users(filename, graph):
    # function to load tweet information contained in a csv file into the graph database
    # inputs: filename - name of file containing user information
    # outputs: none 
   
    # load in twitter user information
    query_string = '''
       LOAD CSV WITH HEADERS FROM "file:///'''+filename+'''" AS row
       MERGE (p:Person {user_id: row.user_id, screen_name: toLower(row.screen_name), name: row.name, 
        user_description: row.user_description, user_friends_n: row.user_friends_n, user_followers_n: row.user_followers_n, 
       prof_created_at: row.prof_created_at, favourites_count: row.favourites_count, verified: row.verified, 
       statuses_count: row.statuses_count});
       '''
    # run cypher query
    graph.run(query_string)
    return


def get_posts(graph):
    ## function to draw edges between Tweet and Person nodes based on user id
    # input: none
    #output: none

    query_string = '''// Create edges linking tweeters and tweets
            MATCH (t:Tweet), (p:Person)
            WHERE t.user_id = p.user_id
            MERGE (p)-[:POSTS]->(t)'''
    graph.run(query_string)
    return

def load_friends(filename,graph):
    # function to load friend information from a file
    # create person nodes for friends not already in the database
    # and to draw follower edges between person nodes 
    # input: filename
    # output: none

    query_string = '''// match link between users and friends in the database, if friend doesnt exisit then create it
            LOAD CSV WITH HEADERS FROM "file:///'''+filename+'''" AS row
            MATCH (p:Person) WHERE toLower(p.screen_name) = toLower(row.screen_name)
            MERGE (n:Person {screen_name: toLower(row.friend)})
            MERGE (p)-[:FOLLOWS]->(n)'''
    graph.run(query_string)
    return

def load_mentions(filename,graph):
    # function to load mention information from a file into the database
    # matches tweet and person nodes based on screen name
    # creates person node if person not already in the database

    query_string = '''// match link between tweets and mentions
            LOAD CSV WITH HEADERS FROM "file:///'''+filename+'''" AS row
            MATCH (t:Tweet) WHERE t.tweet_id = row.tweet_id
            MERGE (p:Person {screen_name: toLower(row.mentions)})
            MERGE (t)-[:MENTIONS]->(p)'''
    graph.run(query_string)
    return

def run_pagerank(nodelist,edgelist,graph,new_native_graph=True):
    # function to run the Page rank algorithm on the network
    # inputs: nodelist - a list of nodes of interest
    #         edgelist - a list of edges of interest
    # outputs: a dataframe containing a list of user names and their rank
    
    if nodelist[0] != 'Person':
        print("Ranking should be on Person nodes")
        return

    if new_native_graph==True:
        # clear the native graph
        query_string = '''CALL gds.graph.drop('my-graph')''' 
        graph.run(query_string)

        # make a new native graph
        query_string = '''// to run gds algorithms one needs to create a named graph
                CALL gds.graph.create(
                'my-graph','''+str(nodelist)+','+str(edgelist)+''')
                YIELD graphName, nodeCount, relationshipCount, createMillis'''
        graph.run(query_string)
    
    # run the Page rank algorithm
    query_string = '''// run pagerank and return the 100 highest scoring accounts
                CALL gds.pageRank.stream('my-graph') 
                YIELD nodeId, score
                WHERE EXISTS(gds.util.asNode(nodeId).screen_name)
                RETURN gds.util.asNode(nodeId).screen_name AS screen_name, score, gds.util.asNode(nodeId).user_followers_n AS user_followers_n
                ORDER BY score DESC, user_followers_n ASC, screen_name ASC'''##//''' LIMIT 100'''
    ans = graph.run(query_string)
    
    # put result into a dataframe
    df = pd.DataFrame.from_records(ans, columns=['screen name', 'rank', 'n_followers'])
    
    return df.copy()

def get_weighted_sample(ranked_df,sample_size,field,weight_exponent):

    # inputs: ranked_df - dataframe with rankings
    #         sample_size - number of samples required 
    #         field - column to weight on
    #         weight exponent - the higher the weight exponent the stronger the weighting
    # outputs: sample dataframe

    sum_of_ranks = np.sum(ranked_df[field]**weight_exponent)
    sample = np.random.choice(ranked_df['screen name'],size=sample_size,
                              replace=False,p=ranked_df[field]**weight_exponent/sum_of_ranks)

    lst = []
    for s in sample:
        index = ranked_df.index[ranked_df['screen name'] == s].tolist()
        lst.append(index[0])     
    sample_df = ranked_df.loc[lst].copy()


    return sample_df

def get_multiple_weighted_sample(ranked_df,sample_size,fields,weight_exponents):  

    weights = []
    for i in range(len(fields)):
        field = fields[i]
        ranked_df[field] = [float(n) for n in ranked_df[field]]
        exponent = weight_exponents[i]
        sum_of_ranks = np.sum(ranked_df[field]**exponent)
        weight = ranked_df[field]**exponent/sum_of_ranks
        weights.append(weight)

    weights = np.prod(weights,axis=0)/np.sum(np.prod(weights,axis=0))
    sample = np.random.choice(ranked_df['screen name'],size=sample_size,
                                    replace=False,p=weights)
     
    lst = []
    for s in sample:
        index  = ranked_df.index[ranked_df['screen name'] == s].tolist()
        lst.append(index[0])
    sample_df = ranked_df.loc[lst].copy()
    return sample_df
