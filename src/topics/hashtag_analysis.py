import sys

import numpy as np
import pandas as pd

from sklearn import feature_extraction as skfe
from sklearn import decomposition as skd

import matplotlib.pyplot as plt
plt.ion()

def get_ranked_wordcounts(words):
    '''
    Use the Counter class from Python collections to count the frequency
    of each word across a set of documents, represented by entries in a 
    Pandas Series.

    Parameters
    ----------
    words : Pandas Series
        A Series containing entries which are either strings or lists of 
        strings.  

    Returns
    -------
    counts_sorted : list
        A list of tuples, where tuple[0] is a word and tuple[1] is its' 
        frequency.
    '''
    # Flatten series of lists into list
    word_list = []
    for word in words:
        word_list.extend(eval(word) if isinstance(word, str) else word)

    from collections import Counter
    # Create a Counter instance, which identifies unique words and counts how often they are used.
    counts = Counter(word_lists)
    # rank the counts from highest to lowest and return
    counts_sorted = sorted(dict(counts).items(), key=lambda x: x[1], reverse=True)

    return counts_sorted

def vectorize_wordlists(words_lists):
    '''
    Generate sparse matrix of word-counts from Pandas series where each entry 
    is a list of words.

    Parameters
    ----------
    words_lists : Pandas Series
        A series of lists containing words to be one-hot encoded.

    Returns
    -------
    observations : Pandas DataFrame.sparse
        A sparse dataframe, where each row is a vectorised representation 
        of a document.
    '''
    cv = skfe.text.CountVectorizer()
    # Turn each list into one space-separated string
    corpus = words_lists.apply(lambda x: ' '.join(eval(x)) if isinstance(x, str) else ' '.join(x))
    # Apply count vectorisation to documents
    corpvec = cv.fit_transform(corpus)
    # Put results into sparse dataframe
    observations = pd.DataFrame.sparse.from_spmatrix(corpvec, index = words_lists.index, columns=cv.get_feature_names())

    return observations

def SVD_on_vectors(vectors, n_components=100, SVD_kwargs={}, plot=True):
    '''
    Use TruncatedSVD on vectorised documents as dimensionality reduction to 
    generate topics.

    Parameters
    ----------
    vectors : Pandas DataFrame.sparse
        A sparse, count-vectorized dataframe to be processed.
    n_components : int
        The number of dimensions to reduce the feature-space to
    SVD_kwargs : dict
        Apart from n_components, any other kwargs which can be passed to
        sklearn.decomposition.TruncatedSVD
    plot : bool
        If True, plots a bar chart showing the variance associated
        with each component.

    Returns
    -------
    vectors_reduced : Pandas DataFrame
        The input sparse matrix, vectors, transformed onto the 
        reduced-dimensions feature-space.
    components : Pandas DataFrame
        The vectors which map each component onto the original feature-space.
    '''
    # Add default values to kwargs if not declared
    default_kwargs = {'random_state':32498, 'n_iter':10}
    for key in default_kwargs.keys():
        if key not in SVD_kwargs:
            SVD_kwargs[key] = default_kwargs[key]
    # Initialise SVD
    svd = skd.TruncatedSVD(n_components=n_components, **SVD_kwargs)
    # Run fit_transform of SVD to get transformed space as dataframe
    vectors_reduced = pd.DataFrame(svd.fit_transform(vectors), index=vectors.index)
    # Extract component information as DataFrame
    components = pd.DataFrame(svd.components_, columns=vectors.columns)

    print('Sum of the explained variance = {:.3f}.'.format(svd.explained_variance_ratio_.sum()))

    if plot:
        plt.figure(figsize=(10,5))
        plt.bar([i for i in range(len(svd.explained_variance_ratio_))], svd.explained_variance_ratio_)
        plt.show()
    
    return vectors_reduced, components

