Project Environment Setup
=========================

Setting up the Python environment
---------------------------------

To create the bare-bones of the Python environment in  the Anaconda prompt, run the following:

.. code-block:: bash

    conda create -n lear python=3.6 nodejs

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
* wikipedia
* Sphinx
* sphinx_rtd_theme

The full list of package dependencies (including versions) which result from this main set can be found in the :ref:`required-modules`.

Neo4j
-----
Note quirks of getting Neo4j going here.