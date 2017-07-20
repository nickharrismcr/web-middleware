'''
Created on 9 Jul 2017

@author: nick
'''

import logging,sys 

# this bypasses the @trace decorators code if False, but @trace decorators should be commented out in release code
DEBUGMODE=False 

def init(config):
    
    global DEBUGMODE 
    
    logging.getLogger().setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    log=logging.getLogger("log")
    log.setLevel(level=logging.INFO)
    console=logging.StreamHandler(stream=sys.stdout)
    console.setFormatter(formatter)
    lfile=logging.FileHandler(config.logfilename)
    lfile.setFormatter(formatter)
    log.addHandler(console)
    log.addHandler(lfile)
    
    datalog=logging.getLogger("datalog")
    datalog.setLevel(level=logging.INFO)
    dconsole=logging.StreamHandler(stream=sys.stdout)
    dconsole.setFormatter(formatter)
    dfile=logging.FileHandler(config.datalogfilename)
    dfile.setFormatter(formatter)
    datalog.addHandler(dconsole)
    datalog.addHandler(dfile)
    
    if DEBUGMODE:
        
        debug=logging.getLogger("debug")
        debug.setLevel(level=logging.DEBUG)
        debconsole=logging.StreamHandler(stream=sys.stdout)
        debconsole.setFormatter(formatter)
        debfile=logging.FileHandler(filename="webmw_python_debug.log")
        debfile.setFormatter(formatter)
        debug.addHandler(debconsole)
        debug.addHandler(debfile)

 
 


    