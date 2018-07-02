# Challenge Summary

Build a program to analyze purchases from within a users social network.
Input data includes both batch and stream logs in .json format; actions which each user can take include adding and deleting a friend from their social network,and also making purchases.


The goal is to analyze recent purchases of a user's network, out to some designated degree of connectedness, and then determine if a user's purchase is anomolous with respect to the users' friend's purchases.

The goal is described in ChallengeSummary.MD


### Input Data ###

The format for both the batch and stream log data are very similar. The .json formatted file
records an action that a user has performed. 

Batch data:

Batch data is read in large "batches". This will make up a historical log of the users data, used to build the social network.

Stream data:

Is read in as a streaming file; with each new line in the stream log, the graph is updated with new actions (additions/deletions from a users social network). Anytime a user makes a new purchase, the anomoly detection analysis will be performed.


### General Data Structures ###

Two main classes are used to store the user information and handle the anomoly detection analysis.
These data structures can be found in graphClasses.py 

# Graph

A simple graph, called Graph(), will be constructed to keep track of any friendships between users.

A dictionary will be initalized to keep track of the graph. Each user, identified by their unique user ID,will be a key in the dictionary, with a list of their neighbors (their unique user IDs), stored as a value in the dictionary.

The graph will be constructed primarily in the batch processing step. Streaming data will come in with additional changes to the graph, in "real time".

Methods of the graph class include basic graph-building functions. (e.g. adding users (keys) to the graph dictionary, adding friendships (mutually adding a user to the neighbor list of another) and conversely removing friendships (mutually deleting a user from the neighbor list of another).

An important method of this class is the DFS function. This allows us to search the graph starting at a given user, and returns the users within a certain degree of connectedness from that user.
This is a Depth-first search of the graph.


# Purchase Analysis

A second data structure will be used to deal, primarily with the purchase analysis functionality.
This structure is called PurchaseAnalysis().

It is similarly a dictionary-based structure, where each in the network is added with the unique user ID as a key. With each key, an associated heap of their recent purchases is stored. 

The size of the heap is kept fairly small to 3 times the size of the threshold value for the number of purchases used in the purchase analysis (this was an arbitrary choice for the size, but can be altered later if there is a need for later analyses).

When a new purchase is made by a user, it is added to that user's heap, based on the timestamp of the purchase. The heap is resized at some batch and stream frequency, and therefore contains only 3xThreshold number of most recent purchases.

When a new purchase is read in from the stream log file, the DFS method is called to find friends within a degree of connectedness. Then, the purchase heaps are accumulated for each of the friends found in the DFS search. The friends' purchases are then heapified, and the Threshold number of most recent purchases are then analyzed to find the mean and standard deviation of the purchases. If the new purchase is larger than  mean + 3 x standard deviation, we deem the purchase anomolous and flag the purchase.












