import numpy as np
import pandas as pd
from py2neo import Graph

def get_graph(new_graph=True):
    '''
    Load an existing neo4j database or create a new one and return a graph object

    Params
    -------
    new_graph :  boolean
        True if a fresh graph is wanted, i.e. if the user wants to clear the database

    Returns
    -------
    graph : a py2neo graph class
    '''

    graph = Graph("bolt://localhost:7687", user="neo4j", password="tweetoftheday")
    graph.begin()

    if new_graph==True:
        graph.delete_all()

    return graph

def load_tweets(filename, graph):
    ''' 
    Load tweets into the graph database as nodes. Uses 'CREATE' therefore duplicate
    nodes may be created if items are already in the database.

    Params
    -------
    filename : str
        The path to a '*.csv' file containing tweet data

    graph : graph
        The graph database into which the tweet data will be loaded

    Returns
    -------
    void
    '''

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
    '''
    function to load user information contained in a '*.csv' file into the graph database
    to be used when users are not already in the database

    Params
    -------
    filename : str
         name of file containing user information
    
    graph : graph

    Returns
    -------
    void
    '''
   
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

def load_existing_users(filename, graph):
    '''
    function to load user information contained in a '*.csv' file into the graph database
    to be used when users ARE already in the database
    
    Params
    -------
    filename : str
        name of file containing user information

    graph : graph

    Returns
    -------
    Void
    '''
    
    query_string = '''
    LOAD CSV WITH HEADERS FROM "file:///'''+filename+'''" AS row
    MATCH (p:Person) WHERE toLower(p.screen_name) = toLower(row.screen_name)
    SET p.user_id = row.user_id, p.name = row.name, p.user_description= row.user_description,
    p.user_friends_n= row.user_friends_n, p.user_followers_n= row.user_followers_n,
    p.prof_created_at= row.prof_created_at, p.favourites_count= row.favourites_count,
    p.verified= row.verified, p.statuses_count= row.statuses_count
    '''
    graph.run(query_string)
    return


def get_posts(graph):
    '''
    function to draw edges between Tweet and Person nodes based on user id

    Params
    -------
    graph : graph

    Returns
    -------
    Void
    '''

    query_string = '''// Create edges linking tweeters and tweets
            MATCH (t:Tweet), (p:Person)
            WHERE t.user_id = p.user_id
            MERGE (p)-[:POSTS]->(t)'''
    graph.run(query_string)
    return

def load_friends(filename,graph,new=False):
    ''' 
    Load friend information from a '*.csv' file into the databse, draw FOLLOWS edges
    
    Params
    -------
    filename : str
        location of file with friend information

    graph : graph
        graph onto which edges will be drawn

    new : boolean
        if True new nodes will be drawn if friends cannot be found in database
        if False only edges between existing Person nodes are drawn

    Returns
    -------
    Void
    '''

    if new == True:
        query_string = '''// match link between users and friends in the database, if friend doesnt exisit then create it
                LOAD CSV WITH HEADERS FROM "file:///'''+filename+'''" AS row
                MATCH (p:Person) WHERE toLower(p.screen_name) = toLower(row.screen_name)
                MERGE (n:Person {screen_name: toLower(row.friend)})
                MERGE (p)-[:FOLLOWS]->(n)'''
    else:
        query_string = '''// match link between users and friends in the database, don't create new person nodes
            LOAD CSV WITH HEADERS FROM "file:///'''+filename+'''" AS row
            MATCH (p:Person) WHERE toLower(p.screen_name) = toLower(row.screen_name)
            MATCH (p2:Person) WHERE toLower(p2.screen_name) = toLower(row.friend)
            MERGE (p)-[:FOLLOWS]->(p2)'''
    graph.run(query_string)
    return


def load_mentions(filename,graph):
    '''
    Loads mention information from a file and draws edges connecting Tweet and Person nodes

    Params
    -------
    filename : str
        location of '*.csv' file containing mentions information

    graph : graph
        graph on which edges will be drawn

    Returns
    -------
    Void
    '''
    query_string = '''// match link between tweets and mentions
            LOAD CSV WITH HEADERS FROM "file:///'''+filename+'''" AS row
            MATCH (t:Tweet) WHERE t.tweet_id = row.tweet_id
            MERGE (p:Person {screen_name: toLower(row.mentions)})
            MERGE (t)-[:MENTIONS]->(p)'''
    graph.run(query_string)
    return

def run_pagerank(nodelist,edgelist,graph,new_native_graph=True):
    '''
    Runs the page rank algorithm on the graph network

    Params
    -------
    nodelist : list of str
        list of node types to include in projection

    edgelist : list of str
        list of edge types to include in projection

    graph : graph
        graph on which algorithm is to be run

    new_native_graph : boolean
        If True makes a new native projection of the graph
        If False uses the existing projection

    Returns
    -------
    df : pandas DataFrame
         dataframe containing a list of user names and their rank
    '''    
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
                'my-graph','''+str(nodelist)+','+str(edgelist)+''',{
    relationshipProperties: 'weight'
  })
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

