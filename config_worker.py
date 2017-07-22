'''
Created on 14 Jul 2017

@author: nick
'''

import config_base
from collections import OrderedDict
from config_base import ParsingError

True=0
False=1 

class WorkerConfig(object):
    
    """ 
    holds config data for the worker section
    """
    
    def __init__(self, config, name, params, configdata):
        
        okparams =  [ [ "stdio", "socket" ], [ "source", "sink" ] ] 
        self.subsection_classes = {
            "main"          : WorkerMainConfig, 
            "transport"     : WorkerTransportConfig,
            "message"       : WorkerMessageConfig,
            "encapsulation" : WorkerEncapsulationConfig
                                  }
        # get and store the worker section config data 
        self.config=config
        self.items={}
        config_sections=config_base.get_sections(configdata)
        
        for section,data in config_sections.iteritems():
            self.items[section]=self.subsection_classes[section](data)
        
        config_base.myassert(len(params)==len(okparams),"Invalid worker parameters")
        config_base.myassert(params[0] in okparams[0], "Invalid worker parameter "+params[0])    
        self.conn_type=params[0]
        config_base.myassert(params[1] in okparams[1], "Invalid worker parameter "+params[1])
        self.conn_dir=params[1]
        
    #---------------------------------------------------------------------------------------------------------------------                    
    def get(self, section, item, default):
        
       
        if section in self.items:
            if item in self.items[section].config:
                return self.items[section][item]
        
            elif default==None:
                raise ParsingError("Config worker section : subsection %s : item %s not found " % (section, item))

        elif default==None:
            raise ParsingError("Config %s section : subsection %s not found " % section)   
   
        return default 
                   
    #---------------------------------------------------------------------------------------------------------------------
    def check(self):
        # ensure all messages listed in the worker section have definitions in the message config sections 
        for k in self.items["message"].messages:
             
            if not self.config.check_message_defined(k):
                raise ParsingError("Message type %s is not defined " % k)
            
            

#---------------------------------------------------------------------------------------------------------------------                    
class WorkerMainConfig(object):
     
    def __init__(self,data):
        
        self.config=OrderedDict()
        _,block=data 
        
        fields={
               "command"        :    ( config_base.read_string,    True ),
               "remoteserver"   :    ( config_base.read_string,    True ),
               "remoteport"     :    ( config_base.read_string,    True ),
               "fromdelimiter"  :    ( config_base.read_delimiter, True ),
               "todelimiter"    :    ( config_base.read_delimiter, True ),
               "fromterminator" :    ( config_base.read_delimiter, True ),
               "toterminator"   :    ( config_base.read_delimiter, True )
               }
        
        for n,l in block:
            try:
                what=l.split("=")[0]
                which=l.split("=")[1]
                self.config[what]=config_base.read_config(fields,what,which) 
            except Exception,e:
                raise ParsingError("Config line %s : invalid item : %s " % (n,str(e) ))
        
        config_base.check_config("Worker", fields, self.config)

    def __getitem__(self,i):
        return self.config[i]
            
#---------------------------------------------------------------------------------------------------------------------                    
class WorkerTransportConfig(object):
     
    def __init__(self,data):
        
        okparams =  [ [ "raw", "tls" ] ] 
        fields = {
                    "port" :  (config_base.read_string, True)
                  }
        
        self.config=OrderedDict()
        params,block=data 
        
        config_base.myassert(len(params)==len(okparams),"Invalid transport definition")
        config_base.myassert(params[0] in okparams[0], "Invalid worker parameter "+params[0])    
        self.config["type"]=params[0]
        
        for n,l in block:
            try:
                what=l.split("=")[0]
                which=l.split("=")[1]
                self.config[what]=config_base.read_config(fields,what,which) 
            except Exception,e:
                raise ParsingError("Config line %s : invalid item : %s " % (n,str(e) ))

        config_base.check_config("Worker transport", fields, self.config)

    def __getitem__(self,i):
        return self.config[i]

#---------------------------------------------------------------------------------------------------------------------                    
class WorkerMessageConfig(object):
     
    def __init__(self,data):
           
        okparams=[ [ "translatedXML" ] ]
        fields={
               "messageID"      :   (config_base.read_message_id, True),
               "replymessageID" :   (config_base.read_message_id, True)
               } 
        
        self.config=OrderedDict()
        self.messages=[]
        params,block=data
        
        config_base.myassert(len(params)==len(okparams),"Invalid message definition")
        config_base.myassert(params[0] in okparams[0], "Invalid message parameter "+params[0])     
        self.type=params[0]
     
        
        for n,l in block:
            try:
                what=l.split("=")[0]
                which=l.split("=")[1]
                if what=="message":
                    self.messages.append(which)
                else:
                    self.config[what]=config_base.read_config(fields,what,which) 
            except Exception,e:
                raise ParsingError("Config line %s : invalid item : %s " % (n,str(e) ))
            
        config_base.check_config("Worker message", fields, self.config)
        
    def __getitem__(self,i):
        return self.config[i]

#--------------------------------------------------------------------------------------------------------------
class WorkerEncapsulationConfig(object):
     
    def __init__(self,data):
        
        self.config=OrderedDict()
        params,block=data 
        
        okparams=[ [ "terminated", "http" ] ]
        fields={
                "contentType"   : (config_base.read_string, False),
                "requestMethod" : (config_base.read_string, False),
                "requestURI"    : (config_base.read_string, False)
                }
        config_base.myassert(len(params)==len(okparams),"Invalid encapsulation definition")
        config_base.myassert(params[0] in okparams[0], "Invalid encapsulation parameter "+params[0])   
        self.config["type"]=params[0]
        
        fields={}
        
        for n,l in block:
            try:
                what=l.split("=")[0]
                which=l.split("=")[1]
                self.config[what]=config_base.read_config(fields,what,which) 
            except Exception,e:
                raise ParsingError("Config line %s : invalid item : %s " % (n,str(e) ))
        
        config_base.check_config("Worker encapsulation", fields, self.config)
        
            
    def __getitem__(self,i):
        return self.config[i]
                      
