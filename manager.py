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
    classdocs
    '''
    def __init__(self, config):
        
        self.worker_config=config.get_worker_config()
        self.command=self.worker_config.get_config_item("main","command","")
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
            req=self.worker_connector.read()  
            self.datalog.info("Received worker request :\n"+req)
            translated_req=self.request_converter.convert_request(req)
            self.datalog.info("Sent translated data :\n"+translated_req)
            try:
                self.socket_mgr.sendto_server(translated_req)
                resp=self.socket_mgr.readfrom_server()
                self.datalog.info("Received response : \n"+resp)
                if len(resp)>1:
                    translated_resp=self.response_converter.convert_request(resp)
                    self.datalog.info("Sent translated response to worker \n"+translated_resp)
                    self.worker_connector.send(translated_resp+"\n")
                else:
                    self.datalog.error("No response from remote server")
            except IOError,e:
                self.datalog.error("No response from remote server")
                self.log.error("Error connecting to remote host : "+str(e))
                self.worker_connector.send(self.response_converter.error())
        
    def poll_socket(self):
        
        class MyTCPHandler(SocketServer.BaseRequestHandler):
 
            def handle(self):

                #print >> sys.stderr, "handler log : "+str(self.server.log)
                self.server.log.info("Connection from %s %s " % self.client_address)
                req=self.server.readmsg(self.request)
                self.server.datalog.info("Received request :\n"+req)
                translated_req=self.server.manager.request_converter.convert_request(req)
                self.server.datalog.info("Translated request : \n"+translated_req)
                self.server.manager.worker_connector.send(translated_req+"\n")
                resp=self.server.manager.worker_connector.read()
                self.server.datalog.info("Worker responded \n"+resp)
                translated_resp=self.server.manager.response_converter.convert_request(resp)
                self.server.datalog.info("Sent translated response\n"+translated_resp)
                self.request.sendall(translated_resp) 
                self.request.shutdown(socket.SHUT_RDWR)
                #self.server.shutdown()
                               

        self.socket_mgr.listen(self,MyTCPHandler)

    def stop(self):
        
        if self.running:
            self.running=False
            self.worker_connector.stop()
 
            
        
    
         
            