#-------------------------------------------------------------------------------
# Name:        Meaningful Spatio-temporal Analytics
# Purpose:
#
# Author:      Simon Scheider
#
# Created:     17/11/2016
# Copyright:   (c) simon 2016
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import os
import re
import sys
from sys import argv
import rdflib
import RDFClosure
from rdflib.namespace import RDFS, RDF
import glob

def file_to_str(fn):
    """
    Loads the content of a text file into a string
    @return a string
    """
    with open(fn, 'r') as f:
        content=f.read()
    return content

def n_triples( g, n=None ):
    """ Prints the number of triples in graph g """
    if n is None:
        print( '  Triples: '+str(len(g)) )
    else:
        print( '  Triples: +'+str(len(g)-n) )
    return len(g)


def run_inferences( g ):
    print('run_inferences')
    # expand deductive closure
    #RDFClosure.DeductiveClosure(RDFClosure.RDFS_Semantics).expand(g)
    RDFClosure.DeductiveClosure(RDFClosure.OWLRL_Semantics).expand(g)
    n_triples(g)
    return g

def load_ontologies( g ):
    print("load_ontologies")
    ontos = ["ontologies/Workflow.rdf","ontologies/GISConcepts.rdf","ontologies/AnalysisData.rdf"]
    for fn in ontos:
        print("  Load RDF file: "+fn)
        g.parse( fn )
    n_triples(g)
    return g

def graph_to_file( g, output_filepath = None ):
    """ Serializes graph g to an XML/RDF file """
    if not output_filepath:
        _outfn = 'output/workflows_output.rdf'
    else: _outfn = output_filepath
    g.serialize( _outfn )
    print("Written "+str(len(g))+" triples to " + _outfn)

def prefixURI(str):
    """Prefixes URI strings"""
    pref = {}
    namere = r"\s[a-z]+:"
    urire = r":\s+<\S+>"
    pre = file_to_str('rdf_prefixes.txt')
    for l in pre.split('\n'):
        uri= ''
        ns = ''
        for m in re.findall(urire,l):
            uri = m[3:-1]
            break
        for m in re.findall(namere,l):
            ns = m[1:]
            break
        pref[uri] = ns
    #print pref.keys()
    for k in pref.keys():
        str = str.replace(k, pref[k])
        #print str
    return str

def loadData(g ):
    file = 'data/mauptest.ttl'
    wf = rdflib.Graph()
    gd = wf.parse(file, format='n3') +g
    print "data loaded"
    return gd

def runQuery( g ):
    file = 'questions/maupquery.rq'
    res = g.query(file_to_str('rdf_prefixes.txt') +'\n'+ file_to_str(file))
    print(80*"-")
    print('OUTPUT:\n')
    for i in res:
        line = ''
        for j in i:
            line += ((prefixURI(j)) if (j!=None) else 'None')+' '
        print(line)

def runConsQuery( g ):
     queries = glob.glob('questions/maupconsquery*.rq')
     for q in (queries):
        res = g.query(file_to_str('rdf_prefixes.txt') +'\n'+ file_to_str(q))
        gwf = rdflib.Graph()
        for i in res:
            gwf.add(i)
        print "constructed triples :"+str(len(gwf))
        for s, p, o in gwf.triples((None, None, None)):
            print (prefixURI(s)) if (s!=None) else 'None',(prefixURI(p)) if (p!=None) else 'None',(prefixURI(o)) if (o!=None) else 'None'
        g = gwf + g
     return g



def main():
    g = rdflib.ConjunctiveGraph()
    g = loadData ( g )
    n_triples(g)
    #g = load_ontologies( g )
    g = runConsQuery( g )
    n_triples(g)

if __name__ == '__main__':
    main()

