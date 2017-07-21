'''
Created on 7 Jul 2017

@author: nick
'''
 
from collections import OrderedDict
from config_worker import WorkerConfig
import config_base
import config_xml
import re,logging,sys
from config_base import ParsingError

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
                        "xmlmessage" : config_xml.XMLMessageConfig, 
                        "xmlrepeat"  : config_xml.XMLRepeatConfig
                      } 
        try:
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
                        
                        config_obj=self.config_classes[self.curr_section](self, self.curr_section,self.curr_params, self.block )
                        self.configs[self.curr_section]=config_obj
     
                    self.block=[]
                    s=config_base.get_section(line)  
                    self.curr_section=s[0] 
                    self.curr_params=s[1:]
                
                else:
                    self.block.append((number+1,line[:-1]))
                    
            config_obj=self.config_classes[self.curr_section](self, self.curr_section, self.curr_params, self.block )
            self.configs[self.curr_section]=config_obj
            
            # ensure all messages listed in the worker section have definitions in the message items sections 
            self.configs["worker"].check()
            
            # ensure messageID/replymessageID are valid in all the XMLmessage defs 
            messageIDpath=self.configs["worker"].get("message","messageID",None)
            replymessageIDpath=self.configs["worker"].get("message","replymessageID",None)
            for _,message in self.configs["xmlmessage"].iterate_message_list():
                message.check_messageID_path(messageIDpath)
                message.check_replymessageID_path(replymessageIDpath)
                
        except ParsingError,e:
            print >>sys.stderr, "%s : %s " % (type(e).__name__, str(e))
            exit()
            
    @property
    def worker(self):
        return self.configs["worker"]
    
    def get(self,section, what,default):
        # proxy for retrieving a worker config item 
        return self.configs["worker"].get(section, what,default)
    
    @property
    def logfilename(self):
        return self.configs["worker"].get("main","log", "webmw.log")

    @property
    def datalogfilename(self):
        return self.configs["worker"].get("main", "datalog", "webmw.data.log")
    
    @property
    def conn_dir(self):
        return self.configs["worker"].conn_dir 
    
    def get_xmlconfig(self,message):
        return self.configs["xmlmessage"].get_config(message)
    
    def get_xmlrepeatconfig(self,message):
        return self.configs["xmlrepeat"].get_config(message)
    
    def check_message_defined(self,message):
        return self.configs["xmlmessage"].check_message_defined(message)
    
    def __str__(self):
        
        out=str(self.configs["worker"])
        out+="\n"+config_xml.XMLMessageConfig.list_messages()
        return out
    
#---------------------------------------------------------------------------------------------------------------------                    
