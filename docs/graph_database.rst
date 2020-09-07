
Inputting data to the Graph Database
------------------------------------

Install and configure Neo4j

Neo4j is a popular graph database, it stores the data in the same way it is layed out on the graph. This makes queerying the database very efficient.
Queeries to a neo4j database are made in the cypher language. Cypher is deliberately similar to SQL to make it easy to use for people who are familiar with SQL style relational databases.
Neo4j has a desktop development environment. It also has wrappers and interfaces with all the popular scripting languages.

Before running the database notebook one needs to have the Neo4j desktop development environment up and running. The Neo4j development app can be downloaded from here:

https://neo4j.com/download/?ref=try-neo4j-lp

There is also and online "sandbox" version, this is actually quite useful because it contains an example of twitter analytics. Neo4j can also be run from a cypher terminal, which comes with the desktop installation. We need to install the APOC and Graph Data Science Library plugins. These can be done via the desktop app.

On the desktop, create a new database by clicking "add database" and selecting "create local database". Then click "create", then "start", a new window will open.

Later we will want to be able to read in and write to different file formats. To do this we need to locate the configuration file and add the following couple of lines to location/conf/neo4j.conf

# Enable loading of json files                                                                                                                                                                  
apoc.import.file.enabled=true

# Enable exportation of files                                                                                                                                                                   
apoc.export.file.enabled=true
