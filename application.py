'''
Created on 13 Jul 2017

@author: nick
'''

import logging 

from worker_socket import WorkerSocket
from worker_stdio import WorkerStdio
from socket_tcp import TCPSocket
from socket_http import HTTPSocket 
#from socket_http import HTTPSocket
from converters import ConverterFactory 
       

class Application(object):
    '''
    start the worker. set up a processing chain :
        create appropriate connector objects for the source and sink 
        instruct the source connector to poll the source, the connectors request handler will perform the translations 
         and comms to/from the sink and return the response to the source 
    '''
    def __init__(self, config):
        
        worker_connectors = {
                     "stdio"  : WorkerStdio,
                     "socket" : WorkerSocket 
                            }
        
        remote_connectors = {
                     "raw"  : TCPSocket, 
                     "http" : HTTPSocket       # TODO : implement http socket connector class 
                            }
 
        
        self.worker_config=config.worker 
        self.command=self.worker_config.get("main","command","")
        self.running=False 
        self.log=logging.getLogger("log")
        self.datalog=logging.getLogger("datalog")
        self.config=config 
        
        # get converter objects, used by the source request handler 
        self.request_converter =ConverterFactory.create(config,config.conn_dir,config.REQUEST)
        self.response_converter=ConverterFactory.create(config,config.conn_dir,config.RESPONSE)
        
        if self.config.get("encapsulation","type",None)=="http":
            transport="http"
        else:
            transport=self.config.get("transport","type",None)
        
        # get connector objects 
        self.worker_connector = worker_connectors[self.worker_config.conn_type](self.worker_config,self) 
        self.remote_connector = remote_connectors[transport](config,self)
        
        if config.conn_dir=="source":
            self.source=self.worker_connector
            self.sink=self.remote_connector
        elif config.conn_dir=="sink":
            self.source=self.remote_connector
            self.sink=self.worker_connector
         
    def poll(self):
        
        # start the worker. poll the source using the source connectors handler func 
        if self.worker_connector.start_worker(self.command):
            self.running=True 
        else:
            raise StandardError("Could not start_worker worker : %s " % self.command )
        
        self.source.listen()


    def stop(self):
        
        if self.running:
            self.running=False
            self.worker_connector.stop()
 
            
        
    
         
            