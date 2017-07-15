'''
Created on 13 Jul 2017

@author: nick
'''

import   socket, SocketServer , logging
 
 
class MyTCPServer(SocketServer.TCPServer):
    
    def __init__(self, server_address, RequestHandlerClass, manager):
        
        SocketServer.TCPServer.__init__(self, server_address,RequestHandlerClass, bind_and_activate=False)
        self.manager=manager 
        self.log=logging.getLogger("log")
        self.datalog=logging.getLogger("datalog")
        
       

    def readmsg(self,conn):
        resp=""
        while 1:
            data=conn.recv(1024).strip()
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
        self.log=logging.getLogger("log")

    
    def listen(self, manager, handler_class ):

        # manager is a reference to the calling Manager object
        self.log.info("Starting server on %s : %s " % ("localhost", self.port))
 
        self.server = MyTCPServer(("localhost", self.port), handler_class, manager  )
        self.server.allow_reuse_address=True
        self.server.server_bind()
        self.server.server_activate()
        self.log.info("Listening on %s : %s " % ("localhost", self.port))
        self.server.serve_forever()
        
    def connect(self):
        
        self.log.info("Connecting to remote host %s : %s " % ((self.ipaddr, self.port)))
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
    
 
 
    
    
