
Data Collection
---------------

Webscraping Journalist Twitter handles

Requesting user profiles


Data Collection: Scraping friend lists
--------------------------------------
The friend lists are scraped using Twint (with the _get_friends function) and saved as individual csv for each journalist; the individual csvs are then joined using the function join_friends_csv. The _get_friends function is used in combination with then twint_in_queue function which uses multi-threading on multiple cores (the number of cores need to be assigned as a function argument). This set up speeds up the process (the Twitter API has more limitations for dowloading lists of friends/followers and would therefore be slower). It has to be noted that if you want to abort the process while the twint_in_queue function is running, you will need to interrupt and restart your kernel, and delete from the folder the files that were produced because they might be incomplete lists of friends.


Data Collection: Requesting user tweets
---------------------------------------
We included in this section of the pipeline functions that can scrape tweets both with Twint and Twitter API. We did this because the two methods produce slightly different datasets and the pipeline user might be more interested one compared to the other.
Main differences between Twint and Twitter API:

**Twint**:

* it has no limitation on the amount of tweets that can be scraped
* the tweet search can be costomized for a specific time period
* for each tweet, we get the number of replies, times it has been retweeted, and likes
* the tweet dataset does not contain retweets (tweets that have been retweeted without adding any text)
* Twint provides a conversation_id, which is a reference to the first tweet of that particular conversation.
* in general, Twint provide less information for each individual tweet

**Twitter API**:

* this method has a maximum of 3200 tweets per user, and these will be the most recent ones
* the number of replies is not available for this type of dataset
* this type of dataset contains retweets and the information regarding who is the author of the tweet
* there is no reference to the conversation_id but we get a in_reply_to_status_id which represent the reference to the tweet the user responded to
* in general, the Twitter API provide a more rich and detailed set of information for each tweet
* it is also the fastest method between the two.