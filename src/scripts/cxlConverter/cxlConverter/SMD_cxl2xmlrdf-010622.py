import xml.etree.ElementTree as ET

## parse cxl and extract classes and properties
def process_cxl(filename):
    
    ## read and parse cxl (xml) file into a tree
    tree = ET.parse(filename)
    root = tree.getroot()

    ## initialize dicts for classes
    classDict = {}
    classDefs = {}

    for neighbor in root.iter('concept'):
    ## sometimes tags contain the namespace, if so use the next line instead of the previous
#     for neighbor in root.iter('{http://cmap.ihmc.us/xml/cmap/}concept'):

        classId = neighbor.attrib['id']
        classLabel = neighbor.attrib['label']

        classDict[classId] = classLabel

        classDefs[classLabel] = []

    ## initalize data structures for properties
    props = set()
    propDict = {}
    propDefs = []

    for neighbor in root.iter('linking-phrase'):
    ## sometimes tags contain the namespace, if so use the next line instead of the previous
#     for neighbor in root.iter('{http://cmap.ihmc.us/xml/cmap/}linking-phrase'):

        propId = neighbor.attrib['id']
        propLabel = neighbor.attrib['label']

        propDict[propId] = propLabel
        props.add(propLabel)
        
        propDefs.append(propLabel)

    triples = set()
  
    for neighbor in root.iter('connection'):
    ## sometimes tags contain the namespace, if so use the next line instead of the previous
#     for neighbor in root.iter('{http://cmap.ihmc.us/xml/cmap/}connection'):

        fromId = neighbor.attrib['from-id']
        toId = neighbor.attrib['to-id']

        if fromId in classDict.keys():

            fromLabel = classDict[fromId]
            propLabel = propDict[toId]
            toLabel = ""

            for neighbor1 in root.iter('connection'):
            ## sometimes tags contain the namespace, if so use the next line instead of the previous
#             for neighbor1 in root.iter('{http://cmap.ihmc.us/xml/cmap/}connection'):

                fromId1 = neighbor1.attrib['from-id']
                toId1 = neighbor1.attrib['to-id']

                if fromId1 == toId:
                    toLabel = classDict[toId1]

            triples.add((fromLabel,propLabel,toLabel))
            
            if fromLabel not in classDefs.keys():
                classDefs[fromLabel] = [(propLabel,toLabel)]
            else:
                if (propLabel,toLabel) not in classDefs[fromLabel]:
                    classDefs[fromLabel].append((propLabel,toLabel))

        elif fromId in propDict.keys():

            fromLabel = ""
            propLabel = propDict[fromId]
            toLabel = classDict[toId]

            for neighbor1 in root.iter('connection'):
            ## sometimes tags contain the namespace, if so use the next line instead of the previous
#             for neighbor1 in root.iter('{http://cmap.ihmc.us/xml/cmap/}connection'):

                fromId1 = neighbor1.attrib['from-id']
                toId1 = neighbor1.attrib['to-id']

                if fromId == toId1:
                    fromLabel = classDict[fromId1]

            triples.add((fromLabel,propLabel,toLabel))
        
            if fromLabel not in classDefs.keys():
                classDefs[fromLabel] = [(propLabel,toLabel)]
            else:
                if (propLabel,toLabel) not in classDefs[fromLabel]:
                    classDefs[fromLabel].append((propLabel,toLabel))
            
    return classDefs,propDefs


if __name__ == '__main__':
    filename = "BIO-ConceptualModel20220104RED.cxl"
    classes, properties = process_cxl("./input/"+filename)

    ## Wrap classes and properties in XMLRDF tags
    xml = '<?xml version="1.0" encoding="UTF-8"?><rdf:RDF xmlns="http://purl.obolibrary.org/obo/sddo.owl#" xml:base="http://purl.obolibrary.org/obo/sddo.owl" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:sddo="http://sddo/schema/" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:vcard="http://www.w3.org/2001/vcard-rdf/3.0#" xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#" xmlns:owl2="http://www.w3.org/2006/12/owl2-xml#" xmlns:owl="http://www.w3.org/2002/07/owl#" xmlns:skos="http://www.w3.org/2004/02/skos/core#">'
    namespace = 'http://purl.obolibrary.org/obo/'

    ## owl-specific
    xml += '<owl:Ontology  rdf:about="http://purl.obolibrary.org/obo/sddo.owl">'
#     xml += '</owl:Ontology>'

    ## URIs
#     URIs = entities

    for classLabel in classes.keys():

        ## remove spaces, commas and periods from label
        cleanLabel = classLabel.replace(' ','').replace(',','').replace('.','')

        ### SPECIAL CHARS ###
        if '&' in cleanLabel:
            cleanLabel = cleanLabel.replace('&','&amp;')

        cleanLabel = cleanLabel.replace("'",'')
        cleanLabel = cleanLabel.replace('"','')
        cleanLabel = cleanLabel.replace('/','')
        cleanLabel = cleanLabel.replace('\\','')

        if '????' in cleanLabel:
            cleanLabel = cleanLabel.replace('????','unnamedConcept')

        ## assign namespace
        if ':' in cleanLabel:
            cleanLabel = cleanLabel[cleanLabel.find(':')+1:]
            if 'spase' in cleanLabel:
                namespace = 'https://spase-group.org/data/model/'
            elif 'genelab' in cleanLabel:
                namespace = 'https://genelab.nasa.gov/schema/'
            elif 'lsda' in cleanLabel:
                namespace = 'https://lsda.jsc.nasa.gov/schema/'


#         xml += '<owl:Class rdf:about="'+namespace+URIs[classLabel]+'">'
        xml += '<owl:Class rdf:about="'+namespace+classLabel+'">'
        xml += '<rdfs:label xml:lang="en-US">'+cleanLabel+'</rdfs:label>'


        if len(classes[classLabel])>0:

            for propRel in classes[classLabel]:

                propLabel = propRel[0]

                objectLabel = propRel[1]

#                 xml += '<sddo:'+URIs[propLabel]+' rdf:resource="'+namespace+URIs[objectLabel]+'"/>'
                xml += '<sddo:'+propLabel+' rdf:resource="'+namespace+objectLabel+'"/>'

    
        ## owl-specific
        xml += '</owl:Class>'
#         xml += '</rdf:Description>'

    for prop in properties:

        cleanProp = prop

        ### NO SPACES IN PROP NAME ###
        if cleanProp == 'is a' or cleanProp == 'is-a':
            cleanProp = 'isA'

    #     xml += '<rdf:Description rdf:about="'+namespace+prop+'"><rdfs:label xml:lang="en-US">'+prop+'</rdfs:label>'

        ## owl-specific    
#         xml += '<owl:AnnotationProperty rdf:about="'+namespace+URIs[prop]+'">'
        xml += '<owl:AnnotationProperty rdf:about="'+namespace+prop+'">'
        xml += '<rdfs:label xml:lang="en-US">'+cleanProp+'</rdfs:label>'

        ## owl-specific
        xml += '</owl:AnnotationProperty>'        
    #     xml += '</rdf:Description>'

    xml += "</rdf:RDF>"