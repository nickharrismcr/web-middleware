'''
Created on 7 Jul 2017

@author: nick
'''

import config_xml
import xml.etree.ElementTree as ET
import etree_fns as ETF
         
class XMLToSSV:
    
    """ 
    convert XML input for a specific message type to ssv using the relevant XMLMessageConfig and XMLRepeatConfig objects
    """ 
    
    def __init__(self,config,direction):
        
        self.direction=direction
        self.items=config
        self.messagetypes={}
        delim_elem="todelimiter" if direction == config.REQUEST else "fromdelimiter"
        self.delim=config.worker_item("main",delim_elem,",")
        messageID_elem = "messageID" if direction==config.REQUEST else "replymessageID"
        self.messageIDpath=config.worker_item("message", messageID_elem, None)
         
    #-----------------------------------------------------------------------------------------------        
    def convert(self, xml):
        
        lssv={}
        
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
        msg_elements = mc.get_request_elems() if self.direction==self.items.REQUEST else mc.get_response_elems()
 
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
        
                          
 