'''
Created on 9 Jul 2017

@author: nick

items element classes and util functions

'''

from collections import OrderedDict
import re
import xml.etree.ElementTree as ET
import etree_fns as ETF 
 

re_subsection = re.compile("^<.*>")

#---------------------------------------------------------------------------------------------------------------------                    
def get_subsection(line):
    
    return line.split("<")[1].split(">")[0].split()
    
#------------------------------------------------------------------------------------------------
def get_sections(indata):
        
    """
    takes a items section and returns a dictionary of subsections : (params,block)
    """ 
    
    indict=OrderedDict()
    curr_subsection="main"
    block=[]
    params=[]
   
    for number,line in indata:
        
        if re_subsection.search(line)!=None:
   
            indict[curr_subsection]=(params,block)
            s=get_subsection(line)   
            curr_subsection=s[0]
            params=[]
            if len(s)>1:
                params=s[1:]
            block=[]
       
        else:
            block.append((number,line))
        
    
    indict[curr_subsection]=(params,block)
    return indict


def get_section(line):
    return line.split("[")[1].split("]")[0].split()
     
#--------------------------------------------------------------------------------------------------------------------- 
def read_delimiter(data):
     
    if data[0] in ('"',"'"):
        return data[1]
    if data[0]=='0':
        return chr(int(data,8))
    return chr(int(data))
 
#--------------------------------------------------------------------------------------------------------------------- #---------------------------------------------------------------------------------------------------------------------                    
def read_message_id(data):
    return data.split(",")[1] 
 
#---------------------------------------------------------------------------------------------------------------------                    
def read_config(readers, what, data):
     
    """ 
    read a items line value using a reader func if defined in readers[] else return the item raw 
    """ 
    
    if what in readers:
        try:
            return readers[what](data)
        except Exception,e:
            raise StandardError("Invalid configuration %s=%s : %s " % (what,data,str(e)))
    else:
        return data

#---------------------------------------------------------------------------------------------------------------------                    
class ConfigElement(object): 
    
    """ 
    holds data for an individual element type items line
    and knows how to add it to an xml tree 
    """

    def __init__(self,config, lineno, what):
       
        path,col=what.split(",")
        self.lineno=lineno
        self.path=path
        self.ssv_col=int(col)-1
        self.items=config
       
    def addto_xml(self, rootnode, lssv , offset=0 ): 
    
        ETF.add_text_node_path(rootnode,self.path,lssv[self.ssv_col+offset]) 
 
    def addto_ssv(self,rootnode,lssv,offset):   
            lssv[self.ssv_col+offset]=""
            node=ETF.get_node_at_path(rootnode,self.path)
            if node != None:
                lssv[self.ssv_col+offset]=node.text
 
           
    def __str__(self):
        return "items element %s|%s" %( self.path,self.ssv_col)
    
    def __repr__(self):
        return "items element %s|%s" %( self.path,self.ssv_col)
 
    
    
#---------------------------------------------------------------------------------------------------------------------                    
class ConfigAttribute(object):
    
    """
    holds data for an individual attribute type items line
    """ 
    
    def __init__(self,config, lineno, what):
        
        path,attrib,col=what.split(",")
        self.lineno=lineno
        self.path=path
        self.attribute=attrib 
        self.ssv_col=int(col)-1
        self.items=config

    def addto_xml(self, rootnode, lssv , offset=0 ): 
        
        ETF.add_attribute_path(rootnode, self.path, self.attribute, lssv[self.ssv_col+offset] )
    
    def addto_ssv(self,rootnode,lssv,offset):       

        lssv[self.ssv_col+offset]=""
        node=ETF.get_node_at_path(rootnode,self.path)
        if node != None:
            if self.attribute in node.attrib:
                lssv[self.ssv_col+offset]=node.attrib[self.attribute]          
    
    def __str__(self):
        return "items attribute %s|%s|%s" %( self.path,self.attribute,self.ssv_col)
    
    def __repr__(self):
        return "items attribute %s|%s|%s" %( self.path,self.attribute,self.ssv_col)
 
   
    
    
