import numpy as np
import pandas as pd
from py2neo import Graph
from src.data import twint_tools as tt

def get_graph(new_graph=True):
    '''
    Load an existing neo4j database or create a new one and return a graph object

    Parameters
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

    Parameters
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
       retweets_count: row.reteets_count, favourite_count: row.favourite_count, like_count: row.like_count,
       hashtags: row.hashtags, topics: row.topics, in_reply_to_screen_name: row.in_reply_to_screen_name, 
       in_reply_to_status_id: row.in_reply_to_status_id, rt_id: row.rt_id, quoted_status: row.quoted_status, quoted_status_id: row.quoted_status_id});
       '''
    # run cypher query
    graph.run(query_string)
    return

def load_users(filename, graph):
    '''
    function to load user information contained in a '*.csv' file into the graph database
    to be used when users are not already in the database

    Parameters
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
    
    Parameters
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

    Parameters
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
    
    Parameters
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

    Parameters
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

    Parameters
    -------
    nodelist : list of str
        list of node types to include in projection

    edgelist : list of str
        list of edge types to include in projection

    graph : graph
        graph on which algorithm is to be run

    new_native_graph : boolean
        If True makes a new native projection of the graph
        If False uses the existing projection.

    Returns
    -------
    df : pandas DataFrame
         dataframe containing a list of user names and their rank
    '''    
    if nodelist[0] != 'Person':
        print("Ranking should be on Person nodes")
        return

    if new_native_graph==True:
        query_string = '''CALL gds.graph.exists('my-graph') YIELD exists'''
        ex = graph.run(query_string)

        if [np.asarray(e) for e in ex][0] == False:
            print("creating new projection")
        else:
            #print("graph exists")
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
    df = pd.DataFrame.from_records(ans, columns=['screen_name', 'rank', 'n_followers'])
    
    return df.copy()

def get_weighted_sample(ranked_df,sample_size,field,weight_exponent=2):
    '''
    Gets a weighted random sample of users

    Parameters
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
    sample = np.random.choice(ranked_df['screen_name'],size=sample_size,
                              replace=False,p=ranked_df[field]**weight_exponent/sum_of_ranks)

    lst = []
    for s in sample:
        index = ranked_df.index[ranked_df['screen_name'] == s].tolist()
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
    sample = np.random.choice(ranked_df['screen_name'],size=sample_size,
                                    replace=False,p=weights)
     
    lst = []
    for s in sample:
        index  = ranked_df.index[ranked_df['screen_name'] == s].tolist()
        lst.append(index[0])
    sample_df = ranked_df.loc[lst].copy()
    return sample_df

def get_talk_about_edges(graph):
    '''
    Draw TALKS_ABOUT edges on the graph connecting Person nodes.
    Requires Tweet nodes, POSTS and MENTIONS edges to already be in the graph

    Parameters
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


def filter_users_by_keywords(keywords,graph,without=False):
    '''                                                                                                                                                                          
    Function to select only twitter users with certain keywords in their bio (or screen name)                                                                                    
                                                                                                                                                                                 
    Parameters                                                                                                                                                                       
    -------                                                                                                                                                                      
    keywords : list of str                                                                                                                                                       
        list of keywords to select users by                                                                                                                                      
                                                                                                                                                                                 
    graph : graph  
    
    without : boolean
        If set to true then returns a list of users without keywords in bio
                                                                                                                                                                                 
    Returns                                                                                                                                                                      
    -------                                                                                                                                                                      
    df : pandas dataframe                                                                                                                                                        
        A dataframe containing the screen names of filtered users    '''

    kw_str = ''

    if without == False:
        for i in range(len(keywords)):
            if i == 0:
                kw_str += "WHERE n.user_description CONTAINS '"+keywords[i]+"' OR n.screen_name CONTAINS '"+keywords[i]+"' "
            else:
                kw_str += "OR n.user_description CONTAINS '"+keywords[i]+"' OR n.screen_name CONTAINS '"+keywords[i]+"' "

    if without == True:
        for i in range(len(keywords)):
            if i == 0:
                kw_str += "WHERE NOT n.user_description CONTAINS '"+keywords[i]+"' AND NOT n.screen_name CONTAINS '"+keywords[i]+"' "
            else:
                kw_str += "AND NOT n.user_description CONTAINS '"+keywords[i]+"' AND NOT n.screen_name CONTAINS '"+keywords[i]+"' "                
                
    query_string = '''MATCH (n:Person)                                                                                                                                           
                '''+kw_str+'''                                                                                                                                                   
                RETURN n.screen_name AS screen_name                                                                                                                              
                ORDER BY screen_name ASC'''
    ans = graph.run(query_string)

    # put result into a dataframe
    df = pd.DataFrame.from_records(ans,columns=['screen name'])

    return df


