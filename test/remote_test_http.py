'''
Created on 14 Jul 2017

@author: nick
'''

import BaseHTTPServer, sys, time, httplib, datetime
from multiprocessing import freeze_support

class MyHTTPServer(BaseHTTPServer.HTTPServer):
    
    def __init__(self, server_address, RequestHandlerClass):
        
        BaseHTTPServer.HTTPServer.__init__(self, server_address,RequestHandlerClass, bind_and_activate=False)
 

class MyHTTPHandler(BaseHTTPServer.BaseHTTPRequestHandler):
 
    def do_PUT(self):

        respmsg='''<rbody>
    <header header_attrib="headat">
      <message_id>TST</message_id>
      <header_item>HDR</header_item>
      <header_static_item>This is static content</header_static_item>
    </header>
    <repeats>
      <repeat>
         <repeat_item rep_attr="rattr1">Ra1</repeat_item>
      </repeat>
      <repeat>
         <repeat_item rep_attr="rattr2">Ra2</repeat_item>
      </repeat>
      <repeat>
         <repeat_item rep_attr="rattr3">Ra3</repeat_item>
      </repeat>
    </repeats>
    <mid>MID</mid>
    <repeats2>
      <repeat2>
         <repeat2_item1>Rb1a</repeat2_item1>
         <repeat2_item2>Rb1b</repeat2_item2>
      </repeat2>
      <repeat2>
         <repeat2_item1>Rb2a</repeat2_item1>
         <repeat2_item2>Rb2b</repeat2_item2>
      </repeat2>
    </repeats2>
    <footer>FTR</footer>
</rbody>'''
 
        content_length = int(self.headers['Content-Length']) 
        post_data = self.rfile.read(content_length) 
        self.send_response(200)
        self.send_header("Content-type", "text/xml")
        self.end_headers()
        self.wfile.write(respmsg)       
    
    def log_message(self, a,b,c,d):
        pass  

def run_dummy_server():
    
    log( "Started dummy remote server " ) 
    HOST, PORT = "localhost", 2468
    server = MyHTTPServer((HOST, PORT), MyHTTPHandler)
    server.allow_reuse_address=True
    server.server_bind()
    server.server_activate()
    server.serve_forever()

def log(msg):
    
    pass 
    #print >>sys.stderr, msg 
    #log=open("remote_server.log","a")
     
def run_dummy_client():
    
    def doit(conn):
        msg='''
<body>
    <header header_attrib="headat">
      <message_id>TST</message_id>
      <header_item>HDR</header_item>
      <header_static_item>This is static content</header_static_item>
    </header>
    <repeats>
      <repeat>
         <repeat_item rep_attr="rattr1">Ra1</repeat_item>
      </repeat>
      <repeat>
         <repeat_item rep_attr="rattr2">Ra2</repeat_item>
      </repeat>
      <repeat>
         <repeat_item rep_attr="rattr3">Ra3</repeat_item>
      </repeat>
    </repeats>
    <mid>MID</mid>
    <repeats2>
      <repeat2>
         <repeat2_item1>Rb1a</repeat2_item1>
         <repeat2_item2>Rb1b</repeat2_item2>
      </repeat2>
      <repeat2>
         <repeat2_item1>Rb2a</repeat2_item1>
         <repeat2_item2>Rb2b</repeat2_item2>
      </repeat2>
    </repeats2>
    <footer>FTR</footer>
</body>'''
     
        log(str(datetime.datetime.now()) + " Remote http client sending request") 
        try: 
            conn.request("PUT", "/", msg )
        except Exception,e : 
            log("Remote client : "+str(e))
            return 
        log(str(datetime.datetime.now()) + " Remote http client sent request" )
        
        resp=read(conn)

        #print >>log,"remote http client read response : "+resp
        

     
    def connect(ipaddr, port ):
        
        try:
            conn=httplib.HTTPConnection(ipaddr, port)
        except Exception,e : 
            raise IOError(str(e))
        return conn  
    
    def read(conn):       
           
        resp=""
        try:
            resp=conn.getresponse()
        except IOError:
            conn.close()
            raise 
        body=resp.read()
         
        return body 
        
    time.sleep(1)
    log("Started dummy remote http client ")
       
    HOST, PORT = "127.0.0.1", 2468 
    log( str(datetime.datetime.now()) + " Remote http client connecting to remote host %s : %s " % ((HOST,PORT)))
    conn=connect(HOST,PORT)

    for _ in range(1,2):
        doit(conn)

    conn.close()  

if __name__== "__main__":
    freeze_support()
    