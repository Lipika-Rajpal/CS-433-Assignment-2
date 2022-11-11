from mininet.topo import Topo  

class MyTopo ( Topo ):
    "My Topo." 
    def build (self):
        "Custom Topo."
        a = self.addHost ('a') 
        b = self.addHost ('b')
        r1 = self.addSwitch ('r1') 
        

        self.addLink (a, r1, loss =5) 
        self.addLink (b, r1, loss =5 ) 


topos = {'mytopo' : (lambda: MyTopo())}