def get_chi2(df):
    '''
    Calculate the chi2 of users based on the assumption that follower and friend numbers are lognormally distributed

    Parameters
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
    
    Parameters
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

def boost_graph(niter,nsample,fields,exponents,pagerank_params,keyword,kwargs):
    '''
    Function to randomly subsample users in the graph and to identify who these people are following
    if they are following other people already in the graph then follower edges are drawn in
    new users are not added to the graph.

    Attempting to find all the friends of friends may result in downloading hundreds of thousands or millions of profiles. The network gets exponentially bigger at each level of abstraction. We can avoid this by selecting a random sample of users in our database and seeing if they are following anyone else in our database. We can weight this random selection by, for example, their previously determined rank or the number of friends or followers they have. By repeating this process several times we can build complexity into our graph.

    Parameters
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
        
    pagerank_params : tuple
        parameters for pagerank

    kwargs : dict
        keywords for twint
        
    Returns
    --------
    Void
    '''

    nodelist, edgelist, graph = pagerank_params

    for i in range(niter):
        print('boost iteration ',i+1)

        # use page rank to estimate centrality of users
        page_rank = run_pagerank(nodelist,edgelist,graph)
    
        # get weighted sample
        sample = get_multiple_weighted_sample(page_rank,nsample,fields,exponents)

        # use twint to get friend information for members of the sample and write a file for each user
        tt.twint_in_queue(tt._get_friends, 3, list(sample['screen_name']), args=('../data/raw/'+keyword+'_',), kwargs=kwargs)

        # concatinate the individual files into one file
        friends_csv = tt.join_friends_csv(list(sample['screen_name']),keyword) 
        friends_csv.to_csv('../data/processed/'+keyword+'_journalist_friends_of_friends_'+str(i)+'.csv', index=False)

        # load new follower edges into the network, only include edges between existing members.
        load_friends('processed/'+keyword+'_journalist_friends_of_friends_'+str(i)+'.csv',graph)
    
    return

def load_topics(fn_topics,graph,threshhold):
    '''
    Function to read in file containing the results of the topic modelling and to load it onto the graph.
    Topics are assigned to nodes and edges drawn between users weighted by their association with that topic.
    (:Person)-[:TWEETS_ABOUT]->(:Topic)
    
    Parameters
    -------
    fn_topics : str
        location of file containing users and their topic weights
        
    graph : graph
    
    threshhold : float
        The minimum weight to assign to a TWEETS_ABOUT edge
        
    Returns
    -------
    Void
    
    '''
    query_string = '''LOAD CSV WITH HEADERS FROM "file:///'''+fn_topics+'''" AS row
    UNWIND keys(row) AS keyn
    MATCH (p:Person {screen_name: row.screen_name})
    WHERE toFloat(row[keyn]) >= '''+str(threshhold)+'''
    MERGE (t:Topic {name: keyn})
    CREATE (p)-[:TWEETS_ABOUT {frequency: toFloat(row[keyn])}]->(t)'''
    graph.run(query_string)
    
    return

def filter_by_topic(keyword,graph):
    '''
    Function returns a list of individuals associated with a particular topic.
    
    Parameters 
    -------
    
    keyword : str
        The topic one wishes to filter on
        
    graph : graph
    
    Returns
    -------
    
    names : pandas dataframe
        A list of user names associated with that topic
    '''

    query_string = '''MATCH (p)-[:TWEETS_ABOUT]->(t:Topic)
        WHERE t.name = "'''+keyword+'''" OR toLower(t.name) = "'''+keyword+'''"
        RETURN p.screen_name'''
    ans = graph.run(query_string)

    names = pd.DataFrame.from_records(ans,columns=['screen_name'])
    
    return names

def add_property(property_name,dataframe,graph):
    '''
    Routine to add a property to nodes in the graph.
    
    Parameters
    -------
    property_name : str
        The name of the property to be added to the node, 
        should be the name of a column heading in the dataframe.
        
    dataframe : pandas dataframe
        Dataframe containing at least the user names and the property to be added to these users
        
    graph : graph
    
    Returns
    -------
    Void
    '''
    for index, row in dataframe.iterrows():
        query_string = '''
        MATCH (p:Person) WHERE p.screen_name = "'''+row['screen_name']+'''"
        SET p.'''+property_name+''' = '''+str(row[property_name])+'''
        '''
        graph.run(query_string)
    return
    
def get_chi2_H_index(df):
    '''
    Routine to calculate the chi2 of each user based on the H index
    
    Parameters
    -------
    df : pandas dataframe
        Dataframe containing le H-index of users
        
    Returns
    -------
    no_loners : pandas dataframe
        Dataframe with added column representing the chi2 of users.
        Users with an H-index of zero are excised from the dataframe.
        
    '''
    no_loners = df[df['h_index_like_retweets'] != 0].copy()
    xvals = np.log(no_loners['h_index_like_retweets'])
    var = np.var(xvals)
    xbar = np.mean(xvals)
    def chi2(x):
        dx = np.log(x) - xbar
        chi2 = dx**2/var
        return chi2
    
    no_loners['chi2'] = no_loners.apply(lambda x: chi2(x['h_index_like_retweets']),axis=1)
    
    return no_loners.copy()

def order_conversations(graph):
    '''
    Depending on the source of data (the Twitter API or twint) tweets either contain a "conversation_id" or a "reply_to_status_id". These are different but related numbers. The "conversation_id" is the id of the first tweet in the conversation, the "reply_to_status_id" is the id of the tweet in the conversation preceding the current tweet. Tweets also contain timestamp information, thus even if we don't have the "reply_to_status_id" we can order tweets in the conversation.

    Parameters
    -------
    graph : graph

    Returns
    -------
    Void
    '''

    # start by finding tweets in the same conversation by matching conversation_id
    query_string = '''// Find tweets in the same conversation
            MATCH (t1:Tweet), (t2:Tweet)
            WHERE t1.conversation_id = t2.conversation_id
            AND t1.tweet_id <> t2.tweet_id
            AND t1.tweet_created_at_date <= t2.tweet_created_at_date
            AND t1.tweet_created_at_time < t2.tweet_created_at_time
            MERGE (t1)-[:CONVERSATION]->(t2)'''
    graph.run(query_string)

    # conversations should be a chain rather than a mesh, although very occasionally tweets may have the same time stamp
    query_string = '''// Find the direction of the conversation
            MATCH (t1)-[c1:CONVERSATION]->(t2), (t1)-[c2:CONVERSATION]->(t3) 
            WHERE t2.tweet_created_at_date < t3.tweet_created_at_date
            DELETE c2;'''
    graph.run(query_string)

    query_string = '''MATCH (t1)-[c1:CONVERSATION]->(t2), (t1)-[c2:CONVERSATION]->(t3) 
            WHERE t2.tweet_created_at_time < t3.tweet_created_at_time
            DELETE c2;'''
    graph.run(query_string)

    return
