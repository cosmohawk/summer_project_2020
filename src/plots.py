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
    default_kwargs = {
        'collocations':False, 
        'width':1000, 
        'height':700, 
        'background_color':'white', 
        'min_font_size':10
    }
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

def make_tSNE_projection_of_SVD(df, kwargs={}):
    '''
    Project SVD-transformed data onto two dimensions for visualisation.

    Parameters
    ----------
    df : Pandas DataFrame

    kwargs : dict


    Returns
    -------
    coords : Pandas DataFrame
        The x- and y-coordinates of each tweet in the projected 2d-space. 
    '''
    defaults = dict(
        init='random',
        random_state=0, 
        n_jobs=2, 
        perplexity=50, 
        n_iter=5000, 
        learning_rate=400)
    for key in defaults.keys():
        if key not in kwargs:
            kwargs[key] = defaults[key]

    tsne = skm.TSNE(n_components=2, **kwargs)
    tsneout = tsne.fit_transform(df)

    coords = pd.DataFrame([tsneout[:,0], tsneout[:,1]], columns=['tsne_x', 'tsne_y'])

    return coords

def plot_tsne_projection(df, label_str, plotly=False, kwargs={}):
    '''
    Function to visualise a tSNE projection in 2 dimensions.

    Parameters
    ----------
    df : Pandas DataFrame
        A dataframe that must contain columns `tsne_x` and `tsne_y` generated
        by `make_tSNE_projection_of_SVD()` as well as a column which can be used
        for labels.
    label_str : str
        The name of the column in `df` to be used as labels for colouring.
    plotly: bool
        If True, use plotly for the visualisation.
        If False, use matplotlib.
    '''

    if plotly:
        defaults = dict(
            width=800,
            height=800,
            hover_name='screen_name',
            hover_data=['hashtags'],
            color_discrete_sequence=px.colors.qualitative.Bold
        )
        for key in defaults.keys():
            if key not in kwargs:
                kwargs[key] = defaults[key]

        import plotly.express as px

        px.scatter(viz, 'tsne_x', 'tsne_y', color=label_str, **kwargs)

    else: # Use Matplotlib
        fig, ax = plt.subplots(1,1)
        ax.scatter(df['tsne_x'], df['tsne_y'], c=df[label_str].astype(int), cmap='tab20')
        fig.set_size_inches(10,10)
        fig.show()
