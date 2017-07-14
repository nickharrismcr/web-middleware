'''
Created on 13 Jul 2017

@author: nick
'''

import sys,time 
 
 
print >> sys.stderr, "worker started"
time.sleep(1)

while [ 1 == 1 ]:
    req="TST|HDR|headat|3|MID|2|FTR|Ra1|rattr1|Ra2|rattr2|Ra3|rattr3|Rb1a|Rb1b|Rb2a|Rb2b\n"
    print >>sys.stderr, "writing request "+req 
    sys.stdout.write(req)
    inp=sys.stdin.readline()
    print >>sys.stderr, "received response ", inp 
    time.sleep(5)
    