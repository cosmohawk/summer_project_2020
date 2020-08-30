import sys

import pandas as pd

from sklearn import feature_extraction as skfe
from sklearn import decomposition as skd

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
    cv = skfe.CountVectorizer()
    # Turn each list into one space-separated string
    corpus = words_lists.apply(lambda x: ' 'join(eval(x)) if isinstance(x, str) else ' '.join(x))
    # Apply count vectorisation to documents
    corpvec = cv.fit_transform(corpus)
    # Put results into sparse dataframe
    observations = pd.DataFrame.sparse.from_spmatrix(corpvec, index = words_lists.index, columns=cv.get_feature_names())

    return observations

