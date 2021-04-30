import Pyro4
import sys
import codecs

f_u = open('uri.txt')
uri = f_u.read()
uri = uri.replace('\n','')
f_u.close()
Server = Pyro4.Proxy(uri)  # get a Pyro proxy to the greeting object

site = input('enter site') 

lis = [1,2,3,4]
action = int(input("choose action to perform- 1: enter nodes on new site \n 2: add more nodes to an existing site \n 3: Route a node \n 4: get routing table items \n"))
if action not in lis:
    print("enter number btw 1-4 only")
if action == 1:  #nodes on new site
    numNodes = input('enter number of nodes to enter ')
    nodes = []
    for i in range(len(numNodes)):
        nodeid = codecs.decode(input('enter node id '), 'unicode_escape')
        nodeid = nodeid*16
        ip = input('enter ip ')
        port = int(input('enter port '))
        node = [nodeid, ip, port]
        nodes.append(node)

    Server.add_nodes(site,nodes)
    print("added nodes: ",nodes)
    print("routing table elements \n")
    lis = Server.get_routing_table_items()
    print(lis)

if action == 2: # add more nodes to an existing site
    numNodes = input('enter number of nodes to enter ')
    nodes = []
    for i in range(len(numNodes)):
        nodeid = codecs.decode(input('enter node id '), 'unicode_escape')
        nodeid = nodeid*16
        ip = input('enter ip ')
        port = int(input('enter port '))
        node = [nodeid, ip, port]
        nodes.append(node)

    Server.update_nodes(nodes)
    print("added nodes:",nodes)
    print("routing table elements \n")
    lis = Server.get_routing_table_items()
    print(lis)
    
if action == 3:  # route node
    nodeid = codecs.decode(input('enter node id '), 'unicode_escape')
    nodeid = nodeid*16
    Server.route_node(nodeid)

if action == 4:  # get routing table items
    lis = Server.get_routing_table_items()
    print(lis)


# find the next hop; key does not need to be exact
# key_lis = ['\x01'*15, '\x00']  # key is addition of items in key
# Server.find_nextHop(key_lis)


       
    



