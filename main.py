'''
Created on 7 Jul 2017

@author: nick

TODO : 

transports/encapsulations 

'''

import signal,logging 
from multiprocessing import freeze_support

import log
import config 
from application import Application  
import remote_test 

TEST=True

def handler(signum, frame):
    
    global app
    logging.getLogger("log").critical("SIGTERM signal reoeived. stopping worker")
    app.stop()
    exit()
   
def main():
    
    signal.signal(signal.SIGTERM, handler)
       
    myconfig=config.Config("test.cfg")
    log.init(myconfig)
    
    if TEST:
        remote_test.start(myconfig)
        
    app=Application(myconfig)
    app.poll()
    app.stop()
    
    if TEST:
        remote_test.stop()


if __name__=="__main__":
    freeze_support()
    main()
 
 
    
    
    
    
