'''
Created on 13 Jul 2017

@author: nick
'''

import sys,time 
 
 
time.sleep(1)
log=open("test_worker_sink.log","a")
print >> log, "worker started"

while [ 1 == 1 ]:
    
    inp=sys.stdin.readline()
    print >>log, "stdio sink worker : read request" , inp
    sys.stdout.write( "TST|resp|resp2|resp3\n" )
    print >>log, "stdio sink worker : sent response TST|resp|resp2|resp3" 

    