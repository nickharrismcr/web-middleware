'''
Created on 13 Jul 2017

@author: nick
'''

import   socket, SocketServer , logging

DIR_REQ=0
DIR_RESP=1


#-------------------------------------------------------------------------------------------------------------------------
class MyTCPHandler(SocketServer.BaseRequestHandler):

    def handle(self):

        #print >> sys.stderr, "handler log : "+str(self.server.log)
        self.server.log.info("Connection from %s %s " % self.client_address)
        translated_req=self.server.readmsg(self.request,self.server.app.request_converter) 
        self.server.app.sink.send(translated_req+"\n")
        translated_resp=self.server.app.sink.read(translator=self.server.app.response_converter) 
        self.request.sendall(translated_resp) 
        self.request.shutdown(socket.SHUT_RDWR)
 
#-------------------------------------------------------------------------------------------------------------------------
class MyTCPServer(SocketServer.TCPServer):
    
    '''TCPServer class with some extra references to application and log objects  '''
    
    def __init__(self, server_address, RequestHandlerClass, app ):
        
        SocketServer.TCPServer.__init__(self, server_address,RequestHandlerClass, bind_and_activate=False)
        self.app=app
        self.log=logging.getLogger("log")
        self.datalog=logging.getLogger("datalog")
        
    def readmsg(self,conn,converter):
        
        ''' read and translate a message from the remote server
           called in MyTCPHandler handle method 
        ''' 
         
        resp=""
        try:
            while 1:
                data=conn.recv(1024)
                if not data:
                    break
                resp+=data
        except IOError,e:
            self.datalog.error("Could not read from remote server")
            self.log.error("Error connecting to remote host : "+str(e))
            raise 
  
        self.datalog.info("Received : \n"+resp) 
        translated_resp=converter.convert(resp)  
        self.datalog.info("Translated message : \n"+translated_resp)    
    
        return translated_resp
        

#-------------------------------------------------------------------------------------------------------------------------
class TCPSocket(object):
    '''
    manage tcp remote host connections
    for worker sink mode, run a SocketServer
    '''

    def __init__(self, config, app):
    
        self.app=app
        self.items=config.worker
        self.socket=None
        self.type=self.items.conn_dir    #source|sink 
        if self.type=="source":
            self.ipaddr=(self.items.get("main","remoteserver",None))
            self.port=int(self.items.get("main","remoteport",None))
        elif self.type=="sink":
            self.port=int(self.items.get("transport","port",None))
        self.log=logging.getLogger("log")
        self.datalog=logging.getLogger("datalog")
        self.request_converter=app.request_converter
        self.response_converter=app.response_converter 
                 
    def listen(self):

        # start TCPServer for remote connections. application is a reference to the calling Manager object
        
        self.log.info("Starting TCP server on %s : %s " % ("localhost", self.port))
 
        self.server = MyTCPServer(("localhost", self.port), MyTCPHandler , self.app    )
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
    
    def send(self, request):
        
        self.connect()
        self.socket.sendall(request)

    def read(self, translator=None):       
           
        resp=""
        try:
            while 1:
                data=self.socket.recv(1024)
                if not data:
                    break
                resp+=data
                
        except IOError,e:
            
            self.disconnect()
            self.datalog.error("No response from remote host")
            self.log.error("Error connecting to remote host : "+str(e))
            raise 
 
        self.disconnect()
        self.datalog.info("Received response : \n%s \n" % resp) 
        translated_resp=translator.convert(resp)
        self.datalog.info("Translated response : \n%s \n" % translated_resp)    

        return translated_resp
    
 
 
    
    
