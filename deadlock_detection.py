import threading 
import sys
import time
from multiprocessing import Process
import datetime
from subprocess import call
#time = 0

def sendMsgTransaction(msg,receiver,params):
    transFileName = "transaction" + str(receiver) + ".txt"
    f = open(transFileName,"a+")
    f.write(msg);
    for p in params:
        p = int(p)
        f.write(" %d" %p)
    f.write("\n")
    f.close()

def sendMsgDmgr(msg,receiver,params):
    transFileName = "datamgr" + str(receiver) + ".txt"
    f = open(transFileName,"a+")
    f.write(msg);
    for p in params:
        p = int(p)
        f.write(" %d" %p)
    f.write("\n")
    f.close()

def datamgr(fname):
    # initialize variables
    lineNo = 0
    holder = -1
    state = "available"
    reqQueue = []
    reqIndex = 0
    #f = open(fname,"r")
    while 1:
        f = open(fname,"a+")
        lines = f.readlines()
        if len(lines) == lineNo+1:
            arr = lines[lineNo].split()
            # handling req message
            if arr[0] == "request":
                print(arr)
                lineNo = lineNo + 1;
                # when state is available
                i = int(arr[1])
                r = int(arr[2])
                params = [i,r]
                if state == "available":
                    holder = i
                    state = "held"
                    sendMsgTransaction("grant",i,params)
                   # print("resource granted")
                # when state is held    
                elif state == "held":
                    reqQueue.append(i)
                    sendMsgTransaction("hold",i,params)
            # handling token message        
            elif arr[0] == "token":
                lineNo = lineNo + 1;
                ts = int(arr[1])
                i = int(arr[2])
                r = int(arr[3])
                params = [ts,i,r]
                if state == "available":
                    print("do nothing")
                # if the state is held  
                elif state == "held":
                    sendMsgTransaction("token",holder,params)

            # handling remove message
            elif arr[0] == "remove":
                print(arr)
                lineNo = lineNo + 1;
                i = int(arr[1])
                r = int(arr[2])
                params = [i,r]
                # when state is available
                if state == "available":
                    reqQueue.remove(i)
                # when state is held
                elif state == "held":
                    if holder == i:
                        if len(reqQueue) == 0:
                            state = "available"
                        else:
                            nextId = reqQueue[reqIndex]
                            holder = nextId
                            params = [nextId,r]
                            reqQueue.remove(nextId)
                            sendMsgTransaction("grant",holder,params)   
                    else:
                        reqQueue.remove(i)
            #handling release message
            elif arr[0] == "release":
                print(arr)
                lineNo = lineNo + 1;
                i = int(arr[1])
                r = int(arr[2])
                params = [i,r]
                # only take action when state is held
                if state == "held":
                    if len(reqQueue) == 0:
                        state = "available"
                    else:
                        nextId = reqQueue[reqIndex]
                        holder = nextId
                        params = [nextId,r]
                        reqQueue.remove(nextId)
                        sendMsgTransaction("grant",holder,params)

        f.close()
    #     print(fname)
    #     time.sleep(1)
    #   f.close()
  
def transaction(fname,tid):
    # initialize variables
    lineNo = 0
    timestamp = 0
    state = "active"
    outsResIndex = -1
    heldResources = []
    recvTokens = []
    timer = "off"
    timerExpire = 0
    i = tid
    outstandingreq = -1 
    # f = open(fname,"a+")
    while 1:
        f = open(fname,"a+")
        lines = f.readlines();
        if len(lines) == lineNo+1:
            arr = lines[lineNo].split()
            #print(arr[0])
            # when hold message is received
            if arr[0] == "hold":
                j = int(arr[1])
                r = int(arr[2])
                print('process ' + str(j) + " received discard for resource " + str(r))
                # when state is active
                if state == "active":
                    # for miliseconds
                    # timestamp = int(round(time.time())*1000);
                    outstandingreq = r
                    timestamp = int(round(time.time()));
                    timerExpire = timestamp + 6
                    timer = "on"
                    # timer started
                    recvTokens = []
                    state = "transition"
                # when state is done
                elif state == "done":
                    print("discard token")
            # when grant message is received
            if arr[0] == "grant":
                j = int(arr[1])
                r = int(arr[2])
                if state == "transition":
                    # need to add discard alarm
                    print('process ' + str(j) + " received grant for resource " + str(r))
                    timer = "off"
                    heldResources.append(r)
                    state = "active"
                elif state == "idle":
                    print('process ' + str(j) + " received grant for resource " + str(r))
                    heldResources.append(r)
                    state = "active"
                elif state == "done":
                    print("discard token")
                elif state == "active":
                    print('process ' + str(j) + " received grant for resource " + str(r))
                    #print("here")
                    #print(r)	
                    heldResources.append(r)	    

            # when token message is received
            if arr[0] == "token":
                tsj = int(arr[1])
                j = int(arr[2])
                b = int(arr[3])
                if state == "transition":
                    try:
                        if ((tsj > timestamp) or ((tsj == timestamp) and (j > i))) and (heldResources.index(b) >= 0):
                            x = (tsj,j,outstandingreq)
                            recvTokens.append(x)
                    except:
                        a = 1
                # if state is idle      
                elif state == "idle":
                    try:
                    	#print(timestamp)
                    	#print(tsj)
                    	#c = timestamp - tsj
                    	# print(timestamp)
                     #    print(tsj)
                    	# print(timestamp == tsj)
                    	# print(heldResources.index(b) >= 0)
                     #    print(i == j)
                        # print(j)
                        if (timestamp == tsj) and (heldResources.index(b) >= 0):
                            if i == j:
                                print("deadlock detected")
                                print("victim is process " + str(i))
                                list_set = set(heldResources)
                                unique_list = list(list_set)
                                for x in heldResources:
                                    params = [i,x]
                                    sendMsgDmgr("release",i,params)
                                params = [i,outstandingreq]    
                                sendMsgDmgr("remove",outstandingreq,params)
                                state = "done"
                                # deadlock detected
                            if i < j:
                            	# print("here")
                                params = [tsj,j,outstandingreq]
                                sendMsgDmgr("token",outstandingreq,params)
                            if i > j:
                                # print("discard here")
                                # discard token
                                a=1;
                        elif (timestamp < tsj) and (heldResources.index(b) >= 0):
                            #print("gotcha")	
                            params = [tsj,j,outstandingreq]
                            sendMsgDmgr("token",outstandingreq,params)
                            # time.sleep(2)
                        else:
                            # print("nooooo")	
                            # discard token
                            a=1
                    except:
                        a = 1

            # when release message is received
            if arr[0] == "release":
                if state == "active":
                    list_set = set(heldResources)
                    unique_list = (list(list_set))
                    for x in unique_list:
                        params = [i,x]
                        sendMsgDmgr("release",i,params)
                
            lineNo = lineNo + 1;

        if timer == "on" and state == "transition":
            curtime = int(round(time.time()));
            if curtime == timerExpire:
                timer = "off"
                state = "idle"
                params = [timestamp,i,outstandingreq]
                sendMsgDmgr("token",outstandingreq,params)
                #print(recvTokens)
                #list_set = set(heldResources)
                #unique_list = (list(list_set))
                #for x in unique_list:
                #	params = [i,x]
                 #       sendMsgDmgr("release",i,params)

        f.close() 

    #f.close()