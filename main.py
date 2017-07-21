'''
Created on 7 Jul 2017

TODO : config logging section 
TODO : command line options for debug etc 

@author: NJH

Main instantiates a config object that reads the supplied configuration file and builds a collection of subobjects holding 
configuration information for each config file section/subsection/elements. it then instantiates an Application and sets it 
polling the source.  

Each defined  message type has its own XMLMessageConfig object, similarly for repeat group config sections. These objects 
contain lists of element config objects, one for each line in the message request and reply definitions, that know how to 
access and update an intermediate DOM and the SSV list to pass the data through. 

Application creates a configuration-dependent source and sink connector, each has converter objects that use the relevant
element config objects to convert between SSV and XML via the DOM. 

Depending on source/sink configuration the worker connector or the socket connector will act as a listener with 
a handle method called per request to  translate the request, send it to the sink, translate the response and 
return it to the source. 

logging is done via the logger module. 

Example object composition : 

Application
     -Logger
     -Config
         -WorkerConfig 
         -XMLMessageConfig
             -ConfigElement, ConfigAttribute etc. ...
         -XMLMessageConfig 
         ...
         -XMLRepeatConfig 
             --ConfigElement, ConfigAttribute etc. ... 
         ... 
      -WorkerStdio
          -XMLToSSV, SSVToXXL
      -HTTPSocket
          -HTTPServer 
          -XMLToSSV, SSVToXML 
'''

import signal,logging, sys
from multiprocessing import freeze_support

import log,config 
from application import Application  
import test.remote_test 

TEST=True

def handler(signum, frame):
    
    global app
    logging.getLogger("log").critical("SIGTERM signal reoeived. Shutting down.")
    app.stop()
    exit()
   
def main():
    
    signal.signal(signal.SIGTERM, handler)   
    
    if TEST:
        log.initdebug()
    
    myconfig=config.Config(sys.argv)
    log.init(myconfig)
    
    if TEST:
        test.remote_test.start(myconfig)
    
    try:       
        app=Application(myconfig)
        app.poll()
        app.stop()
        
    except Exception,e:
        
        logging.getLogger("log").critical(str(e))
        
        if TEST:
            raise 
         
    if TEST:
        test.remote_test.stop()


if __name__=="__main__":
    freeze_support()
    main()
 
 
    
    
    
    
