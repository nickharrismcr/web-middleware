'''
Created on 13 Jul 2017

@author: nick
'''

import subprocess
import logger as log 

class WorkerStdio(object):
    '''
    classdocs
    '''


    def __init__(self, config):
        '''
        Constructor
        '''
        pass
    
    def start_worker(self, command ):
        
        log.log("Starting stdio worker : %s " % command )
        try:
            self.pipe=subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE )
        except:
            return False
        
        return True
        
    def read(self):
        
        return self.pipe.stdout.readline().strip()
        
    def send(self, resp):
        
        self.pipe.stdin.write(resp)
    
    def stop(self):
        
        self.pipe.terminate()
        