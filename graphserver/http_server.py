"""HTTP Server for GS

This module builds on SimpleHTTPServer to add resources for 
the graph patterns requested.
"""

__all__ = ["SimpleHTTPRequestHandler"]

from negotiator import ContentNegotiator, AcceptParameters, ContentType, Language
import os
import posixpath
import SimpleHTTPServer
import urllib
import urlparse
import cgi
import re

class NotFound(Exception):
    pass

class GSHTTPRequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):

    """Simple HTTP request handler to simulate graphs

    Implements HTTP GET and HEAD commands.
    """

    # Class variables used for a number of configurations used each
    # time this handler is instantiated
    server_version = "SimpleHTTP+graphserver/0.000...1"
    base_uri = "http://unknown_base_uri/"
    #protocol_version ... HTTP protocol, no need to override
    #graphs ... set of graphs to support

    def do_GET(self, include_content=True):
        """Serve a GET request (or HEAD by truncating)
        
        The HEAD response is identical to GET except that no
        content is sent, could be optimized.
        """
        # Defaults to build response
        self.code=200
        self.response_headers=[]
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
        self.send_response(self.code)
        self.send_head(self.response_headers,len(self.content))
        if (include_content and self.content):
            self.wfile.write(self.content)

    def do_HEAD(self):
        """Serve a HEAD request

        All this does is call do_GET with include_content=False to do
        everything except actually sending the content
        """
        self.do_GET(include_content=False)

    def do_conneg(self,node):
        """Specify the default parameters. These are the parameters which will be used in place of any HTTP Accept headers which are not present in the negotiation request. For example, if the Accept-Language header is not passed to the negotiator it will assume that the client request is for "en"
        """
        # Configure conneg and work out default from node config
        acceptable=[]
        default_content_type=None
        for content_type in node.conneg:
            (code,dst,default) = node.conneg[content_type]
            self.log_message("conneg: config %s (%d,%s,%s)" % (content_type,code,dst,default))
            acceptable.append(AcceptParameters(ContentType(content_type)))
            if (default):
                default_content_type=content_type
        # If there was no default, pick the last one we saw
        if (not default_content_type):
            default_content_type=content_type
        # Do we have an Accept header in the request? If not then default
        if ('Accept' not in self.headers):
            return(default_content_type)
        # else conneg...
        default_params = AcceptParameters(ContentType(default_content_type))
        cn = ContentNegotiator(default_params, acceptable)
        accept = self.headers["Accept"]
        self.log_message("conneg: request Accept: %s" % (accept))
        selected = cn.negotiate(accept)
        #self.log_message("conneg: match %s" % (str(selected)))
        if (selected is not None and
            str(selected.content_type) in node.conneg):
            self.log_message("conneg: selected %s" % (selected.content_type))
            (code,dst,default) = node.conneg[str(selected.content_type)]
        else:
            self.log_message("conneg: defaulting to %s" % (default_content_type))
            (code,dst,default) = node.conneg[default_content_type]
        self.code = code
        self.response_headers.append(['Location',self.full_uri(dst)])
        self.log_message("conneg: %d redirect to %s" % (code,dst))

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
        elif (len(words)==1 and
            words[0] in self.graphs):
            self.graph_index_page(self.graphs[words[0]])
        # CSS?
        elif (path == '/css/graphserver.css'):
            self.read_file('.'+path)
        # Known graph?
        elif (len(words)==2 and
              words[0] in self.graphs):
            graph = self.graphs[words[0]]
            # Known resource in graph? or SVG image?
            if (words[1] in self.graphs[words[0]].nodes):
                self.build_node(graph, graph.nodes[words[1]])
            elif (words[1]=='svg'):
                self.read_and_link_svg(graph.svg, graph)
        else:
            raise NotFound

    def send_head(self,headers,length=None):
        """Common code for GET and HEAD commands.

        This sends the HTTP headers and adds a Content-Length header based
        on length.
        """
        for header in headers:
            (name,value) = header
            self.send_header(name, value)
        if (length is not None):
            self.send_header("Content-Length", length)
        self.send_header("Last-Modified", self.date_time_string())
        self.end_headers()

    def index_page(self):
        """Sets content for top-level index page
        """
        content = "<html>\n<head>\n"
        content += "<title>Signposting test server</title>\n"
        content += '<link rel="stylesheet" href="/css/graphserver.css">\n</head>\n'
        content += "<body>\n<h1>Signposting test server</h1>\n\n"
        for graph_name in self.graphs:
            graph = self.graphs[graph_name]
            egn = cgi.escape(graph_name)
            content += '<h3><a href="/%s/">Scenario: %s</a></h3>\n\n' % (egn,egn)
            if (graph.svg):
                content += "<a href=\"/%s/svg\"/>svg</a>\n" % (egn)
            content += '<ul>\n'
            for node_name in sorted(graph.nodes):
                n = graph.nodes[node_name]
                enn = cgi.escape(n.name)
                content += "<li><a href=\"/%s/%s\">%s</a></li>\n" % (egn,enn,enn)
            content += "</ul>\n\n"
        content += "</body>\n</html>\n"
        self.content = content

    def graph_index_page(self, graph):
        """Sets content for top-level index page
        """
        content = "<html>\n<head>\n"
        content += "<title>Signposting test server - %s</title>\n" % (graph.name)
        content += '<link rel="stylesheet" href="/css/graphserver.css">\n</head>\n'
        egn = cgi.escape(graph.name)
        content += '<body>\n<h1>Scenario: %s</h1>\n\n' % (egn)
        if (graph.svg):
            content += '<object style="font-size: 50%%;" type="image/svg+xml" data="/%s/svg">Your browser does not support SVG</object>\n' % (graph.name)
        content += '<ul>\n'
        for node_name in sorted(graph.nodes):
            n = graph.nodes[node_name]
            enn = cgi.escape(n.name)
            content += "<li><a href=\"/%s/%s\">%s</a></li>\n" % (egn,enn,enn)
        content += "</ul>\n\n"
        content += "</body>\n</html>\n"
        self.content = content

    def build_node(self, graph, node):
        """Set code, headers and content for resource
        """
        dump = self.node_info(node)
        if (node.mime_type):
            self.response_headers.append(['Content-Type',node.mime_type])
        # Is this a node that supports conneg?
        if (node.conneg):
            self.do_conneg(node)
        if (node.mime_type == 'text/html'):
            self.content="<html>\n<head>\n<title>%s</title>\n" % (node.name)
            self.content+='<link rel="stylesheet" href="/css/graphserver.css">\n</head>\n'
            self.content+=self.node_html_linktags(node)
            self.content+="<body>\n<h1>%s</h1>\n" % (node.name)
            self.content+=self.node_html_links_imgs(node)
            self.content+="<pre>\n"
            self.content+=self.node_info(node)
            self.content+="</pre>\n"
            # Any fragments to deal with?
            for name2 in graph.nodes:
                m = re.match(node.name+"#(.+)",name2)
                if (m):
                    frag = m.group(1)
                    frag_node = graph.nodes[name2]
                    self.content+="<h2><a id=\"%s\">Fragment #%s</a></h2>\n" % (frag,frag)
                    self.content+=self.node_html_links_imgs(frag_node)
                    self.content+="<pre>\n"
                    self.content+=self.node_info(frag_node)
                    self.content+="</pre>\n"
                    self.content+=self.check_frag_against_parent(frag_node, node)
            self.content+="</body></html>\n"
        elif (node.mime_type=='image/png'):
            self.read_file('examples/png.png')
        elif (node.mime_type=='application/pdf'):
            self.read_file('examples/pdf.pdf')
        elif (node.mime_type=='text/turtle'):
            self.build_turtle(node)
        else: #assume text/plain
            self.content=self.node_info(node)
        for link in node.links:
            (rel,dst,mime_type)=link
            uri = self.full_uri(dst)
            mime_type_str = ('; type="%s"' % (mime_type)) if (mime_type) else ''
            self.response_headers.append(['Link','<%s>; rel="%s"%s' % (uri,rel,mime_type_str)])

    def node_info(self, node):
        """Return preformatted node information string"""
        info =  "name: %s\n" % node.name
        info += "mime_type: %s\n" % str(node.mime_type)
        info += "conneg: %s\n" % str(node.conneg)
        info += "links: %s\n" % str(node.links)
        if (node.mime_type=="text/html"):
            info += "html_linktags: %s\n" % str(node.html_linktags)
            info += "html_links: %s\n" % str(node.html_links)
            info += "html_imgs: %s\n" % str(node.html_imgs)
        return(info)

    def node_html_links_imgs(self, node):
        """Return HTML for included links and imgs"""
        return( self.node_html_links(node) + self.node_html_imgs(node) )

    def node_html_imgs(self, node):
        """Return HTML <ul> list of img links for this node"""
        html = ''
        for img in node.html_imgs:
             html += "<li><a href=\"%s\">%s</a></li>\n" % (img,img)
        if (html):
            return("<p>Images included:</p>\n<ul>\n"+html+"</ul>\n")
        else:
            return("")        

    def node_html_linktags(self, node):
        """Return HTML <meta> elements as string for this node"""
        html = ''
        for (rel,dst_name,mime_type) in node.html_linktags:
            mime_str = '' if (mime_type is None) else ' type="%s"' % mime_type
            html += '<link rel="%s" href="%s"%s/>\n' % (rel,dst_name,mime_str)
        return(html)

    def node_html_links(self, node):
        """Return HTML <ul> list of HTML links for this node"""
        html = ''
        for dst in node.html_links:
             html += "<li><a href=\"%s\">%s</a></li>\n" % (dst,dst)
        if (html):
            return("<p>Links to:</p>\n<ul>\n"+html+"</ul>\n")
        else:
            return("")

    def check_frag_against_parent(self, frag_node, parent_node):
        """Check to see whether frag node is compatible with parent

        Returns HTML warnings if note, blank if OK
        """
        warnings = []
        # mime_types should be the same
        if (frag_node.mime_type != parent_node.mime_type):
            warnings.append("MIME type mismatch: %s vs %s" %
                            (frag_node.mime_type, parent_node.mime_type))
        # links should be the same
        links = {}
        for l in frag_node.links:
            links[str(l)]='fragment'
        for l in parent_node.links:
            s=str(l)
            if (s in links):
                links.delete(s);
            else:
                links[s]='parent'
        for s in sorted(links):
            warnings.append("Link %s specified only in %s" % (s,links[s]))
        if (warnings):
            return "<p class=\"error\">WARNINGS:<br/>" + "<br/>\n".join(warnings) + "</p>\n"
        else:
            return ""

    def read_and_link_svg(self, file, graph):
        """ Read SVG and mark up all nodes as links to resources in graph

        This is a svg-scrape fudge and relies upon the formatting of the
        svg output from dot. Likely fragile... but expedient ;-)
        """
        try:
            f = open(file,'r')
        except Exception as e:
            self.log_message("read_and_link_svg: Failed: %s" % (str(e)))
            raise NotFound
        self.content = ""
        in_link = False 
        for line in f:
            m = re.match(r'<!-- ([^-]+) -->', line)
            if (m):
                if (in_link):
                    in_link = False
                    self.content += "</a>\n"
                name = m.group(1)
                name = re.sub(r'(\\n|\s+)', '_', name) #normalize
                if (name in graph.nodes):
                    in_link = True
                    line += '<a xlink:href="/%s/%s">\n' % (graph.name, name)
            self.content += line
        f.close()

    def read_file(self, file):
        """Read specified into self.content

        Depending on how much ends up being dynamically generated vs read in,
        should perhaps pass file ptr to output routine instead, per standard
        SimpleHTTPServer.
        """
        try:
            f = open(file,'r')
            self.content = f.read()
            f.close()
        except Exception as e:
            self.log_message("read_file: Failed: %s" % (str(e)))
            raise NotFound       

    def build_turtle(self, node):
        """Make a turtle description of this node in self.content

        Just a dummy version of the node info for amusement
        """
        turtle =  "@prefix dc: <http://purl.org/dc/elements/1.1/> .\n"
        turtle += "@prefix x: <http://example.org/terms/> .\n\n"
        turtle += '[ dc:title    "%s" ;\n' % node.name
        turtle += '  x:mime_type "%s" ;\n' % str(node.mime_type)
        turtle += '  x:conneg    "%s" ;\n' % str(node.conneg)
        turtle += '  x:links     "%s" ;\n' % str(node.links)
        turtle += "] .\n"
        self.content = turtle

    def full_uri(self, relative_uri):
        """Return full URI for relative_uri based on current request context"""
        return urlparse.urljoin(self.base_uri+self.path, relative_uri)

