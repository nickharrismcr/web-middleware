'''
Created on 13 Jul 2017

@author: nick
'''
import socket_mgr 
import logger as log 
from worker_socket import WorkerSocket
from worker_stdio import WorkerStdio
from convtossv import ConverterToSSV
from convtoxml import ConverterToXML
import SocketServer

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
        
        if self.worker_config.conn_dir=="source":
            self.request_converter=ConverterToXML(config, config.REQUEST)
            self.response_converter=ConverterToSSV(config,config.RESPONSE)
        else:
            self.request_converter=ConverterToSSV(config, config.REQUEST)
            self.response_converter=ConverterToXML(config,config.RESPONSE)
            
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
        else:
            raise StandardError("Invalid worker configuration : "+self.worker_config.conn_dir)
            
    def poll_worker(self):
        
        log.log("Polling worker")
        while ( self.running == True ):
            req=self.worker_connector.read()  
            log.logdata("Received worker request :\n"+req)
            translated_req=self.request_converter.convert_request(req)
            log.logdata("Sent translated data :\n"+translated_req)
            try:
                self.socket_mgr.sendto_server(translated_req)
                resp=self.socket_mgr.readfrom_server()
                log.logdata("Received response : \n"+resp)
                if len(resp)>1:
                    translated_resp=self.response_converter.convert_request(resp)
                    log.logdata("Sent translated response to worker \n"+translated_resp)
                    self.worker_connector.send(translated_resp+"\n")
                else:
                    log.logdata("No response from remote server")
            except IOError,e:
                log.logdata("No response from remote server")
                log.log("Error connecting to remote host : "+str(e))
                self.worker_connector.send(self.response_converter.error())
            finally:
                self.stop()
    
        
    def poll_socket(self):
        
        class MyTCPHandler(SocketServer.BaseRequestHandler):
 
            def handler(server):
                req=server.readmsg()
                log.log("Received request")
                log.logdata("Received request from socket :\n"+req)
                translated_req=server.manager.request_converter.convert_request(req)
                log.logdata("Translated request : \n"+translated_req)
                server.manager.worker_connector.send(translated_req+"\n")
                resp=server.manager.worker_connector.read()
                log.logdata("Worker responded \n"+resp)
                translated_resp=server.manager.response_converter.convert_request(resp)
                log.logdata("Sent translated response\n"+translated_resp)
                server.request.sendall(translated_resp)

        self.socket_mgr.listen(self,MyTCPHandler)
    
   
            
    def stop(self):
        
        if self.running:
            self.running=False
            self.worker_connector.stop()
 
            
        
    
         
            