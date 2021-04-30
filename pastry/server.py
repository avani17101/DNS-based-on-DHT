import Pyro4
from routing import Pastry
import json

@Pyro4.expose
class Server(object):
    def __init__(self, site, nodes):
        self.site = site
        self.peers = None
        # self.pastry = Pastry(bytes(site, 'utf-8'), peers = self.peers)
        self.pastry = None
        self.nodes = nodes
        
        
    def add_nodes(self, site, nodes):
        peers = {}
        for node in nodes:
            nodeid, ip, port = node
            peers[bytes(nodeid, 'utf-8')] = (ip, port)
        self.pastry =  Pastry(bytes(site, 'utf-8'), peers = peers)
   
    def read_json(self):
         with open('peers.json') as f:
            self.peers = json.load(f)

    # def add_nodes(self, nodes):
    #     self.peers = {}
    #     for node in nodes:
    #         nodeid, ip, port = node
    #         self.peers[bytes(nodeid, 'utf-8')] = (ip, port)
    #     print(self.peers)
    #     with open('peers.json', 'w') as outfile:
    #         json.dump(self.peers, outfile)
    #     self.pastry.update(self.peers)
   
    def route_node(self,nodeid):
        res = self.pastry.route(bytes(nodeid, 'utf-8'))
        return res

    def get_routing_table_items(self):
        print(list(self.pastry.routing_table.items()))
        return list(self.pastry.routing_table.items())

# daemon = Pyro4.Daemon()         # make a Pyro daemon
# uri = daemon.register(Server)   # register the greeting maker as a Pyro object

# daemon = Pyro4.Daemon.serveSimple(
#     {
#         Server: "server obj"
#     },
#     ns = False)

# f = open('uri.txt','w+')
# print(uri,file=f)
# f.close()

# print("Ready. Object uri =PYRO:Pyro.NameServer@localhost:9090")      # print the uri so we can use it in the client later
# daemon.requestLoop()                   # start the event loop of the server to wait for calls


nodeid = 'x01'
ip = '0.0.0.0'
port = 8080
node = [nodeid, ip, port]
ob1 = Server('google.com', [node])

nodeid = 'x02'
ip = '0.0.0.1'
port = 8000
node = [nodeid, ip, port]
ob2 = Server('facebook.com', [node])
# Server.add_nodes([node], 'googe.com')
print("running")
with Pyro4.Daemon() as daemon:
    google_uri = daemon.register(ob1)
    fb_uri = daemon.register(ob2)
    with Pyro4.locateNS() as ns:
        ns.register("DNS.google", google_uri)
        ns.register("DNS.facebook", fb_uri)
    daemon.requestLoop()