'''
Created on 7 Jul 2017

@author: nick
'''
import  xmlconfig, configbase, config 
import xml.etree.ElementTree as ET
import logger as log 
import etree_fns as ETF
from collections import OrderedDict
         
class ConverterToSSV:
    
    """ 
    convert XML input for a specific message type to ssv using the relevant XMLMessageConfig and XMLRepeatConfig objects
    """ 
    
    def __init__(self,config,direction):
        
        self.direction=direction
        self.config=config
        self.messagetypes={}
        delim_elem="todelimiter" if direction == config.REQUEST else "fromdelimiter"
        self.delim=config.get_worker_config_item("main",delim_elem,",")
        messageID_elem = "messageID" if direction==config.REQUEST else "replymessageID"
        self.messageIDpath=config.get_worker_config_item("message", messageID_elem, None)
         
    #-----------------------------------------------------------------------------------------------        
    def convert_request(self, xml):
        
        lssv={}
        
        try:
            rootnode=ET.fromstring(xml)
        except:
            raise StandardError("Invalid input xml : \n %s ", xml )
 
 
        messagetypenode=ETF.get_node_at_path(rootnode, self.messageIDpath)
        if messagetypenode <> None:
            messagetype=messagetypenode.text 
        else:
            raise StandardError("No message type") 
        
        mc=xmlconfig.XMLMessageConfig.get_config(messagetype)    
        _, _req_elements, _resp_elements =(mc.value_count, mc.get_request_elems(), mc.get_response_elems())
        
        if self.direction==self.config.REQUEST:
            msg_elements=_req_elements
        else:
            msg_elements=_resp_elements 
 
        # for each xml element defined in the config, search the input xml tree for a matching path and get the value there
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
            
        # each config element type queries the input xml tree in its own way 
           
        if isinstance(elem,configbase.ConfigAttribute):
            
            lssv[elem.ssv_col+offset]=""
            node=ETF.get_node_at_path(rootnode,elem.path)
            if node != None:
                if elem.attribute in node.attrib:
                    lssv[elem.ssv_col+offset]=node.attrib[elem.attribute]
            
        elif isinstance(elem,configbase.ConfigElement):
            
            lssv[elem.ssv_col+offset]=""
            node=ETF.get_node_at_path(rootnode,elem.path)
            if node != None:
                lssv[elem.ssv_col+offset]=node.text
            
        elif isinstance(elem,configbase.ConfigRepeat):
            
            ssv_col_for_repeat = elem.ssv_col
            ssv_col_for_items = elem.startcol 
            
            tempssv=OrderedDict()
            
            repeatroot=ETF.get_node_at_path(rootnode, elem.path)                  
            rc=xmlconfig.XMLRepeatConfig.get_xml_repeat_config(elem.xmlrepeatconfigname)
            vals=rc.value_count
            repeatcount=0
            for child in repeatroot:
               
                for elem in rc.get_elems():
                    target=ETF.get_node_at_path(child,elem.path)
                    if target <> None:
                        self.addto_ssv(target,elem,tempssv,vals*repeatcount)
                repeatcount+=1
                
            lssv[ssv_col_for_repeat]=repeatcount
            lssv[ssv_col_for_items]=tempssv 
            
 

    #-----------------------------------------------------------------------------------------------        
    def error(self):
        return "ERR\n"
        
                          
 