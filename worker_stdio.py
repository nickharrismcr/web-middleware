'''
Created on 13 Jul 2017

@author: nick
'''

import subprocess,logging
 

class WorkerStdio(object):
    
    ''' communicate with a stdio worker process '''

    def __init__(self, config, app):
        '''
        Constructor
        '''
        self.app=app
        self.config=config 
        self.log=logging.getLogger("log")
        self.datalog=logging.getLogger("datalog")
    
    def start_worker(self, command ):
        
        self.log.info("Starting stdio worker : %s " % command )
        try:
            self.pipe=subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE )
        except:
            return False
        
        return True
    
    def listen(self):
        
        while True:
            # worker request handler 
            translated_req=self.read(self.app.request_converter) 
            self.app.sink.send(translated_req+"\n")
            translated_resp=self.app.sink.read(translator=self.app.response_converter) 
            self.send(translated_resp+"\n")    
     
    def read(self,translator=None):
        
        if translator:
            msg=self.pipe.stdout.readline().strip()
            self.app.log.info("Request from worker " )
            self.datalog.info("Received from worker : \n%s \n" % msg)
            translated_msg=translator.convert(msg)
            self.datalog.info("Sent translated data :\n%s \n" % translated_msg)
            return translated_msg 
        raise StandardError("No translator provided")
          
    def send(self, resp):
        
        self.pipe.stdin.write(resp)
    
    def stop(self):
        
        self.pipe.terminate()
        