'''
Created on 14 Jul 2017

@author: nick
'''

import SocketServer, sys, socket, time, struct 
from multiprocessing import freeze_support

log=None

class MyTCPServer(SocketServer.TCPServer):
    
    def __init__(self, server_address, RequestHandlerClass):
        
        SocketServer.TCPServer.__init__(self, server_address,RequestHandlerClass, bind_and_activate=False)
 

class MyTCPHandler(SocketServer.BaseRequestHandler):
 
    def handle(self):
        # self.request is the TCP socket connected to the client

        smallmsg='''<body>
    <header>
        <message_id>TST</message_id>
        <response>resp</response>
        <item>resp2</item>
        <item2>resp3</item2>
    </header>
</body>'''

        ok=True
        while ( ok ):
            self.data = self.request.recv(1024).strip()
            print >>log, "dummy server recv : "+self.data 
            if "</body>" in self.data.split("\n") :
                    self.request.sendall(smallmsg)
                    ok=False 
                    print >>log, "dummy server send : "+smallmsg 
                    break 


def run_dummy_server():
    
    global log 
    
    #log=open("remote_server.log","a")
    log=sys.stderr 
    print >>sys.stderr, "Started dummy remote server "
    HOST, PORT = "localhost", 2468
    server = MyTCPServer((HOST, PORT), MyTCPHandler)
    server.allow_reuse_address=True
    server.server_bind()
    server.server_activate()
    server.serve_forever()
    
def run_dummy_client():
    
    def doit(log):
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
        time.sleep(1.5)
        HOST, PORT = "localhost", 2468 
        print >> log, "Remote client connecting to remote host %s : %s " % ((HOST,PORT))
        try:
            sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.connect((HOST,PORT))
        
        except Exception,e : 
            print >> log, "Remote client : "+str(e)
            return 
        
        print >> log, "Remote client sending msg "
        sock.sendall(msg)
        sock.shutdown(socket.SHUT_WR)
        
        resp=""
        while 1:
            data=sock.recv(1024)
            if not data:
                break
            resp+=data 
 
        print >>log,"remote client read response : "+resp
        sock.shutdown(socket.SHUT_RD)
        sock.close()
       

            
    time.sleep(2)
    log=sys.stderr  #open("remote_client.log","a")
    print >>log, "Started dummy remote client "
    for _ in range(1,4):
        doit(log)
    print >>log, "Ended dummy remote client "
        

if __name__== "__main__":
    freeze_support()
    