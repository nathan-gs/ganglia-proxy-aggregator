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

import SocketServer
import socket
import argparse
import libxml2

class queryGmond:
  """Query individual nodes for gmond data and optionally gmond header"""
  def __init__(self, nodeip, gmondport):
    self.nodeip = nodeip
    self.gmondport = gmondport

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
      return self.readData()
    except:
      print "Error fetching nodedata from node %s, port %d" % (self.nodeip, self.gmondport)

class reqHandler(SocketServer.StreamRequestHandler):
  """Handle serve requests: run all queryGmond objects"""
  
  def setup(self):
    self.qos = []
    
    for host, port in self.nodes.iteritems():
      self.qos.append(queryGmond(host, gmondport = port))
    
    self.wfile = self.request.makefile("wb", 0)
    
  def handle(self):
    doc = None
    cluster = None
    
    for qo in self.qos: # run and wait queries this is faster
      newdoc = libxml2.parseDoc(qo.run())
      newcluster = newdoc.getRootElement().children
      
      if newcluster:
        if not root:
          if self.cluster_name:
            newcluster.setProp("NAME",self.cluster_name)
          
          doc = newdoc
          cluster = newcluster
          
        else:
          cluster.addChildList(newcluster.children.copyNodeList())
          newdoc.freeDoc()
      
    self.wfile.write(doc)
    
  def finish(self):
    self.wfile.flush()
    self.wfile.close()

class CliConfiguration:
  def __init__(self):
    
    argParser = argparse.ArgumentParser(description="Ganglia Proxy")
    argParser.add_argument('nodes', nargs='+', metavar='nodes', help="Specify the nodes.")
    argParser.add_argument('--server-port', dest='server_port', default=8666, type=int )
    argParser.add_argument('--default-port', dest='default_port', default=8649, type=int )
    argParser.add_argument('--cluster-name', dest='cluster_name', default=None )
    
    args = argParser.parse_args()
    
    self.nodes = self._parse_nodes(args.nodes, args.default_port)
    self.server_port = args.server_port
    self.cluster_name = args.cluster_name
    
  def _parse_nodes(self, nodes, default_port):
    nodes_with_ports = {}
    
    for node in nodes:
      host, port = node.split(':')
      if(len(port) > 0):
        nodes_with_ports[host] = int(port)
      else:
        nodes_with_ports[host] = int(default_port)
    
    return nodes_with_ports

  
  
configuration = CliConfiguration()
reqHandler.nodes = configuration.nodes
reqHandler.cluster_name = configuration.cluster_name

s = SocketServer.TCPServer( ("", configuration.server_port), reqHandler)
s.serve_forever()

