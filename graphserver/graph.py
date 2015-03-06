"""Web graph model based on interpretation of GraphViz dot file

Simeon Warner, 2015-03-06
"""
import logging
import os.path
import pydot
import re

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
        conneg_default = True #first conneg edge will be default
        for e in self.g.get_edges():
            src = self.add_node(e.get_source())
            dst_name = self.add_node(e.get_destination()).name
            label = self.normalize_label(e.get_label())
            m = re.match( r'conneg(\s+(\d+))?(\s+(\S+))?', label )
            if (m):
                if (m.group(4) is None):
                    self.log.info("Bad conneg label: %s" % (label))
                else:
                    code = int(m.group(2))
                    content_type = m.group(4)
                    self.log.info("%s conneg %s, %d -> %s" % (src.name, content_type, code, dst_name))
                    src.conneg[content_type] = [code,dst_name,conneg_default]
                    conneg_default = False
            elif (re.match('html\s+link',label,re.I)):
                src.html_links.append(dst_name)
            elif (re.match('html\s+img',label,re.I)):
                src.html_imgs.append(dst_name)
            else:
                # assume space separated set of links (last word might me mime type)
                words = label.split()
                mime_type = None
                if (re.match(r'\w+/\w+$',words[-1])):
                    mime_type = words.pop()
                for rel in words:
                    self.log.info("%s rel=\"%s\" %s %s" % (src.name,rel,dst_name,mime_type))
                    src.links.append([rel,dst_name,mime_type])

            # Do we have an svg file for this graph?
            svg_file = os.path.splitext(file)[0] + '.svg'
            if (os.path.exists(svg_file)):
                self.svg=svg_file

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

    def __str__(self):
        return self.g.to_string()
