'''
Created on 9 Jul 2017

@author: nick

classes for holding XNLMessage and XMLRepeat configuration sections 
each holds a dict of ConfigElement etc. objects,  one per config line 
'''

from collections import OrderedDict
import configbase
 


classlookup = {     "element" :           configbase.ConfigElement ,
                    "attribute" :         configbase.ConfigAttribute ,
                    "staticElement" :     configbase.ConfigStaticElement ,
                    "staticAttribute" :   configbase.ConfigStaticAttribute ,
                    "repeat" :            configbase.ConfigRepeat,
                    "messageid" :         None }

class XMLMessageConfig():
    
    """ 
    holds config data for an individual xml message defn
    """ 
    
    # class level dict of message types 
    xml_messages = OrderedDict()
 
    def __init__(self, name,  params, configdata):
        
        config_sections=configbase.get_sections(configdata)
        
        self.request_elems=[]
        self.response_elems=[]
       
        # populate request and reply data 
        
        if "request" in config_sections:
            for n,l in  config_sections["request"][1]:
                which,what=l.split("=") 
                if which=="valueCount":
                    self.value_count=what
                else:
                    lineclass=classlookup[which]
                    if lineclass:
                        self.request_elems.append(lineclass(n,what))
        
                
        if "reply" in config_sections:
            for n,l in  config_sections["reply"][1]:
                which,what=l.split("=") 
                if which=="valueCount":
                    self.value_count=what
                else:
                    lineclass=classlookup[which]
                    if lineclass:
                        self.response_elems.append(lineclass(n,what))
               
                    
        self.xml_messages[params[0]]=self
        self.messagetype=params[0]
        
        
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
        # get the XMLMessageConfig object for the given message type 
        return cls.xml_messages[messagetype]
    
    def get_request_elems(self):
        return self.request_elems
    
    def get_response_elems(self):
        return self.response_elems
    
#---------------------------------------------------------------------------------------------------------------------                    
    
        
class XMLRepeatConfig():
    
    """
    holds config data for an XML repeat section
    """
    # class level dict of repeat config types 
    xml_repeats = OrderedDict()
    
    def __init__(self, name, params, configdata):
         
        config_sections=configbase.get_sections(configdata)
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
                        self.elems.append(lineclass(n,what))
  
    
    def get_elems(self):
        return self.elems                    
                
    @classmethod
    def get_xml_repeat_config(cls,name):
        # get the XMLRepeatConfig object for the given name, referred to in message repeat elements 
        if name in cls.xml_repeats:
            return cls.xml_repeats[name]
        raise StandardError("XMLRepeat section %s not defined " % name )
    