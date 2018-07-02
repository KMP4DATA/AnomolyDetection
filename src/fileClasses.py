import heapq
import math
import sys
import time

from enum import Enum

class EV_TYPE(Enum):

    PURCHASE = 1
    FRIEND = 2
    UNFRIEND = 3
    NONE = 4

class LogObject(object):

    def __init__(self, event, timestamp, usr1, usr2, value, line):
        self.event = event
        self.stamp = timestamp
        self.usr1 = usr1
        self.usr2 = usr2
        self.value = value
        self.line = line

    def outputLogEvents(self):
        print "--Log Event --"
        print self.line
        print "event_type:", self.event
        print "timestamp:", self.stamp
        print "usr1:", self.usr1
        print "usr2:", self.usr2
        print "value:", self.value
        print "-------------"


""" Class to parse .json batch and stream log files """

class ParseEvents(object):

    def convertTimestamp(self, st):
        try:
            ts = time.mktime(time.strptime(st, '%Y-%m-%d %H:%M:%S'))
        except ValueError:
            ts = time.mktime(clock())
        #return int(time.mktime(time.strptime(st, '%Y-%m-%d %H:%M:%S')))
        return int(ts)

    def processTimestamp(self, timestamp):
        
        timestamp = timestamp.strip()
        timestamp = timestamp.strip("\"timestamp\":")
        timestamp = timestamp.strip()
        timestamp = timestamp.strip('\"')
        
        int_ts = self.convertTimestamp(timestamp)
        
        return int_ts

    def processEventType(self, eventString):

        strTmp, eventType  = eventString.split(':')

        if "\"purchase\"" == eventType:
            event = EV_TYPE.PURCHASE
        elif "\"befriend\"" == eventType:
            event = EV_TYPE.FRIEND
        elif "\"unfriend\"" == eventType:
            event = EV_TYPE.UNFRIEND
        else:
            event = EV_TYPE.NONE
            print 'ERROR: Parser: Event type is not known!\n'

        return event

    def processNumString(self, st):
        s1, s2 = st.split(':')
        s2 = s2.strip()
        num = s2.strip("\"")

        return num

    def processPurchase(self, str2):
        
        s1, s2 = st.split(':')
        s2 = s2.strip()
        usr = s2.strip("\"")

        return usr

    def processLine(self, line):

        """ Function to process lines in the json batch or stream file"""

        line = line.strip()
        line = line.strip('{}')
        
        # split line and get arguments
        try:
            eventString, tsString, str1, str2 = line.split(',')
        except ValueError:
            print 'Error: Parser: Log line has unexpected format!'
            print 'Encountered error on line:\n', line 
            event = EV_TYPE.NONE
            logItem = LogObject(event, "" , "" , "", "","") 
            return logItem

        # get event type
        event = self.processEventType(eventString)

        # get timestamp
        ts = self.processTimestamp(tsString)

        # process either adding or deleting friends by assigning to usr1,usr2
        # set value to -1.0
        if event == EV_TYPE.FRIEND or event == EV_TYPE.UNFRIEND:
           usr1 = self.processNumString(str1) 
           usr2 = self.processNumString(str2) 
           value = -1.0


        # process purchase and keep track of usr1 and value, set usr2 to empty string
        if event == EV_TYPE.PURCHASE:
            usr1 = self.processNumString(str1)
            value = self.processNumString(str2)
            value = float(value)
            usr2 = ""
            

        # create LogObject item
        logItem = LogObject(event, ts, usr1, usr2, value,line) 
        
        return logItem

    def getParams(self, line):

        """ Get parameters from the batch file """
        
        line = line.strip()
        line = line.strip('{}')
       
        str1, str2 = line.split(',')
    
        str1, str_D = str1.split(':')
        str_D = str_D.strip(' ')
        str_D = str_D.strip('\"')
        D = int(str_D)

        str2, str_T = str2.split(':')
        str_T = str_T.strip(' ')
        str_T = str_T.strip('\"')
        T = int(str_T)

        return D,T

