
Topic Modelling: Hashtag analysis
---------------------------------
The number and name of topics chosen for the word2vec analysis comes from dimensional reduction of the hashtags from the tweets. Looking at the graph, the number of topics can be chosen as where the steepest decline is (the elbow of the graph).  After the list of dimensionally reduced hashtags gets produced, it is good to assign hashtags to the topics manually. Once a topic list has been created, these terms can be searched for within the tweet text and keywords are found. Once tweets have been assigned a keyword they can be randomly sampled to balance the topics out. Obviously only sample as many tweets as there are in the topics and balance the classes.  It is good to plot the topics using word cloud plots for a sense check.

Topic Modelling: Doc2vec
------------------------
There are three models in the notebook:

* Distributed bag of words model (model_dbow),  analogous to continuous bag of words in word2vec
* Distributed memory (model_dmm), analogous to the ‘skip-gram’ model in word2vec
* Combined (model_new), the combined vectors of the above models

Run all three models and see what comes up with the best accuracy or F1 score and use this model for all future exploration.

To test the robustness of the doc2vec network that has been created, you can do some similarity checks and some vector arithmetic.  If this doesn’t make sense more training data may be required.

Topic Modelling: Applying to other tweets
-----------------------------------------
Load files that contain all the tweets and apply the model. Some basic analysis can be performed with some simple plots.  The output file can then be saved and fed into the graph database for filtering.
