'''
Created on 7 Jul 2017

@author: nick
'''
 
from collections import OrderedDict
from workerconfig import WorkerConfig
import configbase,logger,xmlconfig
import re

re_section = re.compile("^\[.*\]")


class Config:

    """
    reads the config file and creates a dictionary of config objects ( worker, message, repeat ) that will
    hold the config data. checks the file for consistency. 
    """ 
    REQUEST=1
    RESPONSE=2 
    
    def __init__(self, p_file):
        
        # for each config section, instantiate and populate a relevant config object 
        
        self.config_classes={ 
                        "worker"     : WorkerConfig ,
                        "xmlmessage" : xmlconfig.XMLMessageConfig, 
                        "xmlrepeat"  : xmlconfig.XMLRepeatConfig
                      } 
        
        self.data=[ i for i in open(p_file,"r")]
        self.configs=OrderedDict()
        self.block=[]
        self.curr_section=""
        self.curr_params=[]
        

        for number, line in enumerate(self.data):
             
            if line[0]=="\n" or line[0]=="#" or line[0]==" ":
                continue
            
            if re_section.search(line)!=None:
                if self.curr_section != "":
                    
                    config_obj=self.config_classes[self.curr_section](self.curr_section,self.curr_params, self.block )
                    self.configs[self.curr_section]=config_obj
 
                self.block=[]
                s=configbase.get_section(line)  
                self.curr_section=s[0] 
                self.curr_params=s[1:]
            
            else:
                self.block.append((number+1,line[:-1]))
                
        config_obj=self.config_classes[self.curr_section](self.curr_section, self.curr_params, self.block )
        self.configs[self.curr_section]=config_obj
        
        self.configs["worker"].check()
    
    def get_worker_config(self):
        return self.configs["worker"]
    
    def get_worker_config_item(self,section, what,default):
        # proxy for retrieving a worker config item 
        return self.configs["worker"].get_config_item(section, what,default)
    
    def get_logfilename(self):
        return self.configs["worker"].get_config_item("main","log", "webmw.log")

    def get_datalogfilename(self):
        return self.configs["worker"].get_config_item("main", "datalog", "webmw.datalog")
    
    def __str__(self):
        
        out=str(self.configs["worker"])
        out+="\n"+xmlconfig.XMLMessageConfig.list_messages()
        return out
    
#---------------------------------------------------------------------------------------------------------------------                    