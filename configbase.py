'''
Created on 9 Jul 2017

@author: nick

config element classes and util functions

'''

from collections import OrderedDict
import re

re_subsection = re.compile("^<.*>")

#---------------------------------------------------------------------------------------------------------------------                    
def get_subsection(line):
    
    return line.split("<")[1].split(">")[0].split()
    
#------------------------------------------------------------------------------------------------
def get_sections(indata):
        
    """
    takes a config section and returns a dictionary of subsections : (params,block)
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
    read a config line value using a reader func if defined in readers[] else return the item raw 
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
    holds data for an individual element type config line
    """

    def __init__(self, lineno, what):
       
        path,col=what.split(",")
        self.lineno=lineno
        self.path=path
        self.ssv_col=int(col)-1
       
    
    def __str__(self):
        return "config element %s|%s" %( self.path,self.ssv_col)
    
    def __repr__(self):
        return "config element %s|%s" %( self.path,self.ssv_col)
 
    
    
#---------------------------------------------------------------------------------------------------------------------                    
class ConfigAttribute(object):
    
    """
    holds data for an individual attribute type config line
    """ 
    
    def __init__(self, lineno, what):
        
        path,attrib,col=what.split(",")
        self.lineno=lineno
        self.path=path
        self.attribute=attrib 
        self.ssv_col=int(col)-1

    
                    
    def __str__(self):
        return "config attribute %s|%s|%s" %( self.path,self.attribute,self.ssv_col)
    
    def __repr__(self):
        return "config attribute %s|%s|%s" %( self.path,self.attribute,self.ssv_col)
 
   
    
    
#---------------------------------------------------------------------------------------------------------------------                    
class ConfigRepeat(object):
    
    """ 
    holds data for an individual repeat type config line
    """
    
    def __init__(self, lineno, what):
        
        xmlrepeatconfigname, path, startcol, col = what.split(",")
        self.lineno=lineno
        self.xmlrepeatconfigname=xmlrepeatconfigname
        self.path=path
        self.startcol=int(startcol)-1
        self.ssv_col=int(col)-1
   
                    
    def __str__(self):
        return "config repeat %s|%s|%s " % ( self.path , self.startcol, self.ssv_col)
    
    def __repr__(self):
        return "config repeat %s|%s|%s " % ( self.path , self.startcol, self.ssv_col)
 
#---------------------------------------------------------------------------------------------------------------------                    
class ConfigStaticElement(object):
    
    """ 
    holds data for an individual static element type config line
    """

    def __init__(self, lineno, what):
       
        path,value=what.split(",")
        self.lineno=lineno
        self.path=path
        self.value=value
       
    
    def __str__(self):
        return "static config element : "+self.path   +"|"+self.value  
    
    def __repr__(self):
        return "static config element : "+self.path   +"|"+self.value  
 
    
    
#---------------------------------------------------------------------------------------------------------------------                    
class ConfigStaticAttribute(object):
    
    """
    holds data for an individual static attribute type config line
    """ 
    
    def __init__(self, lineno, what):
        
        path,attrib,value=what.split(",")
        self.lineno=lineno
        self.path=path
        self.attribute=attrib 
        self.value=value

    
                    
    def __str__(self):
        return "static config attribute "+self.path+"|"+self.attribute+"|"+self.value
    
    def __repr__(self):
        return "static config attribute "+self.path+"|"+self.attribute+"|"+self.value
 
   
    
    
