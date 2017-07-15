'''
Created on 9 Jul 2017

@author: nick
'''

import logging,sys 

def init(config):
    
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    log=logging.getLogger("log")
    log.setLevel(level=logging.DEBUG)
    
    console=logging.StreamHandler(stream=sys.stdout)
    console.setFormatter(formatter)
    lfile=logging.FileHandler(filename=config.get_logfilename())
    lfile.setFormatter(formatter)
    
    log.addHandler(console)
    log.addHandler(lfile)
    
    datalog=logging.getLogger("datalog")
    datalog.setLevel(level=logging.INFO)
    
    dconsole=logging.StreamHandler(stream=sys.stdout)
    dconsole.setFormatter(formatter)
    dfile=logging.FileHandler(filename=config.get_datalogfilename())
    dfile.setFormatter(formatter)
    
    datalog.addHandler(dconsole)
    datalog.addHandler(dfile)
    
 
    
    
 
 


    