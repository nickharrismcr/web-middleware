'''
Created on 13 Jul 2017

@author: nick
'''

import SocketServer,socket,logging 

import socket_mgr 
from worker_socket import WorkerSocket
from worker_stdio import WorkerStdio
from xml_to_ssv import XMLToSSV
from ssv_to_xml import SSVToXML


worker_connectors = {
                     "stdio" : WorkerStdio,
                     "socket" : WorkerSocket 
                     }

class Manager(object):
    '''
    start the worker. set up a processing chain :
        worker = source :
            poll worker for requests :
                translate request, send to remote host, translate response, send to worker
        worker = sink :
            set up TCPServer to handle requests from remote host:
                translate request, send to worker, translate response, send response to remote host 
            
    '''
    def __init__(self, config):
        
        self.worker_config=config.worker()
        self.command=self.worker_config.get("main","command","")
        self.socket_mgr=socket_mgr.SocketMgr(self.worker_config)
        self.running=False 
        self.log=logging.getLogger("log")
        self.datalog=logging.getLogger("datalog")
        
        if self.worker_config.conn_dir=="source":
            self.request_converter=SSVToXML(config, config.REQUEST)
            self.response_converter=XMLToSSV(config,config.RESPONSE)
        elif self.worker_config.conn_dir=="sink":
            self.request_converter=XMLToSSV(config, config.REQUEST)
            self.response_converter=SSVToXML(config,config.RESPONSE)
            
        self.worker_connector = worker_connectors[self.worker_config.conn_type](self.worker_config)
                                                                
    def start_worker(self):
        
        if self.worker_connector.start_worker(self.command):
            self.running=True 
        else:
            raise StandardError("Could not start_worker worker : %s " % self.command )
        
    def poll(self):
        
        if self.worker_config.conn_dir=="source":
            self.poll_worker()
        elif self.worker_config.conn_dir=="sink":
            self.poll_socket()
       
            
    def poll_worker(self):
        
        self.log.info("Polling worker")
        while ( self.running == True ):
            translated_req=self.worker_connector.read(translator=self.request_converter)  
            self.socket_mgr.sendto_server(translated_req)
            translated_resp=self.socket_mgr.readfrom_server(translator=self.response_converter)
            self.worker_connector.send(translated_resp+"\n")

        
    def poll_socket(self):
        
        class MyTCPHandler(SocketServer.BaseRequestHandler):
 
            def handle(self):

                #print >> sys.stderr, "handler log : "+str(self.server.log)
                self.server.log.info("Connection from %s %s " % self.client_address)
                translated_req=self.server.readmsg(self.request,self.server.request_converter) 
                self.server.manager.worker_connector.send(translated_req+"\n")
                translated_resp=self.server.manager.worker_connector.read(translator=self.server.response_converter) 
                self.request.sendall(translated_resp) 
                self.request.shutdown(socket.SHUT_RDWR)

                #self.server.shutdown()
         
        self.socket_mgr.listen(self,MyTCPHandler,self.request_converter,self.response_converter)

    def stop(self):
        
        if self.running:
            self.running=False
            self.worker_connector.stop()
 
            
        
    
         
            