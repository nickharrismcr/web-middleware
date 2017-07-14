'''
Created on 7 Jul 2017

@author: nick
'''
import xmlconfig, configbase
import logger as log 
import xml.etree.ElementTree as ET 
import etree_fns as ETF

             
class ConverterToXML:
    
    """ 
    convert ssv input for a specific message type to XML using the relevant XMLMessageConfig and XMLRepeatConfig objects
    """ 
    
    
    def __init__(self,config,direction):
        
        self.config=config
        self.direction=direction
        self.messagetypes={}
        delim_elem="todelimiter" if direction == config.REQUEST else "fromdelimiter"
        self.delim=config.get_worker_config_item("main",delim_elem,",")
        messageID_elem = "messageID" if direction==config.REQUEST else "replymessageID"
        self.messageIDpath=config.get_worker_config_item("message",messageID_elem,None) 
        
    #-----------------------------------------------------------------------------------------------        
    def convert_request(self, ssv):
        
        if not self.delim in ssv:
            raise StandardError("Invalid input line : No delimiter found : %s ", ssv )

        
        lssv=ssv.split(self.delim)
        messagetype=lssv[0]
        
        mc=xmlconfig.XMLMessageConfig.get_config(messagetype)    
        _, _req_elements, _resp_elements  =(mc.value_count, mc.get_request_elems(), mc.get_response_elems())
        if self.direction==self.config.REQUEST:
            msg_elements=_req_elements
        else:
            msg_elements=_resp_elements 
        
        rootnode=ET.Element("root")
        
        # add a root node to hang the output xml off 
        ETF.add_text_node_path(rootnode, self.messageIDpath,messagetype)
        
        # for each element in the request config, create an output xml node containing the corresponding ssv value 
        if msg_elements != []:
            for elem in msg_elements:     
                self.addto_xml(rootnode, elem, lssv )
        
        rv=ETF.pretty(rootnode[0])                            

        return rv
    
    #-----------------------------------------------------------------------------------------------        
    def addto_xml(self, rootnode, elem, lssv , offset=0 ): 
        
        # each config element creates a different xml node structure 
        
        if isinstance(elem,configbase.ConfigAttribute):
            
            ETF.add_attribute_path(rootnode, elem.path, elem.attribute, lssv[elem.ssv_col+offset] )
            
        elif isinstance(elem,configbase.ConfigElement):
            
            ETF.add_text_node_path(rootnode,elem.path,lssv[elem.ssv_col+offset]) 
            
        elif isinstance(elem,configbase.ConfigRepeat):
            
            # repeater element. get the repeat group config and recursively call this routine with the contents 
            
            repeats=int(lssv[elem.ssv_col+offset])
            nextcol=elem.startcol                  
            rc=xmlconfig.XMLRepeatConfig.get_xml_repeat_config(elem.xmlrepeatconfigname)
            repeatrootnode=ETF.add_node_path(rootnode,elem.path)
            cols_required=repeats*rc.value_count
            
            if nextcol+cols_required-1 > len(lssv):
                raise StandardError("Config line %s : insufficient ssv input columns")
                    
            for i in range(0,repeats):
                # add repeat tag
                currnode=ET.SubElement(repeatrootnode,  ETF.get_name(rc.repeattag))
                # add tags for repeating group
                for repelem in rc.get_elems():
                    ssv_offset=nextcol+(i*rc.value_count) 
                    self.addto_xml(currnode, repelem, lssv, ssv_offset)   
                    
            # pop ssv columns for repeating groups
            for _ in range(0,cols_required-1):
                del(lssv[nextcol])   
        
        elif isinstance(elem,configbase.ConfigStaticAttribute):
            
            ETF.add_attribute_path(rootnode, elem.path, elem.attribute, elem.value )
            
        elif isinstance(elem,configbase.ConfigStaticElement):
            
            ETF.add_text_node_path(rootnode, elem.path,  elem.value )

    #-----------------------------------------------------------------------------------------------        
 
                            
 