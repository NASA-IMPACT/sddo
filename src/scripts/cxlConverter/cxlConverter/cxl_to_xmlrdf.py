# creator: eleisa@rpi.edu
# date_created 04/25/2021
#!/usr/bin/env python
# coding: utf-8

# In[2]:


import xml.etree.ElementTree as ET


# In[17]:


## read & examine cxl

tree = ET.parse('./input/SMD_ConceptualIM20210407a_RED.xml')
# tree = ET.parse('./cmap_export.cxl')

root = tree.getroot()

print("root:",root)

## print concept nodes and their contents
for concept in root.iter('concept'):
    print(concept,concept.attrib)


# In[59]:


def read_cxl(filename):
    
    tree = ET.parse(filename)
    root = tree.getroot()

#     print(root)
    
    concepts = {}
    concept_defs = {}

    for neighbor in root.iter('concept'):
        
    
    #     print(neighbor.attrib)
    #     print(neighbor.attrib['id']+"  "+neighbor.attrib['label'])

        concept_id = neighbor.attrib['id']
        concept_label = neighbor.attrib['label']

        concepts[concept_id] = concept_label

        concept_defs[concept_label] = []

    props = set()
    properties = {}
    prop_labels = []
    
    for neighbor in root.iter('linking-phrase'):
    
    #     print(neighbor.attrib)
    #     print(neighbor.attrib['id']+"  "+neighbor.attrib['label'])

        prop_id = neighbor.attrib['id']
        prop_label = neighbor.attrib['label']

        properties[prop_id] = prop_label
        props.add(prop_label)
        
        prop_labels.append(prop_label)

    triples = set()
    
    for neighbor in root.iter('connection'):
    
    #     print(neighbor.attrib)

        from_id = neighbor.attrib['from-id']
        to_id = neighbor.attrib['to-id']

        if from_id in concepts.keys():

            from_label = concepts[from_id]
            prop_label = properties[to_id]
            toLabel = ""

            for neighbor1 in root.iter('connection'):

                from_id1 = neighbor1.attrib['from-id']
                to_id1 = neighbor1.attrib['to-id']

                if from_id1 == to_id:
                    to_label = concepts[to_id1]

            triples.add((from_label,prop_label,to_label))
            
            if from_label not in concept_defs.keys():
                concept_defs[from_label] = [(prop_label,to_label)]
            else:
                if (prop_label,to_label) not in concept_defs[from_label]:
                    concept_defs[from_label].append((prop_label,to_label))

        elif from_id in properties.keys():

            from_label = ""
            prop_label = properties[from_id]
            to_label = concepts[to_id]

            for neighbor1 in root.iter('connection'):

                from_id1 = neighbor1.attrib['from-id']
                to_id1 = neighbor1.attrib['to-id']

                if from_id == to_id1:
                    from_label = concepts[from_id1]

            triples.add((from_label,prop_label,to_label))
        
            if from_label not in concept_defs.keys():
                concept_defs[from_label] = [(prop_label,to_label)]
            else:
                if (prop_label,to_label) not in concept_defs[from_label]:
                    concept_defs[from_label].append((prop_label,to_label))
            
    return concepts,concept_defs,properties,prop_labels,triples


# In[60]:

def main():
    filename = './input/SMD_ConceptualIM20210407a_RED.xml'
    
    concepts,concept_defs,properties,prop_labels,triples = read_cxl(filename)


# In[63]:


# concepts
# concept_defs
# properties
# prop_labels


# In[66]:


## put together xml

    xml = '<?xml version="1.0" encoding="UTF-8"?><rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:smd="http://smd.dev/schema#" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:vcard="http://www.w3.org/2001/vcard-rdf/3.0#" xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#" xmlns:owl2="http://www.w3.org/2006/12/owl2-xml#" xmlns:owl="http://www.w3.org/2002/07/owl#" xmlns:skos="http://www.w3.org/2004/02/skos/core#">'
    
    for concept_label in concept_defs.keys():
            
        clean_label = concept_label
        
        ### SPECIAL CHARS ###
        if '&' in clean_label:
            clean_label = clean_label.replace('&','&amp;')
        
        ## OWL
        xml += '<rdf:Description rdf:about="http://smd.dev/schema#'+clean_label+'"><rdf:type rdf:resource="http://www.w3.org/2002/07/owl#Class"/><rdfs:label xml:lang="en-US">'+clean_label+'</rdfs:label>'
        
        ## SKOS
    #     xml += '<skos:Concept rdf:about="http://smd.dev/schema#'+clean_label+'"><rdfs:label xml:lang="en-US">'+clean_label+'</rdfs:label>'
        
        
        if len(concept_defs[concept_label])>0:
            for prop_rel in concept_defs[concept_label]:
                
    #             print(prop_rel)
                
                clean_prop_label = prop_rel[0]
                clean_object_label = prop_rel[1]
                
                ### NO SPACES IN PROP NAME ###
                if clean_prop_label == 'is a':
                    clean_prop_label = 'is-a'
                                    
                ### SPECIAL CHARS ###
                if '&' in clean_object_label:
                    clean_object_label = clean_object_label.replace('&','&amp;')
            
                xml += '<smd:'+clean_prop_label+' rdf:resource="http://smd.dev/schema#'+clean_object_label+'"/>'
            
        ## OWL
        xml += '</rdf:Description>'
    
        ## SKOS
    #     xml += '</skos:Concept>'
        
    for prop in prop_labels:
    
        ### NO SPACES IN PROP NAME ###
        if prop == 'is a':
            prop = 'is-a'
        
        ## OWL (consistent with SKOS)
        xml += '<rdf:Description rdf:about="http://smd.dev/schema#'+prop+'"><rdfs:label xml:lang="en-US">'+prop+'</rdfs:label>'
        
        xml += '<rdf:type rdf:resource="http://www.w3.org/2002/07/owl#ObjectProperty"/>'
        
        xml += '</rdf:Description>'
        
    # for triple in triples:
        
    # #     print('smd:'+tripl[0])
        
    #     xml += '<rdf:Description rdf:about="'+'smd:'+triple[0]+'"> '+'<smd:'+triple[1]+' '+'rdf:resource="'+'smd:'+triple[2]+'"/></rdf:Description>'
    
            
            
    xml += "</rdf:RDF>"
    
    
    # In[67]:
    
    
    print(xml.replace("'",""))
    
    
    # In[68]:
    
    
    ## output extracted classes,triples to XMLRDF
    with open('./'+filename.split('.')[0]+'_XMLRDF.xml','w') as xmlfile:
        xmlfile.write(xml)


# In[12]:


## output triples as edgelist
# with open('./'+filename.split('.')[0]+'_edgelist.csv','w') as csvfile:
#     for key in classes.keys():
#         if (len(classes[key])>0):
#             for pair in classes[key]:
#                 csvfile.write(key+','+pair[0]+','+pair[1]+'\n')
if __name__ == "__main__":
    main() 
