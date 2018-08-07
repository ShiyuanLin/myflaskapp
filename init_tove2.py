import logging
import rdflib
from rdflib.namespace import RDF, OWL, RDFS
from rdflib import Literal, BNode, URIRef, Graph, Namespace

import DateTimeDescription
import ctime


def main():
    print('Starting main')

    logging.basicConfig(filename='myapp.log', level=logging.INFO)
    logging.info(' ctime Started')

    # load the W3 standard time ontology
    g = Graph()
    g.parse("http://www.w3.org/2006/time")
    time = rdflib.Namespace(
        'http://www.w3.org/2006/time#')  # specify the time namespace

    # load the temporal constraint satisfaction extensions to the time ontology
    g.parse("http://ontology.eil.utoronto.ca/TOVE2/ctime.rdf")
    cot = rdflib.Namespace(
        'http://ontology.eil.utoronto.ca/TOVE2/ctime.rdf#')  # specify the time namespace

    # load test instances
    test = rdflib.Namespace('http://ontology.eil.utoronto.ca/TOVE2/test.owl#')
    g.parse('http://ontology.eil.utoronto.ca/TOVE2/test.ttl#', format="turtle")

    logging.info('ctime Finished')

    print('Ending main')


# if __name__ == '__main__':

logging.basicConfig(filename='ctime.log', filemode='w',
                    format='%(levelname)s %(asctime)s: %(message)s',
                    level=logging.INFO)

main()

