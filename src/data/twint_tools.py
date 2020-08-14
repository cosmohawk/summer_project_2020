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

def _get_friends(q, fp, n_retries=1, suppress=True):
    '''
    Within a threaded queue, use twint to scrape the names of users followed
    by a given user, and save the list of results to a .csv file.

    NOTE: This function has to be called from within another process, as it is
    intended to be the target of a Thread object. See function `twint_in_queue`

    Params
    ------
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
            c.Output = filepath

            twint.run.Following(c)

            if attempt<nRetries:
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

    Params
    ------
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