import sys
import re
import nltk

def tokenize_text(text):
    '''
    Convert  string `text` into a list of word tokens.

    Params
    ------
    text : str
        The text string to be tokenized.
        
    Returns
    -------
    tokens : list of strings
        `text` broken up into tokens.
    '''
    tokens = []

    for sent in nltk.sent_tokenize(text):
        for word in nltk.word_tokenize(sent):
            if (len(word) >= min_characters_word) & (word not in stop_words): 
                tokens.append(word)

    return tokens

