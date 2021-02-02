import sys
import os
import time
import logging
import csv

import threading
import queue

import nest_asyncio
nest_asyncio.apply()
import twint

import pandas as pd

def _get_friends(q, fp, n_retries=1, suppress=True):
    '''
    Within a threaded queue, use twint to scrape the names of users followed
    by a given user, and save the list of results to a .csv file.

    NOTE: This function has to be called from within another process, as it is
    intended to be the target of a Thread object. See function `twint_in_queue`

    Parameters
    ----------
    q : a Queue object instance
        A reference to the queue object that this threaded function will interact with
    fp : string
        Provides the path where the file should be saved.
    n_retries : int
        The max number of attempts to make.  The default value of 1 corresponds
        to a single attempt and makes no repeats should the first fail.
    suppress : bool
        If True, attempts to hide the critical warnings printed by twint, 
        which seem to occur even if the code is successful.
    '''
    while True:
        username = q.get() # retrieve username from queue
        attempt = 0
        filepath = fp+'friends_'+username+'.csv' # combine full path and name of file to be saved
        success = False

        if suppress:
            logger = logging.getLogger()
            logger.addHandler(logging.NullHandler)
            logger.propagate = False
        
        while not success:
            print('Attempt #'+str(attempt+1)+' to get friends of @'+username)
            c = twint.Config()
            c.Username = username
            c.User_full = False # Setting User_full=True seems to break the code, no idea what its intended outcome is
            c.Hide_output = True
            c.Store_csv = True
            c.Output = filepath

            twint.run.Following(c)

            if attempt<n_retries:
                if os.path.exists(filepath):
                    success=True
                    print('Results for @'+username+' saved to: '+filepath)
                else:
                    attempt += 1
            else: success=True

        if suppress:
            logger.propagate = True

        q.task_done()

def _search_tweets_by_user(q, fp, date_range=(None,None), n_retries=1, suppress=True):
    '''
    Within a threaded queue, use twint to scrape tweets from the advanced search
    for a given user and save the list of results to a .csv file.

    NOTE: This function has to be called from within another process, as it is
    intended to be the target of a Thread object. See function `twint_in_queue`

    Parameters
    ----------
    q : a Queue object instance
        A reference to the queue object that this threaded function will interact with
    fp : string
        Provides the path where the file should be saved.
    date_range : 2-tuple
        If specified, the start and end dates of the period from which to scrape tweets.
        The tuple must be length 2, and contain either None, or strings with the date and
        time, so the format is "YYYY-MM-DD HH:MM:SS"
    n_retries : int
        The max number of attempts to make.  The default value of 1 corresponds
        to a single attempt and makes no repeats should the first fail.
    suppress : bool
        If True, attempts to hide the critical warnings printed by twint, 
        which seem to occur even if the code is successful.

    TODO: Add handling for when a date is not provided.
    '''
    while True:
        username = q.get()
        attempt = 0
        filepath = fp+'tweets_'+username+'.csv'
        success = False

        if suppress:
            logger = logging.getLogger()
            logger.addHandler(logging.NullHandler)
            logger.propagate = False

        while not success:
            print('Attempt #'+str(attempt+1)+' to get tweets of @'+username)
            c = twint.Config()
            c.Username = username
            
            if date_range[0] is not None: c.Since = date_range[0]
            if date_range[1] is not None: c.Until = date_range[1]
            c.Retweets = True
            c.Hide_output = True
            c.Store_csv = True
            c.Output = filepath

            twint.run.Search(c)

            if attempt<n_retries:
                if os.path.exists(filepath):
                    success=True
                    print('Results for @'+username+' saved to: '+filepath)
                else:
                    attempt += 1
            else: success=True

        if suppress:
            logger.propagate = True

        q.task_done()



def twint_in_queue(target, num_threads, queue_items, args=(), kwargs={}):
    '''
    Function for executing twint requests in threads.

    Parameters
    ----------
    target : func
        The function each thread will be executing.
    num_threads : int
        The number of threads to distribute the queue items to.
    queue_items : list
        A list of variables to be passed to the target function via the queue.
    args : tuple
        A set of arguments for the target function which remain constant
        between iterations
    kwargs : dict
        The keyword arguments to be taken by the target function.
    '''
    q = queue.Queue(maxsize=0)

    for i in range(num_threads):
        worker = threading.Thread(target=target, args=(q,*args), kwargs=kwargs)
        worker.setDaemon = True
        worker.start()

    for item in queue_items:
        q.put(item)

    q.join()

#####################################################################################

def join_tweet_csv(user_list, keyword):
    '''
    Parameters
    ---------- 
    '''
    all_handles = []
    all_users = []
    failed = []
    all_tweets = pd.DataFrame()
    for name in user_list:
        filepath = '../data/raw/'+keyword +'_'+'tweets' +'_'+name+'.csv'
        if os.path.exists(filepath):
            all_handles.append(filepath)
            temp_csv = pd.read_csv(filepath)
            all_tweets = pd.concat([all_tweets, temp_csv])
    return all_tweets

######################################################################################

def join_friends_csv(list_journalists,keyword):
    all_handles = []
    all_users = []
    failed = []
    for name in list_journalists:
        filepath = '../data/raw/'+keyword+'_friends_'+name+'.csv'
        if not os.path.exists(filepath):
            failed.append(name)
        else:
            with open(filepath, newline='') as f:
                reader = csv.reader(f)
                next(reader, None) # trying to fix the bug
                handles = list(reader)
                all_handles.extend([handle[0] for handle in handles])
                all_users.extend([name for handle in handles])
                print('@'+name+' follows '+str(len(handles))+' users.')

    print('\nTotal number of handles pulled: '+str(len(all_handles)))

    unique = len(set(all_handles))
    print('Number of unique twitter handles: '+str(unique))

    print('\nZero following in list for users: '+str(failed))
    df = pd.DataFrame(list(zip(all_users, all_handles)), 
                   columns =['screen_name', 'friend'])
    df['screen_name'] = df['screen_name'].str.lower()
    df['friend'] = df['friend'].str.lower()
    return df