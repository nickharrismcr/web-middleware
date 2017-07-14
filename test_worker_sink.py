'''
Created on 13 Jul 2017

@author: nick
'''

import sys,time 
 
 

print >> sys.stderr, "worker started"
time.sleep(1)

while [ 1 == 1 ]:
    
    inp=sys.stdin.readline()
    time.sleep(1)
    print >>sys.stderr, "read request" , inp
    time.sleep(2)
    sys.stdout.write( "TST|resp|resp2|resp3\n" )
    print >>sys.stderr, "sent response TST|resp|resp2|resp3" 

    