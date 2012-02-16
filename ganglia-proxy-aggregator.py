#!/usr/bin/python

# ganglia_hack.py (c) 12.apr.2006 Antti.Vanne@iki.fi
# extended by Nathan Bijnens <nathan@nathan.gs>
# Description:
# Quick hack to use ganglia in a cluster with a non-multicasting
# switch. Doesn't scale too well, usable on a 24 cluster though.
# Idea: listen to port _serverPort (8666 as default) for gmetad's
# request for XML data and when connected, gather XML from
# individual nodes from port _gmondport and serve it to gmetad.

# Originally a perl script now rewritten in Python

import sre
import SocketServer
import socket
import argparse

class queryGmond:
  """Query individual nodes for gmond data and optionally gmond header"""
  def __init__(self, nodeip, gmondport, queryHeader = False):
    self.nodeip = nodeip
    self.nodedata = ""
    self.gmondport = gmondport
    self.queryHeader = queryHeader
    self.header = ""
    self.datapat = sre.compile("<HOST NAME=\"[\w\.]+\" IP=\"%s\".*?</HOST>" % self.nodeip, sre.DOTALL)
    self.headerpat = sre.compile("<\?xml version.*?<CLUSTER NAME=.*?>", sre.DOTALL)

  def readData(self):
    bufsize = 100000
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((self.nodeip, self.gmondport))
    data = ""
    incoming = s.recv(bufsize)
    while (incoming != ""):
      data += incoming;
      incoming = s.recv(bufsize)
    s.close()
    return data


  def run(self):
    try:
      data = self.readData()
      # extract information concerning this node from the data
      self.nodedata = sre.findall(self.datapat, data)[0]
      if (self.queryHeader):
        # extract header
        self.header = sre.findall(self.headerpat, data)[0]

    except:
      print "Error fetching nodedata from node %s, port %d" % (self.nodeip, self.gmondport)

class reqHandler(SocketServer.StreamRequestHandler):
  """Handle serve requests: run all queryGmond objects"""
  
  def setup(self):
    self.qos = []
    with_header = true
    
    for host, port in self.nodes.iteritems():
      queryGmond(host, gmondport = port, queryHeader = with_header)
      with_header = False
      
    self.wfile = self.request.makefile("wb", 0)
  def handle(self):
    self.qos[0].run()
    #self.qos[0].join()
    self.wfile.write(self.qos[0].header)
    self.wfile.write(self.qos[0].nodedata)

    for qo in self.qos[1:]: # run and wait queries this is faster
      qo.run()
      #qo.join()
      self.wfile.write(qo.nodedata)

    self.wfile.write("</CLUSTER>\n</GANGLIA_XML>\n")
  def finish(self):
    self.wfile.flush()
    self.wfile.close()

class CliConfiguration:
  def __init__(self):
    
    argParser = argparse.ArgumentParser(description="Ganglia Proxy")
    argParser.add_argument('nodes', nargs='+', metavar='nodes', help="Specify the nodes.")
    argParser.add_argument('--server-port', dest='server-port', default=8666, type=int )
    argParser.add_argument('--default-port', dest='default-port', default=8649, type=int )
    
    args = argParser.parse_args()
    
    self.nodes = self._parse_nodes(args.nodes, args.default_port)
    self.server_port = args.server_port
    
  def _parse_nodes(self, nodes, default_port):
    nodes_with_ports = {}
    
    for node in nodes:
      host, port = node.split(':')
      if(len(port) > 0):
        nodes_with_ports[host] = port
      else:
        nodes_with_ports[host] = default_port
    
    return nodes_with_ports

  
  
configuration = CliConfiguration()
reqHandler.nodes = configuration.nodes

s = SocketServer.TCPServer( ("", configuration.server_port), reqHandler)
s.serve_forever()

