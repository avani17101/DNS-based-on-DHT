import Pyro4
import sys

f_u = open('uri.txt')
uri = f_u.read()
uri = uri.replace('\n','')
f_u.close()
Server = Pyro4.Proxy(uri)  # get a Pyro proxy to the greeting object

# infile  = sys.argv[1]
# outfile = sys.argv[2]
# f = open(infile)
# f2 = open(outfile,'w+')
# f2.close()

# add nodes
site = 'google.com'
nodeid1 = '\x01'*16
ip1 = '8.8.8.8'
port1 = 8080

node1 = [nodeid1, ip1, port1]
nodeid2 = '\x02'*16
ip2 = '8.8.4.4'
port2 = 5353
node2 = [nodeid2, ip2, port2]

Server.add_nodes(site,[node1, node2])


# Update node
site = 'facebook.com'
nodeid3 = '\x03'*16
ip2 = '10.20.20.2'
port = 8081
Server.update_nodes([[nodeid3, ip2, port]])


# route node
Server.route_node(nodeid3)

           
# get routing table items
lis = Server.get_routing_table_items()
print(lis)

# find the next hop; key does not need to be exact
# key_lis = ['\x01'*15, '\x00']  # key is addition of items in key
# Server.find_nextHop(key_lis)


       
    



