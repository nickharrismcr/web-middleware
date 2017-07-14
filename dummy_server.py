'''
Created on 14 Jul 2017

@author: nick
'''

import SocketServer, re, sys
from multiprocessing import freeze_support


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
            print >>sys.stderr, "dummy server recv : "+self.data 
            if "</body>" in self.data.split("\n") :
                    self.request.sendall(smallmsg)
                    ok=False 
                    print >>sys.stderr, "dummy server send : "+smallmsg 
                    break 


def run_dummy_server():
    
    print >>sys.stderr, "Started dummy remote server "

    HOST, PORT = "localhost", 2468

    # Create the server, binding to localhost on port 9999
    server = SocketServer.TCPServer((HOST, PORT), MyTCPHandler)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
    
if __name__== "__main__":
    freeze_support()
    