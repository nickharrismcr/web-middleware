'''
Created on 13 Jul 2017

@author: nick
'''

import sys,time 
 
 

time.sleep(1)

#log=open("test_worker_source.log","a")
log=sys.stderr
print >> log, "worker started"
while [ 1 == 1 ]:
    time.sleep(1)
    req="TST|HDR|headat|3|MID|2|FTR|Ra1|rattr1|Ra2|rattr2|Ra3|rattr3|Rb1a|Rb1b|Rb2a|Rb2b\n"
    print >>log, "writing request "+req 
    sys.stdout.write(req)
    inp=sys.stdin.readline()
    print >>log, "received response ", inp 
    