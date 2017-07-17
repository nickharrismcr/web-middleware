'''
Created on 17 Jul 2017

@author: nick
'''
import config_xml
import xml.etree.ElementTree as ET
import etree_fns as ETF
from trace_decorator import trace 

class ConverterFactory(object):
    
    def __init__(self):
        pass
    
    @classmethod
    def create(cls,config,conn_dir,req_or_resp):
        if conn_dir=="source" and req_or_resp==config.REQUEST:
            return SSVToXML(config, config.REQUEST)
        elif conn_dir=="source" and req_or_resp==config.RESPONSE:
            return XMLToSSV(config,req_or_resp)
        elif conn_dir=="sink" and req_or_resp==config.REQUEST:
            return XMLToSSV(config,req_or_resp)
        elif conn_dir=="sink" and req_or_resp==config.RESPONSE:
            return SSVToXML(config,req_or_resp)
 

#--------------------------------------------------------------------------------------------------------------------
class XMLToSSV:
    
    """ 
    convert XML input for a specific message type to ssv using the relevant XMLMessageConfig and XMLRepeatConfig objects
    """ 
    
    def __init__(self,config,req_or_resp):
        
        self.req_or_resp=req_or_resp
        self.items=config
        self.messagetypes={}
        delim_elem="todelimiter" if req_or_resp == config.REQUEST else "fromdelimiter"
        self.delim=config.get("main",delim_elem,",")
        messageID_elem = "messageID" if req_or_resp==config.REQUEST else "replymessageID"
        self.messageIDpath=config.get("message", messageID_elem, None)
         
    #-----------------------------------------------------------------------------------------------        
    def convert(self, xml):
        
        lssv={}
        
        # read the incoming xml into a node tree 
        try:
            rootnode=ET.fromstring(xml)
        except:
            raise StandardError("Invalid input XML : \n %s ", xml )
 
        messagetypenode=ETF.get_node_at_path(rootnode, self.messageIDpath)
        if messagetypenode <> None:
            messagetype=messagetypenode.text 
        else:
            raise StandardError("No message type element in XML") 
        
        mc=config_xml.XMLMessageConfig.get_config(messagetype)    
        msg_elements = mc.get_request_elems() if self.req_or_resp==self.items.REQUEST else mc.get_response_elems()
 
        # for each xml element defined in the items, search the input xml tree for a matching path and get the value there
        if msg_elements != []:
            for elem in msg_elements:      
                self.addto_ssv(rootnode, elem, lssv )
        
        # expand any placeholder repeat groups in the ssv with their values 
        out=[messagetype]         
        for k in sorted(lssv.keys()):
            i=lssv[k]
            if isinstance(i,dict):
                for j in i.itervalues():
                    out.append(str(j))
            else:
                out.append(str(i))  
        
        rv=self.delim.join(out)
        return rv
    
    #-----------------------------------------------------------------------------------------------                  
    def addto_ssv(self,rootnode, elem, lssv, offset=0 ): 
            
        # each items element type queries the input xml tree in its own way 
        elem.addto_ssv(rootnode,lssv,offset)

    #-----------------------------------------------------------------------------------------------        
    def error(self):
        return "ERR\n"
        
                          
 
#--------------------------------------------------------------------------------------------------------------------------
class SSVToXML:
    
    """ 
    convert ssv input for a specific message type to XML using the relevant XMLMessageConfig and XMLRepeatConfig objects
    """ 
    
    def __init__(self,config,req_or_resp):
 
        self.items=config 
        self.req_or_resp=req_or_resp
        self.messagetypes={}
        delim_elem="todelimiter" if req_or_resp == config.REQUEST else "fromdelimiter"
        self.delim=config.get("main",delim_elem,",")
        messageID_elem = "messageID" if req_or_resp==config.REQUEST else "replymessageID"
        self.messageIDpath=config.get("message",messageID_elem,None) 
        
    #-----------------------------------------------------------------------------------------------        
    @trace("debug")
    def convert(self, ssv):
        
        if not self.delim in ssv:
            raise StandardError("Invalid input line : No delimiter found : %s ", ssv )

        lssv=ssv.split(self.delim)
        messagetype=lssv[0]
        
        mc=self.items.get_xmlconfig(messagetype)    
        msg_elements = mc.get_request_elems() if self.req_or_resp==self.items.REQUEST else mc.get_response_elems()
           
        rootnode=ET.Element("root")
        # add a root node to hang the output xml off 
        ETF.add_text_node_path(rootnode, self.messageIDpath,messagetype)
        # for each element in the request items, create an output xml node containing the corresponding ssv value 
        if msg_elements != []:
            for elem in msg_elements:     
                self.addto_xml(rootnode, elem, lssv )
        
        rv=ETF.pretty(rootnode[0])                            
        return rv
    
    #-----------------------------------------------------------------------------------------------        
    def addto_xml(self, rootnode, config_elem, lssv , offset=0 ): 
        
        config_elem.addto_xml(rootnode,lssv,offset)
              
    #-----------------------------------------------------------------------------------------------        
 
                            
 