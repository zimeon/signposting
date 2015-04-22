"""Web graph model based on interpretation of GraphViz dot file

Simeon Warner, 2015-03-06
"""
import logging
import os.path
import pydot
import re

class BadEdge(Exception):
    pass

"""A node that represents a web resource

Has a name (relative URI), possibly conneg rules
of mime type and redirect code, possibly Link headers. 
"""
class Node(object):

    def __init__(self, name=None):
        self.name = name
        self.mime_type = None
        self.conneg = {}
        self.links = []
        self.html_links = []
        self.html_linktags = []
        self.html_imgs = []

"""A node-oriented view of a GraphViz graph for modeling web resources

Each node corresponds to a web resource and we accumulate the properties
of each node from the data in the pydot.Graph.
"""
class Graph(object):

    def __init__(self, g=None, name=None, nodes=None):
        self.g = g
        self.name = name
        self.nodes = nodes if (nodes is not None) else {}
        self.svg = None
        self.log = logging.getLogger('graph')

    def parse(self, file):
        self.g = pydot.graph_from_dot_file(file)

        self.name = self.g.get_name()
        self.log.info("##### GRAPH NAME %s..." % (self.name))

        # Pick out all nodes and populate local nodes dict. The model
        # from pydot.Graph includes only explicitly mentioned nodes
        # in get_nodes(), others must be extracted from get_edges()
        #
        self.log.info("nodes:")
        for n in self.g.get_nodes():
            node = self.add_node(n.get_name())
            
        self.log.info("edges:")
        self.conneg_default = True #first conneg edge will be default
        for e in self.g.get_edges():
            try:
                self.parse_edge(e)
            except BadEdge as e:
                self.log.error("Bad edge: %s" % str(e))
        # Do we have an svg file for this graph?
        svg_file = os.path.splitext(file)[0] + '.svg'
        if (os.path.exists(svg_file)):
            self.svg=svg_file

    def parse_edge(self,e):
        src = self.add_node(e.get_source())
        dst_name = self.add_node(e.get_destination()).name
        label = self.normalize_label(e.get_label())
        words = label.split()
        if (len(words)<1):
            raise BadEdge("Must have at least 1 word: %s" % label)
        # If the first word is html or http then expect qualifier
        link_type = words.pop(0).lower()
        if (link_type=='html' or link_type=='http' and len(words)>0):
            link_type+=' '+words.pop(0).lower()
        # If we have just rel= then assume HTTP Link
        if (re.match(r'rel=',link_type)):
            words.insert(0,link_type)
            link_type='http link'
        # Now have type, rest depends on that
        if (link_type=='conneg'):
            if (len(words)!=2):
                raise BadEdge("Bad conneg label: %s" % (label))
            code = int(words[0])
            content_type = words[1]
            self.log.info("%s conneg %s, %d -> %s" % (src.name, content_type, code, dst_name))
            src.conneg[content_type] = [code,dst_name,self.conneg_default]
            self.conneg_default = False
        elif (link_type=='html link'):
            src.html_links.append(dst_name)
        elif (link_type=='html img'):
            src.html_imgs.append(dst_name)
        elif (link_type=='html linktag'):
            rel = self.normalize_rel(words[0])
            mime_type = words[1]
            self.log.info("%s HTML linktag rel=\"%s\" %s %s" % (src.name,rel,dst_name,mime_type))
            src.html_linktags.append([rel,dst_name,mime_type])
        elif (link_type=='http link'):
            mime_type = None
            if (len(words)==2):
                # second is MIME type
                mime_type = words.pop()
                if (not re.match(r'\w+/[\w\+]+$',mime_type)):
                    raise BadEdge("Bad MIME type '%s' in %s" % (mime_type,label))
            elif (len(words)!=1):
                raise BadEdge("Bad HTTP Link: %s" % (label))
            rel = self.normalize_rel(words[0])
            self.log.info("%s rel=\"%s\" %s %s" % (src.name,rel,dst_name,mime_type))
            src.links.append([rel,dst_name,mime_type])
        elif (len(words)>1):
            # assume space separated set of links (last word might me mime type)
            mime_type = None
            if (re.match(r'\w+/[\w\+]+$',words[-1])):
                mime_type = words.pop()
            for rel in words:
                rel = self.normalize_rel(rel)
                self.log.info("%s rel=\"%s\" %s %s" % (src.name,rel,dst_name,mime_type))
                src.links.append([rel,dst_name,mime_type])
        else:
            raise BadEdge("Unrecognized edge: %s" % label)

    def add_node(self, node_name):
        """Normalize name and add if not already present, return normalized name
        """
        node_name = self.normalize_name(node_name)
        if (node_name not in self.nodes):
            self.nodes[node_name] = Node(node_name)
            self.log.info(" Added node %s" % (node_name))
            # A little fudging to infer type from name
            if (re.search('(HTML|Splash|Choice)', node_name, re.I)):
                self.nodes[node_name].mime_type = "text/html"
            elif (re.search('PDF', node_name, re.I)):
                self.nodes[node_name].mime_type = "application/pdf"
            elif (re.search('RDF', node_name, re.I)):
                self.nodes[node_name].mime_type = "text/turtle"
            elif (re.search('IMG', node_name, re.I)):
                self.nodes[node_name].mime_type = "image/png"
        else:
            self.log.info(" Already have node %s" % (node_name))
        return(self.nodes[node_name])

    def normalize_name(self, name):
        """Normalize a node name in pydot data

        Remove quotes, convert spaces and newlines to underscore
        """
        name = re.sub( r'"', '', name )
        name = re.sub( r'(\s|\\n)+', '_', name )
        return(name)

    def normalize_label(self, name):
        """Normalize name in pydot data

        Remove quotes, convert return to space
        """
        name = re.sub( r'"', '', name )
        name = re.sub( r'\\n', ' ', name )
        return(name)

    def normalize_rel(self,rel):
        """Normalize relation

        Accept single relation or rel="relation" forms to return relation
        """
        rel = re.sub( r'"', '', rel )
        rel = re.sub( r'rel=', '', rel )
        return(rel)

    def __str__(self):
        return self.g.to_string()