#---------------------------------------------------------------------------------------------------------------------                    
class ConfigRepeat(object):
    
    """ 
    holds data for an individual repeat type items line
    """
    
    def __init__(self,config, lineno, what):
        
        self.xmlrepeatconfigname, path, startcol, col = what.split(",")
        self.lineno=lineno
        self.path=path
        self.startcol=int(startcol)-1
        self.ssv_col=int(col)-1
        self.items=config

    def addto_xml(self, rootnode, lssv , offset=0 ): 
        
            # repeater element. get the repeat group items and recursively call this routine with the contents 
            
            repeats=int(lssv[self.ssv_col+offset])
            nextcol=self.startcol                  
            rc=self.items.get_xmlrepeatconfig(self.xmlrepeatconfigname)
            repeatrootnode=ETF.add_node_path(rootnode,self.path)
            cols_required=repeats*rc.value_count
            
            if nextcol+cols_required-1 > len(lssv):
                raise StandardError("Config line %s : insufficient ssv input columns")
                    
            for i in range(0,repeats):
                # add repeat tag
                currnode=ET.SubElement(repeatrootnode,  ETF.get_name(rc.repeattag))
                # add tags for repeating group
                for repelem in rc.get_elems():
                    ssv_offset=nextcol+(i*rc.value_count) 
                    repelem.addto_xml(currnode,lssv, ssv_offset)   
                    
            # pop ssv columns for repeating groups
            for _ in range(0,cols_required-1):
                del(lssv[nextcol])   
        
    def addto_ssv(self,rootnode,lssv,offset):
        
        ssv_col_for_repeat = self.ssv_col
        ssv_col_for_items = self.startcol 
        
        tempssv=OrderedDict()
        
        repeatroot=ETF.get_node_at_path(rootnode, self.path)                  
        rc=self.items.get_xmlrepeatconfig(self.xmlrepeatconfigname)
        vals=rc.value_count
        repeatcount=0
        for child in repeatroot:
           
            for elem in rc.get_elems():
                target=ETF.get_node_at_path(child,self.path)
                if target <> None:
                    elem.addto_ssv(target,tempssv,vals*repeatcount)
            repeatcount+=1
            
        lssv[ssv_col_for_repeat]=repeatcount
        lssv[ssv_col_for_items]=tempssv 
        

    
                
    def __str__(self):
        return "items repeat %s|%s|%s " % ( self.path , self.startcol, self.ssv_col)
    
    def __repr__(self):
        return "items repeat %s|%s|%s " % ( self.path , self.startcol, self.ssv_col)
 
#---------------------------------------------------------------------------------------------------------------------                    
class ConfigStaticElement(object):
    
    """ 
    holds data for an individual static element type items line
    """

    def __init__(self,config, lineno, what):
       
        path,value=what.split(",")
        self.lineno=lineno
        self.path=path
        self.value=value
        self.items=config
         
    def addto_xml(self, rootnode, lssv , offset=0 ): 
        
        ETF.add_text_node_path(rootnode, self.path, self.value )
        
    def addto_ssv(self,rootnode,lssv,offset):      
        
        pass   
    
    def __str__(self):
        return "static items element : "+self.path   +"|"+self.value  
    
    def __repr__(self):
        return "static items element : "+self.path   +"|"+self.value  
 
    
#---------------------------------------------------------------------------------------------------------------------                    
class ConfigStaticAttribute(object):
    
    """
    holds data for an individual static attribute type items line
    """ 
    
    def __init__(self,config, lineno, what):
        
        path,attrib,value=what.split(",")
        self.lineno=lineno
        self.path=path
        self.attribute=attrib 
        self.value=value
        self.items=config 

    def addto_xml(self, rootnode, lssv , offset=0 ): 
        
        ETF.add_attribute_path(rootnode, self.path, self.attribute, self.value )

    def addto_ssv(self,rootnode,lssv,offset):      
        
        pass   
          
    def __str__(self):
        return "static items attribute "+self.path+"|"+self.attribute+"|"+self.value
    
    def __repr__(self):
        return "static items attribute "+self.path+"|"+self.attribute+"|"+self.value
        
#---------------------------------------------------------------------------------------------------------------------                    

