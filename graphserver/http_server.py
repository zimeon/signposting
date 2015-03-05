"""HTTP Server for GS

This module builds on SimpleHTTPServer to add resources for 
the graph patterns requested.
"""

__all__ = ["SimpleHTTPRequestHandler"]

import os
import posixpath
import SimpleHTTPServer
import urllib
import urlparse
import cgi
import re
import sys
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

class NotFound(Exception):
    pass

class GSHTTPRequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):

    """Simple HTTP request handler with GET and HEAD commands.

    This serves files from the current directory and any of its
    subdirectories.  The MIME type for files is determined by
    calling the .guess_type() method.

    The GET and HEAD requests are identical except that the HEAD
    request omits the actual contents of the file.

    """

    # Class variables used for a number of configurations used each
    # time this handler is instantiated
    server_version = "SimpleHTTP+graphserver/0.000...1"
    #protocol_version ... HTTP protocol, no need to override
    #graphs ... set of graphs to support

    def do_GET(self, include_content=True):
        """Serve a GET request (or HEAD by truncating)
        
        The HEAD response is identical to GET except that no
        content is sent, could be optimized.
        """
        # Defaults to build response
        self.code=200
        self.headers=[]
        self.content=''
        try:
            self.set_headers_content(self.path)
        except NotFound as e:
            self.send_error(404)
            return
        except Exception as e:
            self.send_error(500, "SERVER ERROR: " + str(e))
            return        
        # Have content, send HEAD or full GET
        self.send_response(200)
        self.send_head(self.headers,len(self.content))
        if (include_content):
            self.wfile.write(self.content)

    def do_HEAD(self):
        """Serve a HEAD request

        All this does is call do_GET with include_content=False to do
        everything except actually sending the content
        """
        self.do_GET(include_content=False)

    def set_headers_content(self,path):
        """Path may be either index or a defined resource

        Paths supported have the forms:
           /                index
           /graph/resource  resource withing graph

        Either returns content for the page or raises and exception.
        """
        # abandon query and fragment parameters
        path = path.split('?',1)[0]
        path = path.split('#',1)[0]
        path = posixpath.normpath(urllib.unquote(path))
        words = path.split('/')[1:] # discard first word as empty
        # Top-level index page?
        if (path == '/'):
            self.index_page()
        # Known resource in graph?
        elif (len(words)==2 and
            words[0] in self.graphs and
            words[1] in self.graphs[words[0]].nodes):
            self.build_node(self.graphs[words[0]].nodes[words[1]])
        else:
            raise NotFound

    def send_head(self,headers,length):
        """Common code for GET and HEAD commands.

        This sends the response code and MIME headers.
        """
        for header in headers:
            (name,value) = header
            self.send_header(name, value)
        self.send_header("Content-Length", length)
        #self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
        self.end_headers()

    def index_page(self):
        """Sets content for top-level index page
        """
        content = '<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">\n'
        content += "<html>\n<head>\n"
        content += "<title>Signposting test server</title>\n"
        #'<link rel="stylesheet" href="/css/graphserver.css">\n</head<\n>')
        content += "<body>\n<h1>Signposting test server</h1>\n\n"
        for graph_name in self.graphs:
            egn = cgi.escape(graph_name)
            content += "<h3>Graph: %s</h3>\n\n<ul>\n" % (egn)
            for node_name in self.graphs[graph_name].nodes:
                n = self.graphs[graph_name].nodes[node_name]
                enn = cgi.escape(n.name)
                content += "<li><a href=\"/%s/%s\">%s</a></li>\n" % (egn,enn,enn)
            content += "</ul>\n\n"
        content += "</body>\n</html>\n"
        self.content = content

    def build_node(self, node):
        """Set code, headers and content for resource
        """
        dump="name: %s\n" % node.name
        dump+="mime_type: %s\n" % str(node.mime_type)
        dump+="conneg: %s\n" % str(node.conneg)
        dump+="links: %s\n" % str(node.links)
        if (node.mime_type == 'text/html'):
            self.content="<html>\n<head>\n<title>%s</title>\n</head>\n" % (node.name)
            self.content="<body><h1>%s</h1>\n<pre>%s</pre></body></html>\n" % (node.name,dump)
        else: #assume text/plain
            self.content=dump
        for rel in node.links:
            uri = self.full_uri(node.links[rel])
            self.headers.append(['Link','<%s>; rel="%s"' % (uri,rel)])

    def full_uri(self, relative_uri):
        # FIXME - get host and port from object state
        return urlparse.urljoin('http://localhost:9999'+self.path, relative_uri)