def get_weighted_sample(ranked_df,sample_size,field,weight_exponent=2):
    '''
    Gets a weighted random sample of users

    Params
    -------
    ranked_df : panadas dataframe
        contains the user names and the parameters on which to weight

    sample_size : int
        desired sample size

    field : str
        name of column containing weights

    weight_exponent : float
        the higher the weight exponent the stronger the weighting
        +ve => upweighting
        -ve => downweighting
        default is quadratic
    
    '''
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

def get_talk_about_edges(graph):
    '''
    Draw TALKS_ABOUT edges on the graph connecting Person nodes.
    Requires Tweet nodes, POSTS and MENTIONS edges to already be in the graph

    Params
    -------
    graph : graph

    Returns
    -------
    Void
    '''

    query_string = '''
                  MATCH path=(p1:Person)-[po:POSTS]->(t:Tweet)-[m:MENTIONS]->(p2:Person)
                  WHERE p1 <> p2
                  WITH p1,p2, COUNT(path) AS weight
                  MERGE (p1)-[i:TALKS_ABOUT]->(p2)
                  SET i.strength = weight/5
                  '''
    graph.run(query_string)

    return

def filter_users_by_keywords(keywords,graph):
    '''
    Function to select only twitter users with certain keywords in their bio (or screen name)
    
    Params
    -------
    keywords : list of str
        list of keywords to select users by
    
    graph : graph
    
    Returns
    -------
    df : pandas dataframe
        A dataframe containing the screen names of filtered users
    '''

    kw_str = ''

    for i in range(len(keywords)):
        if i == 0:
            kw_str += "WHERE n.user_description CONTAINS '"+keywords[i]+"' OR n.screen_name CONTAINS '"+keywords[i]+"' "
        else:
            kw_str += "OR n.user_description CONTAINS '"+keywords[i]+"' OR n.screen_name CONTAINS '"+keywords[i]+"' "

    query_string = '''MATCH (n:Person) 
                '''+kw_str+'''
                RETURN n.screen_name AS screen_name 
                ORDER BY screen_name ASC'''
    ans = graph.run(query_string)

    # put result into a dataframe                                                                                                                                                
    df = pd.DataFrame.from_records(ans,columns=['screen name'])

    return ans

def get_chi2(df):
    '''
    Calculate the chi2 of users based on the assumption that follower and friend numbers are lognormally distributed

    Params
    -------
    df : pandas dataframe
        contains user information

    Returns
    -------
    no_loners : pandas dataframe
        contains augmented user information with singularities (users with zero friends) removed
        should be same dimensions as df
    '''
    no_loners = df[df['user_friends_n'] != 0].copy()
    
    x = np.log(no_loners['user_friends_n'])
    y = np.log(no_loners['user_followers_n'])

    cov = np.cov(x, y)

    xbar = np.mean(x)
    ybar = np.mean(y)

    def chi2(x,y,xbar,ybar,cov):
        ''' calculate chi squared '''
        deltax = np.log(x) - xbar
        deltay = np.log(y) - ybar
        ans = np.dot(np.asarray([deltax,deltay]),np.dot(np.linalg.inv(cov),np.asarray([deltax,deltay])))
        return ans

    no_loners['chi2'] = no_loners.apply(lambda x: chi2(x['user_friends_n'],x['user_followers_n'],xbar,ybar,cov),axis=1)

    return no_loners

def excise_outliers(outlier_list,graph):
    '''
    Delete list of users and all their connections from a graph
    
    Params
    -------
    outlier_list : list of str
        list of user names of users to be deleted
        
    graph : graph
    
    Returns
    -------
    void
    '''
    for outlier in outlier_list:
        query_string = '''MATCH (p:Person)-[r]-() WHERE p.screen_name = "'''+outlier+'''" DELETE r, p'''
        graph.run(query_string)
    return

def boost_graph(niter,nsample,fields,exponents,kwargs):
    '''
    Function to randomly subsample users in the graph and to identify who these people are following
    if they are following other people already in the graph then follower edges are drawn in
    new users are not added to the graph.

    Params
    --------
    niter : int
        number of boosting iterations
    
    nsample : int
        number of random samples to take on each iteration
    
    fields : list of str
        fields on which sampling should be weighted (must be columns in dataframe)
        
    exponents : list of floats
        exponents to determine strength of weighting, 
        +ve => upweighted, -ve => downweighted
        default quadratic weights is 2
        
    kwargs : dict
        keywords for twint
        
    Returns
    --------
    Void
    '''

    for i in range(niter):
        print('boost iteration ',i+1)

        # use page rank to estimate centrality of users
        page_rank = gdb.run_pagerank(nodelist,edgelist,graph)
    
        # get weighted sample
        sample = gdb.get_multiple_weighted_sample(page_rank,n_sample,fields,exponents)

        # use twint to get friend information for members of the sample and write a file for each user
        tt.twint_in_queue(tt._get_friends, 3, list(sample['screen name']), args=('../data/raw/'+keyword+'_',), kwargs=kwargs)

        # concatinate the individual files into one file
        friends_csv = tt.join_friends_csv(list(sample['screen name']),keyword) 
        friends_csv.to_csv('../data/processed/'+keyword+'_journalist_friends_of_friends_'+str(i)+'.csv', index=False)

        # load new follower edges into the network, only include edges between existing members.
        load_friends('processed/'+keyword+'_journalist_friends_of_friends_'+str(i)+'.csv',graph)
    
    return

