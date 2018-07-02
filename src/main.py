import os
import json
import heapq
import sys

import fileClasses as flc
import graphClasses as grphc
import analysisClasses as anlyc

def batchProcessing(graph_obj, purch_obj, log_flag):
    
    if log_flag:
        print '\nBatch processing...'
        print 'Updating Purchase Analysis Dictionary: ',purch_obj.getPurchaseComplete()
        print '\n'
    
    # update the users from graph in the Social Network and Purchase Analysis objects
    keys = graph_obj.getVertices()
    purch_obj.passUsers(keys)
    purch_obj.reducePurchaseHeap()


def streamProcessUpdate(line, parser_obj, graph_obj, purch_obj):
    
    """ Analyze the purchase for new stream purchase line"""

    item = parser_obj.processLine(line)

    DFS_results = graph_obj.DFS(item.usr1, graph_obj.degree)
    
    purchAnalysis = purch_obj.getFriendsPurchases(DFS_results) 
    
    if purchAnalysis == None:
        return
    else:
        purch_obj.isAnomolous(item,purchAnalysis)


def dataPipeline(line, parser_obj, graph_obj, purch_obj, analysis_flag, output_flag):

    """ Controls flow between batch processing and graph/analysis functions"""

    item = parser_obj.processLine(line)  

    if (True == output_flag):
        item.outputLogEvents()
    
    retVal = graph_obj.processLogItem(item)
   
    if flc.EV_TYPE.PURCHASE==item.event:
        
        purch_obj.updatePurchaseDict(item)
        
        if (True == analysis_flag):
            streamProcessUpdate(line, parser_obj, graph_obj, purch_obj)

    # likely will want to get rid of this return value
    return retVal


def main():

    # Get arguments from command line
    batch_log = sys.argv[1]
    stream_log = sys.argv[2]
    output = sys.argv[3]
    batch_freq = int(sys.argv[4])
    stream_freq = int(sys.argv[5]) # mini-batch so like every 5 lines update the graph

    if len(sys.argv) != 6:
        print 'Error!'
        print 'Usage: main.py batch_log.json stream_log.json out_log.json int_batch_freq int_stream_freq'
        return
    else:
        print '\n\n\n'
        print '--- Starting main program ---'
        print 'input batch file: ', batch_log
        print 'input stream file: ', stream_log
        print 'write results to file: ', output
        print '------------------------------'
        print '\n\n\n'

    # create parser objects to process stream and batch files separately
    batch_parser = flc.ParseEvents()
    stream_parser = flc.ParseEvents()
  

    # process the batch file at some frequency
    fp_batch = open(batch_log)

    batch_count = 0
    for line in fp_batch:
        if batch_count == 0:

            # initialize the purchase, graph instances
            D,T = batch_parser.getParams(line)

            graph = grphc.Graph(D)
            purchAnalysis = grphc.PurchaseAnalysis(T, output)

        else:
            batch_pipeRV = dataPipeline(line, batch_parser, graph, purchAnalysis,False, False)
            
            if batch_pipeRV == 0:
                print 'Error in parsing batch file!'
                break

        batch_count = batch_count + 1

        if batch_count % batch_freq == 0:
            print "----Processed batch logs at count: ", batch_count,"-----"
            batchProcessing(graph, purchAnalysis, False)
          

    print " ---- Finished with batch processing ---- "
    
    # process the stream file
    fp_stream = open(stream_log)
    #stream_freq = 100
   

    stream_count = 0
    for line in fp_stream:

        stream_pipeRV = dataPipeline(line, stream_parser, graph, purchAnalysis,True, False)
        if stream_pipeRV == 0:
            print 'Error in parsing the stream file!'
            print 'Stream count = ', stream_count
            break
        
        stream_count = stream_count +1

        if stream_count % stream_freq == 0:
            print "----Processed stream logs at count: ", stream_count,"-----"
            
            # resize the purchase heap occasionally so that it doesn't get too long for any user
            purchAnalysis.reducePurchaseHeap()       

if __name__=='__main__':
    main()


