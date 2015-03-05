"""Graph model based on interpretation of GraphViz dot file
"""
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
        self.links = {}

"""A node-oriented view of a GraphViz graph for modeling web resources

Each node corresponds to a web resource and we accumulate the properties
of each node from the data in the pydot.Graph.
"""
class Graph(object):

    def __init__(self, g=None, name=None, nodes=None):
        self.g = g
        self.name = name
        self.nodes = nodes if (nodes is not None) else {}

    def parse(self, file):
        self.g = pydot.graph_from_dot_file(file)

        self.name = self.g.get_name()
        print "GRAPH NAME %s..." % (self.name)

        # Pick out all nodes and populate local nodes dict. The model
        # from pydot.Graph includes only explicitly mentioned nodes
        # in get_nodes(), others must be extracted from get_edges()
        #
        print "nodes:"
        for n in self.g.get_nodes():
            node = self.add_node(n.get_name())
            
        print "edges:"
        for e in self.g.get_edges():
            src = self.add_node(e.get_source())
            dst_name = self.add_node(e.get_destination()).name
            label = self.normalize_label(e.get_label())
            m = re.match( r'conneg(\s+(\d+))?(\s+(\S+))?', label )
            if (m):
                if (m.group(4) is None):
                    print "Bad conneg label: %s" % (label)
                else:
                    print "%s conneg %s, %s -> %s" % (src.name, m.group(4), m.group(2), dst_name)
                    src.conneg[m.group(4)]=[m.group(2),dst_name]
            else:
                # assume space separated set of links
                for rel in label.split():
                    print "%s rel=\"%s\" %s" % (src.name,rel,dst_name)
                    src.links[rel]=dst_name

    def add_node(self, node_name):
        """Normalize name and add if not already present, return normalized name
        """
        node_name = self.normalize_name(node_name)
        if (node_name not in self.nodes):
            self.nodes[node_name] = Node(node_name)
            print "Added node %s" % (node_name)
            # A little fudging to infer type from name
            if (re.search('(HTML|Splash|Choice)', node_name, re.I)):
                self.nodes[node_name].mime_type = "text/html"
            elif (re.search('PDF', node_name, re.I)):
                self.nodes[node_name].mime_type = "application/pdf"
            elif (re.search('RDF', node_name, re.I)):
                self.nodes[node_name].mime_type = "text/turtle"
        else:
            print "Already have node %s" % (node_name)
        return(self.nodes[node_name])

    def normalize_name(self, name):
        """Normalize name in pydot data

        Remove quotes, convert space to underscore
        """
        name = re.sub( r'"', '', name )
        name = re.sub( r'\s+', '_', name )
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
