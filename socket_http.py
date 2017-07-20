'''
Created on 13 Jul 2017

@author: nick
'''

import  httplib, BaseHTTPServer , logging


DIR_REQ=0
DIR_RESP=1


#-------------------------------------------------------------------------------------------------------------------------
class MyHTTPHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    def do_PUT(self):

        #print >> sys.stderr, "handler log : "+str(self.server.log)
        self.server.log.info("Connection from %s %s " % self.client_address)
        content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
        post_data = self.rfile.read(content_length) # <--- Gets the data itself
        self.server.datalog.info("Received : \n%s\n%s\n%s\n" % ("-"*80, self.headers,post_data) )
        self.send_response(200)
        self.send_header("Content-type", "text/xml")
        self.end_headers()
        translated_req=self.server.app.request_converter.convert(post_data)
        self.server.datalog.info("Translated message : \n%s \n" % translated_req)    
        self.server.app.sink.send(translated_req+"\n")
        translated_resp=self.server.app.sink.read(translator=self.server.app.response_converter) 
        self.wfile.write(translated_resp)      
        self.wfile.close()  
    
    def log_message(self, a,b,c,d):
        pass  

#-------------------------------------------------------------------------------------------------------------------------
class HTTPSocket(object):
    '''
    manage http remote host connections
    for worker sink mode, run an HTTPServer
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

        # start HTTPServer for remote connections. application is a reference to the calling Manager object
        
        self.log.info("Starting HTTP server on %s : %s " % ("localhost", self.port))
        self.server = BaseHTTPServer.HTTPServer(("127.0.0.1", self.port), MyHTTPHandler , bind_and_activate=False    )
        self.server.allow_reuse_address=True
        self.server.server_bind()
        self.server.server_activate()
        self.server.app=self.app
        self.server.log=logging.getLogger("log")
        self.server.datalog=logging.getLogger("datalog")
        self.server.serve_forever()
        
    def connect(self):
        
        self.log.info("Connecting to remote host %s : %s " % ((self.ipaddr, self.port)))
        try:
            self.conn=httplib.HTTPConnection(self.ipaddr, self.port)
        except Exception,e : 
            raise IOError(str(e))
            
    def disconnect(self):
        
        self.conn.close()
    
    def send(self, request):
        
        self.connect()
        self.conn.request("PUT", "/", request )

    def read(self, translator=None):       
           
        resp=""
        try:
            resp=self.conn.getresponse()

        except IOError,e:
            
            self.disconnect()
            self.datalog.error("No response from remote host")
            self.log.error("Error connecting to remote host : "+str(e))
            raise 
 
        self.disconnect()
        body=resp.read()
        self.datalog.info("Received response : \n%s \n" % body) 
        translated_resp=translator.convert(body)
        self.datalog.info("Translated response : \n%s \n" % translated_resp)    

        return translated_resp
    
 
 
    
    
