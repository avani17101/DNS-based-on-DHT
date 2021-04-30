import Pyro4
import sys
import codecs

f_u = open('uri.txt')
uri = f_u.read()
uri = uri.replace('\n','')
f_u.close()
Server = Pyro4.Proxy(uri)  # get a Pyro proxy to the greeting object



lis = [1,2,3,4]
while True:
    action = int(input("choose action to perform- \n 1: enter nodes on new site \n 2: add more nodes to an existing site \n 3: Route a node \n 4: get routing table items \n"))
    if action not in lis:
        print("enter number btw 1-4 only")
    if action == 1:  #nodes on new site
        site = input('enter site ') 
        numNodes = int(input('enter number of nodes '))
        nodes = []
        for i in range(numNodes):
            nodeid = codecs.decode(input('enter node id ',i+1), 'unicode_escape')
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
        site = input('enter site ') 
        numNodes = input('enter number of nodes ')
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
        res = Server.route_node(nodeid)
        print(res)

    if action == 4:  # get routing table items
        lis = Server.get_routing_table_items()
        print(lis)

