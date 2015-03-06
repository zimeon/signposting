#!/usr/bin/env python
"""
graphserver: HTTPD server to simulate a set of resources 
described in a GrapgViz .dot digraph.

Simeon Warner, 2015
"""

import glob
import logging
import optparse
import os.path
import re
import sys
import BaseHTTPServer
from graphserver.http_server import GSHTTPRequestHandler
from graphserver.graph import Graph
from graphserver.html_wrapper import HtmlWrapper

DEFAULT_PORT = 9876

def main():

    if (sys.version_info < (2,6)):
        sys.exit("This program requires python version 2.6 or later")

    # Options and arguments
    p = optparse.OptionParser(description='graphserver webserver which will run on http://localhost:%d/ unless another port is specified (-p).'%(DEFAULT_PORT),
                              usage='usage: %prog [options] [directory] (-h for help)')
    p.add_option('--port', '-p', action='store', type=int, default=DEFAULT_PORT,
                 help='port to run server on (default %default)')
    p.add_option('--verbose', '-v', action='store_true',
                 help='verbose output')

    (args, dirs) = p.parse_args()

    level = logging.INFO if args.verbose else logging.WARN
    logging.basicConfig(level=level)

    # Use either current directory or one specified as base_dir
    base_dir = os.getcwd()
    if (len(dirs)==1):
        base_dir = dirs[0]
    elif (len(dirs)>1):
        sys.exit("Supports only one base directory as argument (-h for help)")

    # Read graphs
    graphs = {}
    for dot_file in (glob.glob("%s/*.dot" % base_dir)):
        print "Loading %s..." % (dot_file) 
        g = Graph()
        g.parse(dot_file)
        if (g.name in graphs):
                raise Exception("Duplicate graph name %s in file %s" % (g.name,dot_file))
        graphs[g.name]=g

    # Run server
    run(GSHTTPRequestHandler, BaseHTTPServer.HTTPServer, port=args.port, graphs=graphs)

def run(HandlerClass, ServerClass, port, graphs):
    protocol='HTTP/1.1'
    server_address = ('localhost', port)
    HandlerClass.protocol_version = protocol
    HandlerClass.graphs = graphs
    HandlerClass.base_uri = "http://%s:%d" % server_address
    httpd = ServerClass(server_address, HandlerClass)
    sa = httpd.socket.getsockname()
    print "Serving HTTP on %s port %d..." % sa
    httpd.serve_forever()

if __name__ == '__main__':
    main()
