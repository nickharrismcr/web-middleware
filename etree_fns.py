'''
Created on 12 Jul 2017

@author: nick

util functions for the xml.etree.ElementTree lib 

'''
import re
import xml.etree.ElementTree as ET

re_split=re.compile("><")

def get_path_list(path):
    
    """
    converts a path <tag1><tag2><tag2> to a list [ "tag1,"tag2",tag3" ] 
    """
    
    return re_split.split(path[1:-1])

def add_text_node_path(node, path,val):

    pathlist=get_path_list(path)
    return add_text_node_list(node, pathlist,val)
    
def add_text_node_list(node, pathlist, val ):
    
    new=add_node_list(node,pathlist)
    new.text=val 
    return new 

def add_attribute_path(node, path, attrib, val):

    pathlist=get_path_list(path)
    return add_attribute_list(node, pathlist,attrib, val)

def add_attribute_list(node, pathlist, attrib, val ):
    
    new=add_node_list(node,pathlist) 
    new.set(attrib,val)
    return new 

def add_node_path(node, path):

    pathlist=get_path_list(path)
    return add_node_list(node, pathlist)
    
def add_node_list(node, pathlist ):
    
    if len(pathlist)==1:
        new=node.find(pathlist[0])
        if new==None:
            new=ET.SubElement(node, pathlist[0])
        return new
    
    ch=node.find(pathlist[0])
    if ch == None:
        new=ET.SubElement(node, pathlist[0])
        return add_node_list(new,pathlist[1:])
    else:
        return add_node_list(ch,pathlist[1:])

def get_node_at_path(node,path):

    pathlist=get_path_list(path)

    for elem in pathlist:
        if node.tag==elem:
            continue 
        ch=node.find(elem)
        if ch == None:
            return None
        node=ch

    return node 

      
def pretty(node,indent=0,out=""):
   
    attribs=[ '%s="%s"' % (a,b) for a,b in node.attrib.iteritems() ]
    attrs=" "+" ".join(attribs) if len(attribs)>0 else ""
    
    if node.text <> None and node.text.strip() <> "" :    
        out+="%s<%s%s>%s</%s>\n" % (" "*indent*3,node.tag,attrs,node.text,node.tag)
    else:
        out+="%s<%s%s>\n" % (" "*indent*3,node.tag,attrs)
        indent+=1
        for c in node:
            out=pretty(c,indent,out)
        indent-=1
        out+="%s</%s>\n" % (" "*indent*3,node.tag)
        
    return out
 
def get_name(s):
     
    return s.split("<")[1].split(">")[0]

# unit test           
if __name__=="__main__":
    
    root=ET.Element("root")
    add_attribute_path(root, "<att1><att2><att3>", "att3att", "att3attval")
    add_text_node_path(root,"<lev1><lev2a><lev3a>", "value")
    add_text_node_path(root,"<lev1><lev2b><lev3b>", "value2")
    add_attribute_path(root, "<lev1><lev2b><lev3b>", "attrib3b","val3b")
    add_text_node_path(root, "<att1><att2><att3>", "att3val")
 
    print pretty(root)
    
 
