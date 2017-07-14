'''
Created on 7 Jul 2017

@author: nick

TODO : 

 
communicate with a worker 
transports

'''

import signal,multiprocessing

import config 
import logger as log
import dummy_server
from manager import Manager  
from multiprocessing import freeze_support


def handler(signum, frame):
    
    global mgr
    log.log("SIGTERM signal reoeived. stopping worker")
    mgr.stop()
    exit()
   
def main():
    signal.signal(signal.SIGTERM, handler)
    
    myconfig=config.Config("test.cfg")
    log.init(myconfig)
    
    th=multiprocessing.Process(target=dummy_server.run_dummy_server)
    th.start()
    
    mgr=Manager(myconfig)
    mgr.start_worker()
    mgr.poll()
    mgr.stop()
    th.terminate() 

if __name__=="__main__":
    freeze_support()
    main()
 
 
    
    
    
    
