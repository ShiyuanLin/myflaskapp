import logging
import rdflib 
from rdflib.namespace import RDF, OWL, RDFS
from rdflib import Literal, BNode, URIRef, Graph, Namespace

import DateTimeDescription
import ctime
	
logging.basicConfig(filename='myapp.log', level=logging.INFO)
    
# load the W3 standard time ontology
# g = Graph(store = 'Sleepycat', identifier='ctime')
# g.open('ctimeStore', create = True)

g=Graph()

g.parse("http://www.w3.org/2006/time")
time = rdflib.Namespace('http://www.w3.org/2006/time#')	# specify the time namespace

# load the temporal constraint satisfaction extensions to the time ontology
g.parse("http://ontology.eil.utoronto.ca/TOVE2/ctime.rdf")
cot = rdflib.Namespace('http://ontology.eil.utoronto.ca/TOVE2/ctime.rdf#')	# specify the time namespace

# load test instances
test = rdflib.Namespace('http://ontology.eil.utoronto.ca/TOVE2/test.owl#')
g.parse('http://ontology.eil.utoronto.ca/TOVE2/test.ttl#', format="turtle")

tmin = DateTimeDescription.DateTimeDescription(g, test.cins1emin_Instant)

# g.close()