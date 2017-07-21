'''
Created on 9 Jul 2017

@author: nick

config message element classes and util functions for parsing the config file 

'''

from collections import OrderedDict
import re
import xml.etree.ElementTree as ET
import etree_fns as ETF 
 
re_subsection = re.compile("^<.*>")
from trace_decorator import trace 

#---------------------------------------------------------------------------------------------------------------------                    
def get_subsection(line):
    
    return line.split("<")[1].split(">")[0].split()
    
#------------------------------------------------------------------------------------------------
def get_sections(indata):
        
    """
    takes a config section and returns a dictionary of { subsections : (params,block) } 
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

#--------------------------------------------------------------------------------------------------------------------- 
def get_section(line):
    return line.split("[")[1].split("]")[0].split()
     
#--------------------------------------------------------------------------------------------------------------------- 
def read_string(data):
    return data 

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
def read_config(fields, what, data):
     
    """ 
    read a config line value using a reader func if defined in readers[] else return the item raw 
    """ 
    
    if what in fields:
        try:
            return fields[what][0](data)
        except Exception,e:
            raise ParsingError("Invalid configuration %s=%s : %s " % (what,data,str(e)))
    else:
        return data
#---------------------------------------------------------------------------------------------------------------------      
def check_config(name, fields,items):
    
    for field,t in fields.iteritems():
        _,mandatory=t 
        myassert ( not mandatory or field in items , "%s %s not defined " % (name, field))
            
#---------------------------------------------------------------------------------------------------------------------      
class ParsingError(Exception):
    pass 
#---------------------------------------------------------------------------------------------------------------------       
def myassert(cond, error):
    
    if not cond:
        raise ParsingError(error)
    
#---------------------------------------------------------------------------------------------------------------------       
# classes for message config elements.  all have methods for 
# * getting text content of their specified xml node from the passed in tree and adding it to the ssv list, 
# * getting an ssv list value and creating an xml node on the passed in tree containing it as text. 
              
class ConfigElement(object): 
    
    """ 
    holds data for an individual element type config line
    """

    def __init__(self,config, lineno, what):
       
        path,col=what.split(",")
        self.lineno=lineno
        self.path=path
        self.ssv_col=int(col)-1
        self.config=config
       
    def addto_xml(self, rootnode, lssv , offset=0 ): 
    
        ETF.add_text_node_path(rootnode,self.path,lssv[self.ssv_col+offset]) 
 
    def addto_ssv(self,rootnode,lssv,offset):   
            lssv[self.ssv_col+offset]=""
            node=ETF.get_node_at_path(rootnode,self.path)
            if node != None:
                lssv[self.ssv_col+offset]=node.text
 
           
    def __str__(self):
        return "config element %s|%s" %( self.path,self.ssv_col)
    
    def __repr__(self):
        return "config element %s|%s" %( self.path,self.ssv_col)
 
    
    
#---------------------------------------------------------------------------------------------------------------------                    
class ConfigAttribute(object):
    
    """
    holds data for an individual attribute type config line
    """ 
    
    def __init__(self,config, lineno, what):
        
        path,attrib,col=what.split(",")
        self.lineno=lineno
        self.path=path
        self.attribute=attrib 
        self.ssv_col=int(col)-1
        self.config=config

    def addto_xml(self, rootnode, lssv , offset=0 ): 
        
        ETF.add_attribute_path(rootnode, self.path, self.attribute, lssv[self.ssv_col+offset] )
    
    def addto_ssv(self,rootnode,lssv,offset):       

        lssv[self.ssv_col+offset]=""
        node=ETF.get_node_at_path(rootnode,self.path)
        if node != None:
            if self.attribute in node.attrib:
                lssv[self.ssv_col+offset]=node.attrib[self.attribute]          
    
    def __str__(self):
        return "config attribute %s|%s|%s" %( self.path,self.attribute,self.ssv_col)
    
    def __repr__(self):
        return "config attribute %s|%s|%s" %( self.path,self.attribute,self.ssv_col)
 
   
    
    
#---------------------------------------------------------------------------------------------------------------------                    
class ConfigRepeat(object):
    
    """ 
    holds data for an individual repeat type config line
    """
    
    def __init__(self,config, lineno, what):
        
        self.xmlrepeatconfigname, path, startcol, col = what.split(",")
        self.lineno=lineno
        self.path=path
        self.startcol=int(startcol)-1
        self.ssv_col=int(col)-1
        self.config=config

    @trace("debug")
    def addto_xml(self, rootnode, lssv , offset=0 ): 
        
            # repeater element. get the repeat group config and process its elements 
            
            repeats=int(lssv[self.ssv_col+offset])
            nextcol=self.startcol                  
            rc=self.config.get_xmlrepeatconfig(self.xmlrepeatconfigname)
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
        rc=self.config.get_xmlrepeatconfig(self.xmlrepeatconfigname)
        vals=rc.value_count
        repeatcount=0
        for child in repeatroot:
           
            for elem in rc.get_elems():
                target=ETF.get_node_at_path(child,elem.path)
                if target <> None:
                    elem.addto_ssv(target,tempssv,vals*repeatcount)
            repeatcount+=1
            
        lssv[ssv_col_for_repeat]=repeatcount
        lssv[ssv_col_for_items]=tempssv 
        

    
                
    def __str__(self):
        return "config repeat %s|%s|%s " % ( self.path , self.startcol, self.ssv_col)
    
    def __repr__(self):
        return "config repeat %s|%s|%s " % ( self.path , self.startcol, self.ssv_col)
 
#---------------------------------------------------------------------------------------------------------------------                    
class ConfigStaticElement(object):
    
    """ 
    holds data for an individual static element type config line
    """

    def __init__(self,config, lineno, what):
       
        path,value=what.split(",")
        self.lineno=lineno
        self.path=path
        self.value=value
        self.config=config
         
    def addto_xml(self, rootnode, lssv , offset=0 ): 
        
        ETF.add_text_node_path(rootnode, self.path, self.value )
        
    def addto_ssv(self,rootnode,lssv,offset):      
        
        pass   
    
    def __str__(self):
        return "static config element : "+self.path   +"|"+self.value  
    
    def __repr__(self):
        return "static config element : "+self.path   +"|"+self.value  
 
    
#---------------------------------------------------------------------------------------------------------------------                    
class ConfigStaticAttribute(object):
    
    """
    holds data for an individual static attribute type config line
    """ 
    
    def __init__(self,config, lineno, what):
        
        path,attrib,value=what.split(",")
        self.lineno=lineno
        self.path=path
        self.attribute=attrib 
        self.value=value
        self.config=config 

    def addto_xml(self, rootnode, lssv , offset=0 ): 
        
        ETF.add_attribute_path(rootnode, self.path, self.attribute, self.value )

    def addto_ssv(self,rootnode,lssv,offset):      
        
        pass   
          
    def __str__(self):
        return "static config attribute "+self.path+"|"+self.attribute+"|"+self.value
    
    def __repr__(self):
        return "static config attribute "+self.path+"|"+self.attribute+"|"+self.value
        
#---------------------------------------------------------------------------------------------------------------------                    

