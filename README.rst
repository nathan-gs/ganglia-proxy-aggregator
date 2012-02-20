Ganglia: a proxy & aggregator
#############################

Usage::
    
    ./ganglia-proxy-aggregator.py node01:8649 node02 nodeN:8649
    
Advanced usages

- Override the cluster name::
        
        ./ganglia-proxy-aggregator.py --cluster-name="TestCluster" node01:8649 node02 nodeN:8649
        
- On what port should the proxy listen to.::
        
        ./ganglia-proxy-aggregator.py --server-port=8649 node01:8649 node02 nodeN:8649
    
The options can be mixed.


Dependencies
~~~~~~~~~~~~

- Python >2.6
- libxml2 Python bindings.
    
Credits
~~~~~~~

Fork of ganglia-multicast-hack, found on http://code.google.com/p/ganglia-multicast-hack/

- Antti Vanne <antti.vanne@iki.fi>
- Nathan Bijnens <nathan@nathan.gs>

License
~~~~~~~

Distributed under a New BSD LICENSE, see LICENSE for details.