Project Environment Setup
=========================

Setting up the Python environment
---------------------------------
To create the bare-bones of the Python environment in  the Anaconda prompt, run the following:

.. code-block:: bash

    conda create -n lear python=3.6

Once the new environment has been created, switch into it using

.. code-block:: bash

    conda activate lear

To populate the environment with the required packages, simply run the following in the prompt while in the top level of the repo directory;

.. code-block:: bash

    pip install requirements.txt


Python dependencies
-------------------
Due to current dependency conflicts with py2neo, the project requires a python version at or below 3.7.1.

The primary module dependencies of this project are:

* twint
* nest_asyncio
* tweepy
* py2neo
* pandas
* numpy
* tqdm
* nltk
* gensim
* spacy
* beautifulsoup
* sklearn
* wordcloud
* wikipedia
* Sphinx
* sphinx_rtd_theme

The full list of package dependencies (including versions) which result from this main set can be found in the :ref:`required-modules`.

Jupyter Notebooks & Plotly
--------------------------
Plotly is a python module which is excellent for creating interactive plots that allow you to visually inspect data in a way that would be incredibly challenging in matplotlib.
To get plotly up-and-running in a Jupyter Notebook (or Jupyter Lab) requires a few extra bits and bobs.

In your conda environment, first install  plotly, node.js and the node package manager with:

.. code-block:: bash

    pip install plotly==4.9.0

    conda install nodejs

Then, to get going in Jupyter Notebook, run:

.. code-block:: bash

    pip install jupyterlab "ipywidgets>=7.5"

Or if you are using notebooks in Jupyter Lab:

.. code-block:: bash

    # JupyterLab renderer support
    jupyter labextension install jupyterlab-plotly@4.9.0

    # OPTIONAL: Jupyter widgets extension
    jupyter labextension install @jupyter-widgets/jupyterlab-manager plotlywidget@4.9.0



Neo4j
-----
Note quirks of getting Neo4j going here.