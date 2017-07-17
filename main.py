'''
Created on 7 Jul 2017

@author: nick

TODO : 

transports/encapsulations 

'''

import signal,multiprocessing,logging 
from multiprocessing import freeze_support

import log
import config 
import remote_dummy
from application import Application  


def handler(signum, frame):
    
    global app
    logging.getLogger("log").critical("SIGTERM signal reoeived. stopping worker")
    app.stop()
    exit()
   
def main():
    
    
    signal.signal(signal.SIGTERM, handler)
       
    myconfig=config.Config("test.cfg")
    log.init(myconfig)
 
    if myconfig.conn_dir=="source":
        th=multiprocessing.Process(target=remote_dummy.run_dummy_server)
    else:
        th=multiprocessing.Process(target=remote_dummy.run_dummy_client)
    th.start()
    
    app=Application(myconfig)
    app.poll()
    app.stop()
    th.terminate() 

if __name__=="__main__":
    freeze_support()
    main()
 
 
    
    
    
    
