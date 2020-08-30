import sys

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