def make_topic_keywords_from_svd(svd_vectors, threshold=0.2):
    '''
    Takes the results of TruncatedSVD and generates a list of keywords
    for each SVD component based on the component scores.

    Parameters
    ----------
    svd_vectors : Pandas DataFrame
        Dataframe containing the scores of each feature in the original space
        for each SVD component.
    threshold : float
        A significant threshold to apply on the selection of relevant keywords.
        Only keywords with a score greater than the threshold are returned for
        each component.
    
    Returns
    -------
    topic_kwds : Pandas DataFrame
        Dataframe where the index is the topic number, and the chosen keywords
        are contained as a list in the `keywords` column.
        Topics for which no keywords were returned are dropped from the
        returned dataframe.
    '''
    topic_kwds = pd.DataFrame(svd_vectors.apply(lambda x: svd_vectors.columns[x>threshold].tolist(), axis=1), 
                              columns=['keywords'], 
                              index=svd_vectors.index)
    topic_kwds.index.name = 'topic'
    
    topic_kwds = topic_kwds[topic_kwds.astype(str)['keywords'] != '[]'] # drop topics which are empty
    
    return topic_kwds

def label_data_by_topic(topic_space, threshold):
    '''
    Takes the SVD transformed data vectors and assigns a label based on most significant axis.
    Threshold can be used to further filter out noise.

    Parameters
    ----------
    topic_space : Pandas DataFrame
        DF which contains the results of dimension reduction by SVD.
    threshold : float
        The value above which label assignment is considered valid.
        To be used to remove spurious association of tweets with a topic.

    Returns
    -------
    labels : Pandas DataFrame
        Has one column which contains the topic label assigned to each tweet.
    '''
    label_series = topic_space.apply(lambda x: topic_space.columns[[a and b for a, b in zip(x>threshold, x==x.max())]], axis=1)
    labels = pd.DataFrame(label_series.apply(lambda x: x[0] if len(x)>0 else np.nan), columns=['labels',])
    
    return labels

def check_for_matches(tag_list, topic_list, number_other_topic):
    '''
    Compares a list of hashtags in tweets against those in each topic.
    
    Parameters
    ----------
    tag_list : Pandas DataFrame column
        A column containing hashtags
    topic_list : list of lists
        Each list in the list contains hashtags belonging to one topic.
    number_other_topic : interger
        The number to declare the 'other' topic, for example, -1, or one plus the number of topics
        
    Returns
    -------
    matches : Pandas series
        Series of a numbers, where the number corresponds to which topic the hastags fall into
    '''
    
    matches = []
    
    potential_matches = [bool(set(tag_list).intersection(set(topic))) for topic in topic_list]
    if any(potential_matches):
        matches.extend([i for i in range(len(potential_matches)) if potential_matches[i]])
    else:
        matches.append(number_other_topic)
    return matches

def check_keyword_matches(text, topic_list):
    '''
    Compares a list of 'keywords' in tweets.
    
    Parameters
    ----------
    text : Pandas dataframe column 
        containing the text that the keywords search is to be performed on
    topic_list : a list
        a list of topics
            
    Returns
    -------
    matches : Pandas series
        Series of a numbers, where the number corresponds to which topic the keywords fall into
    '''
    words = text.split(' ')
    matches = [word for word in words if word in topic_list]
    return matches

def produce_random_sample(df, df_column, number_of_samples):
    '''
    Pro.
    
    Parameters
    ----------
    df : Pandas dataframe
    
    df_column : Pandas dataframe column
    
    number_of_samples : number to sample in each group 
            
    Returns
    -------
    sample_df : Pandas dataframe
        dataframe containing random samples from original dataframe
    '''
    import random
    sample_df = pd.DataFrame()
    for label in df_column.unique():
        rnd_idx = random.sample(range(df[df_column==label].shape[0]), number_of_samples)
        sample_df = pd.concat([sample_df, df[df_column==label].iloc[rnd_idx]], axis=0)
    return sample_df

