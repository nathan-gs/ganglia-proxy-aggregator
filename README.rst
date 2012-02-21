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

Running as a daemon
~~~~~~~~~~~~~~~~~~~

It uses the upstart system of Ubuntu.

Create a ganglia-pa user.

Copy following files::
    
    ganglia-proxy-aggregator.default -> /etc/default/ganglia-proxy-aggregator
    ganglia-proxy-aggregator.init -> /etc/init.d/ganglia-proxy-aggregator
    ganglia-proxy-aggregator.py -> /usr/bin/ganglia-proxy-aggregator.py

Dependencies
~~~~~~~~~~~~

- Python >2.6
    
Credits
~~~~~~~

Fork of ganglia-multicast-hack, found on http://code.google.com/p/ganglia-multicast-hack/

replaced the regex with xml dom parsing & added cli arguments.

- Antti Vanne <antti.vanne@iki.fi>
- Nathan Bijnens <nathan@nathan.gs>

License
~~~~~~~

Distributed under a New BSD LICENSE, see LICENSE for details.