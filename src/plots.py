import sys

import numpy as np
import pandas as pd

from sklearn import manifold as skm

from PIL import Image
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import matplotlib.pyplot as plt
plt.ion()

def wordcloud_plot(text, filename=None, cloudargs={}):
    '''
    Displays and saves a wordcloud plot. 

    Parameters
    ----------
    text : str
        The text to be parsed in the wordcloud.
    filename : str
        If used, also saves a copy of the wordcloud to file as specified
        in the string.
    cloudargs : dict
        A list of keywords that can be passed to WordCloud if deviating from defaults.

    Returns
    -------
    fig : matplotlib figure
        A hook to the figure to make tweaks if wanted.
    '''
    default_kwargs = {'collocations':False, 'width':1000, 'height':700, 'background_color':'white', 'min_font_size':10}
        for key in default_kwargs.keys():
            if key not in cloudargs:
                cloudargs[key] = default_kwargs[key]

    wordcloud = WordCloud(**cloudargs).generate(text)

    fig, ax = plt.subplots(1,1, tight_layout=True)
    fig.set_size_inches(8,8)
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')
    fig.show()

    if filename is not None:
        fig.savefig(filename+'.jpg', dpi=300)

    return fig

def make_tSNE_projection():
    '''

    '''

    tsne = skm.TSNE(n_components=2, init='random',
                            random_state=0, n_jobs=6, perplexity=50, n_iter=5000, learning_rate=400)
    tsneout = tsne.fit_transform(hashtag_dimred)