'''
Created on 9 Jul 2017

@author: nick

classes for holding XNLMessage and XMLRepeat configuration sections 
each holds a dict of ConfigElement etc. objects,  one per config line 
'''

from collections import OrderedDict
import config_base
import etree_fns
from config_base import ParsingError
 


classlookup = {     "element" :           config_base.ConfigElement ,
                    "attribute" :         config_base.ConfigAttribute ,
                    "staticElement" :     config_base.ConfigStaticElement ,
                    "staticAttribute" :   config_base.ConfigStaticAttribute ,
                    "repeat" :            config_base.ConfigRepeat,
                    "messageid" :         None }

class XMLMessageConfig():
    
    """ 
    holds config data for an individual xml message defn
    """ 
    
    # class level dict of message types 
    xml_messages = OrderedDict()
    xml_workermessages = OrderedDict()
 
    def __init__(self, config, name,  params, configdata):
        
        config_sections=config_base.get_sections(configdata)
        
        self.items=OrderedDict()
        self.request_elems=[]
        self.response_elems=[]
        self.messagetype=params[0]
        self.request_value_count=0
        self.reply_value_count=0
        
        # populate request and reply data 
        
        fields={ "messageType"       : (config_base.read_string, True ),
                 "workerMessageType" : (config_base.read_string, True)
               }

        for n,l in config_sections["main"][1]:
            try:
                what=l.split("=")[0]
                which=l.split("=")[1]
                self.items[what]=config_base.read_config(fields,what,which) 
            except Exception,e:
                raise ParsingError("Config line %s : invalid item : %s " % (n,str(e) ))
        
        config_base.check_config("Message %s" % self.messagetype , fields, self.items)
        self.xml_messages[self.items["messageType"]]=self
        self.xml_workermessages[self.items["workerMessageType"]]=self
        
        if "request" in config_sections:
            for n,l in  config_sections["request"][1]:
                try:
                    which,what=l.split("=") 
                    if which=="valueCount":
                        self.request_value_count=int(what)
                    else:
                        lineclass=classlookup[which]
                        if lineclass:
                            self.request_elems.append(lineclass(config, n,what))
                except:
                    raise ParsingError("Invalid configuration : %s at line %s " % (l,n))
        else:
            raise ParsingError("xmlmessage %s missing request definition" % self.messagetype )
              
        if "reply" in config_sections:
            for n,l in  config_sections["reply"][1]:
                try:
                    which,what=l.split("=") 
                    if which=="valueCount":
                        self.reply_value_count=int(what)
                    else:
                        lineclass=classlookup[which]
                        if lineclass:
                            self.response_elems.append(lineclass(config, n,what))
                except:
                    raise ParsingError("Invalid configuration : %s at line %s " % (l,n))
        else:
            raise ParsingError("xmlmessage %s missing reply definition" % self.messagetype )            
        
        if self.request_value_count==0:
            raise ParsingError("xmlmessage %s missing request value count " % self.messagetype )
        if self.request_value_count-1 != self.request_elems[-1].ssv_col:
            raise ParsingError("xmlmessage %s invalid request value count %s " % (self.messagetype,self.request_value_count))
        if self.reply_value_count==0:
            raise ParsingError("xmlmessage %s missing reply value count " % self.messagetype )
        if self.reply_value_count-1 != self.response_elems[-1].ssv_col:
            raise ParsingError("xmlmessage %s invalid reply value count %s " % (self.messagetype, self.reply_value_count))

    def get(self,itemkey):
        return self.items[itemkey]
    
    @classmethod
    def iterate_message_list(cls):
        return cls.xml_messages.iteritems()
        
    @classmethod
    def list_messages(cls):
        out=""
        for k,m in cls.xml_messages.iteritems():  
            out+= "Message %s \n%s" % (k,m)
        return out
    
    @classmethod
    def check_message_defined(cls, messagetype):
        return messagetype in cls.xml_messages
        
    @classmethod
    def get_config(cls,messagetype):
        # get the XMLMessageConfig object for the given xml message type 
        return cls.xml_messages[messagetype]
    
    @classmethod
    def get_config_worker(cls,messagetype):
        # get the XMLMessageConfig object for the given worker message type 
        return cls.xml_workermessages[messagetype]
    
    
    def get_request_elems(self):
        return self.request_elems
    
    def get_response_elems(self):
        return self.response_elems
    
    def check_messageID_path(self,path):
        
        pathlist=etree_fns.get_path_list(path)
        for req_elem in self.request_elems:
            reqpath=etree_fns.get_path_list(req_elem.path)
            if pathlist[0]!=reqpath[0]:
                raise ParsingError("messageID path %s does not match request path at config line %s : %s " % 
                                    (path, req_elem.lineno,req_elem.path))
    
    def check_replymessageID_path(self,path):
        
        pathlist=etree_fns.get_path_list(path)
        for resp_elem in self.response_elems:
            resppath=etree_fns.get_path_list(resp_elem.path)
            if pathlist[0]!=resppath[0]:
                raise ParsingError("replymessageID path %s does not match reply path at config line %s : %s " % 
                                    (path, resp_elem.lineno, resp_elem.path))
    
#---------------------------------------------------------------------------------------------------------------------                    
    
        
class XMLRepeatConfig():
    
    """
    holds config data for an XML repeat section
    """
    # class level dict of repeat config types 
    xml_repeats = OrderedDict()
    
    def __init__(self, config, name, params, configdata):
         
        config_sections=config_base.get_sections(configdata)
        self.xml_repeats[params[0]]=self
        self.elems=[]
        self.repeattag=""
        if "main" in config_sections:
            for n,l in  config_sections["main"][1]:
                which,what=l.split("=") 
                if which=="valueCount":
                    self.value_count=int(what)
                elif which=="repeattag":
                    self.repeattag=what
                else:
                    lineclass=classlookup[which]
                    if lineclass:
                        self.elems.append(lineclass(config, n,what))
  
    
    def get_elems(self):
        return self.elems                    
                
    @classmethod
    def get_config(cls,name):
        # get the XMLRepeatConfig object for the given name, referred to in message repeat elements 
        if name in cls.xml_repeats:
            return cls.xml_repeats[name]
        raise StandardError("XMLRepeat section %s not defined " % name )
   
