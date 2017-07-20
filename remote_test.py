'''
Created on 20 Jul 2017

@author: nick
'''

import multiprocessing
from multiprocessing import freeze_support
import remote_test_tcp, remote_test_http 


th=None 

def start(myconfig):
    
    if myconfig.conn_dir=="source":
        if myconfig.get("encapsulation","type",None)=="http":
            proc=remote_test_http.run_dummy_server
        else:
            proc=remote_test_tcp.run_dummy_server
    else:
        if myconfig.get("encapsulation","type",None)=="http":
            proc=remote_test_http.run_dummy_client
        else:
            proc=remote_test_tcp.run_dummy_client 
        
    th=multiprocessing.Process(target=proc) 
    th.start()
    

def stop():
    th.terminate()
    


if __name__=="__main__":
    freeze_support() 