'''
Created on 7 Jul 2017

@author: nick

TODO : 

 
communicate with a worker 
transports

'''

import signal,multiprocessing,logging 
from multiprocessing import freeze_support


import config 
import log_setup
import remote_dummy
from manager import Manager  


def handler(signum, frame):
    
    global mgr
    logging.getLogger("log").critical("SIGTERM signal reoeived. stopping worker")
    mgr.stop()
    exit()
   
def main():
    signal.signal(signal.SIGTERM, handler)
    
    myconfig=config.Config("test.cfg")
    log_setup.init(myconfig)
    
    if myconfig.get_worker_config().conn_dir=="source":
        th=multiprocessing.Process(target=remote_dummy.run_dummy_server)
    else:
        th=multiprocessing.Process(target=remote_dummy.run_dummy_client)
    th.start()
    
    mgr=Manager(myconfig)
    mgr.start_worker()
    mgr.poll()
    mgr.stop()
    th.terminate() 

if __name__=="__main__":
    freeze_support()
    main()
 
 
    
    
    
    
