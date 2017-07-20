'''
Created on 13 Jul 2017

@author: nick
'''

import sys,time 
 
 
time.sleep(1)
log=open("test_worker_sink.log","a")
#log=sys.stderr
print >> log, "worker started"

while [ 1 == 1 ]:
    
    inp=sys.stdin.readline()
    #print >>log, "stdio sink worker : read request" , inp
    sys.stdout.write( "TST|rHDR|rheadat|3|rMID|2|rFTR|rRa1|rrattr1|rRa2|rrattr2|rRa3|rrattr3|rRb1a|rRb1b|rRb2a|rRb2b\n" )
    sys.stdout.flush()
    #print >>log, "stdio sink worker : sent response TST|resp|resp2|resp3" 

    