import sys

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

    Returns
    -------
    '''
