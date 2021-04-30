import Pyro4
from routing import Pastry

@Pyro4.expose
class Server(object):
    def __init__(self):
        self.pastry = None
        

    def add_nodes(self, site, nodes):
        peers = {}
        for node in nodes:
            nodeid, ip, port = node
            peers[bytes(nodeid, 'utf-8')] = (ip, port)
        self.pastry =  Pastry(bytes(site, 'utf-8'), peers = peers)

    def update_nodes(self, nodes):
        peers = {}
        for node in nodes:
            nodeid, ip, port = node
            peers[bytes(nodeid, 'utf-8')] = (ip, port)
        self.pastry.update(peers)
   
    def route_node(self,nodeid):
        self.pastry.route(bytes(nodeid, 'utf-8'))

    def get_routing_table_items(self):
        print(list(self.pastry.routing_table.items()))
        return list(self.pastry.routing_table.items())

daemon = Pyro4.Daemon()         # make a Pyro daemon
uri = daemon.register(Server)   # register the greeting maker as a Pyro object

f = open('uri.txt','w+')
print(uri,file=f)
f.close()

print("Ready. Object uri =", uri)      # print the uri so we can use it in the client later
daemon.requestLoop()                   # start the event loop of the server to wait for calls