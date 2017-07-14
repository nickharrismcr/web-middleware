'''
Created on 9 Jul 2017

@author: nick
'''

import datetime

class Logger(object):
    '''
    classdocs
    '''


    def __init__(self):
        
        self.debug=open("debug","a")
    
    def init(self,config):
        
        self.logfile=open(config.get_logfilename(),"a")
        self.datalogfile=open(config.get_datalogfilename(),"a")

        
    def __enter__(self):
        return self
        
    def logdata(self,msg):
        
        s="%s : %s \n" % ( str(datetime.datetime.now()).split(".")[0] , msg ) 
        print >>self.datalogfile,s
        print "data ",s 
        
    def log(self,msg):
        
  
        s="%s : %s" % ( str(datetime.datetime.now()).split(".")[0] , msg ) 
        print >>self.logfile,s
        print "log : ",s
        
    def logdebug(self,msg):
        
        print "debug : "+msg
        print >>self.debug, msg 
        
    def __exit__(self,exception_type, exception_value, traceback):
        self.logfile.close()
        self.datalogfile.close()
        self.debug.close()
 
def debug(s):
    
    print >>l.debug, s
    print s

l=Logger()
init=l.init
log=l.log
logdata=l.logdata
 


    