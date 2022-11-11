from mininet.topo import Topo  

class MyTopo ( Topo ):
    "My Topo." 
    def build (self):
        "Custom Topo."
        a = self.addHost ('a') 
        b = self.addHost ('b')
        c = self.addHost ('c') 
        d = self.addHost ('d') 
        r1 = self.addSwitch ('r1') 
        r2 = self.addSwitch('r2') 

        self.addLink (a, r1, bw = 1000, delay = '1ms') 
        self.addLink (d, r1, bw = 1000, delay = '1ms') 
        self.addLink (r2, r1, bw = 500, delay = '10ms') 
        self.addLink (b, r2, bw = 1000, delay = '1ms') 
        self.addLink (c, r2, bw = 1000, delay = '5ms') 


topos = {'mytopo' : (lambda: MyTopo())}