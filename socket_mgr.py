'''
Created on 13 Jul 2017

@author: nick
'''

import   socket, SocketServer 
import logger as log 
 
class MyTCPServer(SocketServer.TCPServer):
    
    def __init__(self, server_address, RequestHandlerClass, manager):
        
        SocketServer.TCPServer.__init__(self, server_address,RequestHandlerClass)
        self.manager=manager 
    
    def readmsg(self):
        
        resp=""
        while 1:
            data=self.request.recv(1024).strip()
            if not data:
                break
            resp+=data
            
        return resp 

class SocketMgr(object):
    '''
    manage external connections
    for worker sink mode, run a SocketServer 
    '''

    def __init__(self,worker_config):
    
        self.config=worker_config 
        self.socket=None
        self.type=self.config.conn_dir    #source|sink 
        if self.type=="source":
            self.ipaddr=(self.config.get_config_item("main","remoteserver",None))
            self.port=int(self.config.get_config_item("main","remoteport",None))
        elif self.type=="sink":
            self.port=int(self.config.get_config_item("transport","port",None))
 
    
    def listen(self, manager, handler_class ):

        # manager is a reference to the calling Manager object
        log.log("Starting server on %s : %s " % ("localhost", self.port))
        self.server = MyTCPServer(("localhost", self.port), handler_class, manager)
        log.log("Listening on %s : %s " % ("localhost", self.port))
        self.server.serve_forever()
        
    def connect(self):
        
        log.log("Connecting to remote host %s : %s " % ((self.ipaddr, self.port)))
        try:
            self.socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            self.socket.connect((self.ipaddr,self.port))
        except Exception,e : 
            raise IOError(str(e))
            
    def disconnect(self):
        
        self.socket.close()
    
    def sendto_server(self, request):
        
        self.connect()
        self.socket.sendall(request)

    def readfrom_server(self):       
        
        resp=""
        while 1:
            data=self.socket.recv(1024)
            if not data:
                break
            resp+=data
        
        self.disconnect()
        return resp
    
 
 
    
    
