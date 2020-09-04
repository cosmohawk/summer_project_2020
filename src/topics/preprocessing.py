import sys
import re
import nltk


def tokenize_text(text, x):
    '''
    Convert  string `text` into a list of word tokens.
    Removes stopwords and words that are too short.

    Parameters
    ----------
    text : str
        The text string to be tokenized.
    x : interger or variable
        the minimum length of words to be included
    Returns
    -------
    tokens : list of strings[InternetShortcut]
URL=https://github.com/S2DSLondon/Aug20_Ditchley/stargazers

        `text` broken up into tokens.
    '''
    tokens = []

    for sent in nltk.sent_tokenize(text):
        for word in nltk.word_tokenize(sent):
            if (len(word) >= x): 
                tokens.append(word)

    return tokens

