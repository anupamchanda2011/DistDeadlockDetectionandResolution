import threading 
import sys
import time
from multiprocessing import Process
import datetime
from subprocess import call
import deadlock_detection as deadlock

call("rm data*;rm trans*",shell=True)
#time = 0
def main():
    inputfilename = sys.argv[1]
    f = open(inputfilename,"a+")
    lines = f.readlines()
    if len(lines) == 0:
        print("file is empty or not exists")
    else:
        arr = lines[0].split()       
        transactions = int(arr[0])
        datamgrs = int(arr[1])
        proc = []
        for i in range(transactions):
            filename = "transaction" + str(i) + ".txt"
            p = Process(target=deadlock.transaction,args=(filename,i))
            p.start()
            proc.append(p)
        for i in range(datamgrs):
            filename = "datamgr" + str(i) + ".txt"
            p = Process(target=deadlock.datamgr, args=(filename,))
            p.start()
            proc.append(p)
        # for p in proc:
        #     p.join()    


        for i in range(1,len(lines)): 
            arr = lines[i].split()
            tid = int(arr[0])
            rid = int(arr[1])    
            dmgrFileName = "datamgr" + str(rid) + ".txt"
            f = open(dmgrFileName,"a+")
            f.write("request ");
            f.write("%d " %int(tid))
            f.write("%d\n" %int(rid))
            print('process ' + str(tid) + ' request for resource ' + str(rid))
            f.close()
            time.sleep(1)   

if __name__ == "__main__":
    main()

