'''
Created on 14 Jul 2017

@author: nick
'''

import configbase, xmlconfig
from collections import OrderedDict

class WorkerConfig(object):
    
    """ 
    holds config data for the worker section
    """
    
    def __init__(self, name, params, configdata):
        
        self.subsection_classes = {
            "main"          : WorkerMainConfig, 
            "transport"     : WorkerTransportConfig,
            "message"       : WorkerMessageConfig,
            "encapsulation" : WorkerEncapsulationConfig
                                  }
        # get and store the worker section config data 
        self.config={}
        config_sections=configbase.get_sections(configdata)
        
        for section,data in config_sections.iteritems():
            self.config[section]=self.subsection_classes[section](data)
            
        self.conn_type=params[0]
        self.conn_dir=params[1]

    #---------------------------------------------------------------------------------------------------------------------                    
    def get_config_item(self, section, item, default):
        
       
        if section in self.config:
            if item in self.config[section].items:
                return self.config[section][item]
            elif default==None:
                raise StandardError("Config worker section : subsection %s : item %s not found " % (section, item))
        elif default==None:
            raise StandardError("Config %s section : subsection %s not found " % section)   
   
        return default 
                   
    #---------------------------------------------------------------------------------------------------------------------
    def check(self):
        # ensure all messages listed in the worker section have definitions in the message config sections 
        for k in self.config["message"].messages:
            if not xmlconfig.XMLMessageConfig.check_message_defined(k):
                raise LookupError("Config line %s : message type %s is not defined " % (self.messages[k],k))
            
            

#---------------------------------------------------------------------------------------------------------------------                    
class WorkerMainConfig(object):
     
    def __init__(self,data):
        
        self.items=OrderedDict()
        params,block=data 
        readers={
               "fromdelimiter" :    configbase.read_delimiter,
               "todelimiter" :      configbase.read_delimiter,
               "fromterminator" :   configbase.read_delimiter,
               "toterminator" :     configbase.read_delimiter
               }
        
        for n,l in block:
            try:
                what=l.split("=")[0]
                which=l.split("=")[1]
                self.items[what]=configbase.read_config(readers,what,which) 
            except Exception,e:
                raise StandardError("Config line %s : parsing error : %s " % (n,str(e) ))

    def __getitem__(self,i):
        return self.items[i]
            
#---------------------------------------------------------------------------------------------------------------------                    
class WorkerTransportConfig(object):
     
    def __init__(self,data):
        
   
        self.items=OrderedDict()
        params,block=data 
        self.type=params[0]
        
        readers={}
        
        for n,l in block:
            try:
                what=l.split("=")[0]
                which=l.split("=")[1]
                self.items[what]=configbase.read_config(readers,what,which) 
            except Exception,e:
                raise StandardError("Config line %s : parsing error : %s " % (n,str(e) ))

    def __getitem__(self,i):
        return self.items[i]

#---------------------------------------------------------------------------------------------------------------------                    
class WorkerMessageConfig(object):
     
    def __init__(self,data):
        
        self.items=OrderedDict()
        self.messages=[]
        params,block=data 
        self.type=params[0]
        
        readers={
               "messageID" :        configbase.read_message_id,
               "replymessageID" :   configbase.read_message_id,
              } 
        
        for n,l in block:
            try:
                what=l.split("=")[0]
                which=l.split("=")[1]
                if what=="message":
                    self.messages.append(which)
                else:
                    self.items[what]=configbase.read_config(readers,what,which) 
            except Exception,e:
                raise StandardError("Config line %s : parsing error : %s " % (n,str(e) ))
            
    def __getitem__(self,i):
        return self.items[i]

#--------------------------------------------------------------------------------------------------------------
class WorkerEncapsulationConfig(object):
     
    def __init__(self,data):
        
        self.items=OrderedDict()
        params,block=data 
        self.type=params[0]
        
        readers={}
        
        for n,l in block:
            try:
                what=l.split("=")[0]
                which=l.split("=")[1]
                self.items[what]=configbase.read_config(readers,what,which) 
            except Exception,e:
                raise StandardError("Config line %s : parsing error : %s " % (n,str(e) ))
            
    def __getitem__(self,i):
        return self.items[i]
                       