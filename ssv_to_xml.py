'''
Created on 7 Jul 2017

@author: nick
'''
import xmlconfig
import config 
import xml.etree.ElementTree as ET 
import etree_fns as ETF

from trace_decorator import trace 

             
class SSVToXML:
    
    """ 
    convert ssv input for a specific message type to XML using the relevant XMLMessageConfig and XMLRepeatConfig objects
    """ 
    
    
    def __init__(self,config,direction):
 
        self.items=config 
        self.direction=direction
        self.messagetypes={}
        delim_elem="todelimiter" if direction == config.REQUEST else "fromdelimiter"
        self.delim=config.worker_item("main",delim_elem,",")
        messageID_elem = "messageID" if direction==config.REQUEST else "replymessageID"
        self.messageIDpath=config.worker_item("message",messageID_elem,None) 
        
    #-----------------------------------------------------------------------------------------------        
    @trace("debug")
    def convert(self, ssv):
        
        if not self.delim in ssv:
            raise StandardError("Invalid input line : No delimiter found : %s ", ssv )

        lssv=ssv.split(self.delim)
        messagetype=lssv[0]
        
        mc=self.items.get_xmlconfig(messagetype)    
        _, _req_elements, _resp_elements  =(mc.value_count, mc.get_request_elems(), mc.get_response_elems())
        if self.direction==self.items.REQUEST:
            msg_elements=_req_elements
        else:
            msg_elements=_resp_elements 
        
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
 
                            
 