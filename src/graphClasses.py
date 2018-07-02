import heapq
import math
import sys
import time

from fileClasses import EV_TYPE

""" Object to hold recent purchases for each user, and perform analysis"""

class PurchaseAnalysis(object):

    def __init__(self, T, outfile):
        """ 
        Initialize with a file to print output to.
        T is the number of recent purchases to keep track of.
        """
        self.numRecentPurchases = T
        self.fpOut = open(outfile, 'w')
        self.purchase_dict = {}
    
    def addUser(self, usr):
        if usr in self.purchase_dict:
            return
        else:
            self.purchase_dict[usr] = []

    def passUsers(self, usrList):
        """ Initialize the dictionary with the users network, or update"""   

        for usr in usrList:
            self.addUser(usr)
    
    def getPurchaseComplete(self):
        """ Print all recent purchase"""
        return self.purchase_dict

    def reducePurchaseHeap(self):
        """ 
            Reduce the size of the purchase heap for each user.
            Do this periodically so that not storing increasingly 
            long purchase histories.
        """


        for usr in self.purchase_dict:
            heapLen = len(self.purchase_dict[usr])

            # if heap is very large, reduce the size to something manageable
            if heapLen > 3*self.numRecentPurchases:
                self.purchase_dict[usr] = heapq.nlargest(3*self.numRecentPurchases,self.purchase_dict[usr])


    def updatePurchaseDict(self, logItem):
        
        usr = logItem.usr1
        amount = logItem.value
        timestamp = logItem.stamp

        # error checking before updating heap
        if (timestamp is None) or (amount is None):
            return

        if usr not in self.purchase_dict:
            self.purchase_dict[usr] = []
        
        heapq.heappush(self.purchase_dict[usr], (timestamp,amount))
        


    def getMean(self, purchaseList):
        
        mean = 0.
        
        for ts, val in purchaseList:
            mean = mean + val
        
        mean = mean/ float(len(purchaseList))

        return mean

    def getStdev(self,purchaseList, mean):
        
        stdev = 0.

        for ts, val in purchaseList:
            tmp = mean - val
            tmp = math.pow(tmp, 2)
            stdev = stdev + tmp

        stdev = stdev / float(len(purchaseList) -1)
        stdev = math.sqrt(stdev)

        return stdev
    
    def getFriendsPurchases(self, friendList):

        """ Given results of DFS search, accumulate heap.
            This should be a temporary heap that sorts all of the most recent 
            purchases from all friends into a chronological order. 
        """

        tempHeap = []
        

        # loop through friendList
        for usr in friendList:
            
            for i in range(len(self.purchase_dict[usr])):
                item = self.purchase_dict[usr][i]
                heapq.heappush(tempHeap, item)


        heapLen = len(tempHeap)

        if heapLen < 2:
            print "Error: Not enough historical information to calculate!"
            return 


        if heapLen < self.numRecentPurchases:
            return heapq.nlargest(heapLen,tempHeap)
        
        else:
            return heapq.nlargest(self.numRecentPurchases,tempHeap)


    def getThreshold(self,purchaseList):
        
        mean = self.getMean(purchaseList)
        stdev = self.getStdev(purchaseList, mean)

        threshold = mean + 3*stdev

        return mean, stdev, threshold


    def isAnomolous(self, logItem, purchaseAnalysis):
        
        usr = logItem.usr1
        amount = logItem.value
        timestamp = logItem.stamp

        if (amount is None) or (timestamp is None):
            return

        mean,stdev,threshold = self.getThreshold(purchaseAnalysis)

        if amount > threshold:
            line = '{'+logItem.line+'}\n'
            self.fpOut.write(line)
    

class Graph(object):
    """ Graph data structure using a dictionary """

    def __init__(self,D):
        self.vert_dict = {}
        
        self.degree = D
        self.threshold = 0
        self.num_vertices = 0

    def __iter__(self):
        return iter(self.vert_dict.values())
   
    def getVertices(self):
        return self.vert_dict.keys()
   
    def addUser(self, usr):

        if usr in self.vert_dict:
            return
        else:
            self.vert_dict[usr] = []

    def addFriend(self, usr1, usr2):
        
        #check if users already exist, if not, add
        self.addUser(usr1)
        self.addUser(usr2)
        
        # add connection
        self.vert_dict[usr1].append(usr2)
        self.vert_dict[usr2].append(usr1)

    
    def removeFriend(self, usr1, usr2):
        
        # check if users already exist, if not, add
        self.addUser(usr1)
        self.addUser(usr2)

        # remove connection
        self.vert_dict[usr1].remove(usr2)
        self.vert_dict[usr2].remove(usr1)


    def processLogItem(self, item):

        event = item.event

        if event == EV_TYPE.FRIEND:
            self.addFriend(item.usr1, item.usr2)
            return 1
        
        if event == EV_TYPE.UNFRIEND:
            self.removeFriend(item.usr1, item.usr2)
            return 1

        if event == EV_TYPE.PURCHASE:
            self.addUser(item.usr1)
            return 1

        if event == EV_TYPE.NONE:
            print "Error: Event type unknown. Did nothing with this event..."
            return 0

    def DFS(self, usr, degree):
        
        """ DFS to get circle of friends out to degree of connectedness"""
  

        stack = []
        network = [[]]*(degree+1)
        visited ={}
        level = 0

        # helper function
        def addToTempList(neighbList, level, visited, network):
            
            if len(neighbList) == 0:
                return 
            for i in neighbList:
                if i not in visited:
                    network[level].append(i)
                    visited[i] = 1
                else:
                    visited[i] = visited[i] + 1
            

        stack = [usr]
        visited[usr] = 1
        network[level] = usr


        while level < degree:
            level = level + 1
            
            while stack:
        
                node = stack.pop()

                neighbors = self.vert_dict[node]
                addToTempList(neighbors, level, visited, network)
            
            stack= stack + network[level]

        
        del visited[usr]
        
        return visited.keys()

