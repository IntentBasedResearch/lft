import subprocess
from host import Host
from switch import Switch
from controller import Controller
from onos import ONOS
import paramiko

from os import getcwd
import signal
import sys

c1 = Controller("c1")

# Developers subnetwork
h1 = Host("h1")
h2 = Host("h2")
h4 = Host("h4")
h5 = Host("h5")
h6 = Host("h6")
h7 = Host("h7")
h8 = Host("h8")
h9 = Host("h9")
h10 = Host("h10")
h11 = Host("h11")
# Other subnetwork
h3 = Host("h3")
middlebox = Host("middlebox")

s1 = Switch("s1") #getcwd() +'/flows/'+"s1", '/home/pcap')
s2 = Switch("s2")

nodes = {}

def createSwitch():
    print("[Experiment] Creating switch s1")
    print("... Instatiating container")
    s1.instantiate(networkMode='bridge')
    print("[Experiment] Creating switch s2")
    print("... Instatiating container")
    s2.instantiate(networkMode='bridge')
    print("[Experiment] Switches created successfully")

def createController(name: str):
    print(f" ... Creating controller {name}")
    nodes[name] = ONOS(name)
    mapports = False
    if name == "c1": mapports = True
    nodes[name].instantiate(mapPorts=mapports)
    print(" ... Creating config folder")
    subprocess.call(f"docker exec {name} mkdir /root/onos/config", shell=True)
    print(f" ... Controller {name} created successfully")

def signal_handler(sig, frame):
    print("You've pressed Ctrl+C!")
    [node.delete() for _,node in nodes.items()]
    s1.delete()
    s2.delete()
    h1.delete()
    h2.delete()
    h3.delete()
    h4.delete()
    h5.delete()
    h6.delete()
    h7.delete()
    h8.delete()
    h9.delete()
    h10.delete()
    h11.delete()
    middlebox.delete()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

try:
    print("Starting experiment")
    print("[LFT] ... Creating ONOS controller")
    createController("c1")

    print("[Experiment] ONOS created sucessfully, wait for initialization and press y")
    inp = ''
    while(inp != 'y'):
        inp = input(" Proceed to switch creation? [y]")

    nodes["c1"].activateONOSApps("172.17.0.2")
    createSwitch()
    print("[Experiment] Setting controller for the s1 and s2")
    s1.setController("172.17.0.2", 6653) # Onos container's IP (can be obtained with docker container inspect) and default port for OpenFlow
    s2.setController("172.17.0.2", 6653)

    print(["[Experiment] Creating Hosts"])
    print(" ... Instantiating h1")
    h1.instantiate() #dockerImage="perfsonar/testpoint")
    print(" ... Instantiating h2")
    h2.instantiate()
    print(" ... Instantiating h3")
    h3.instantiate() #dockerImage="perfsonar/testpoint")
    print(" ... Instantiating h4")
    h4.instantiate()
    print(" ... Instantiating h5")
    h5.instantiate()
    print(" ... Instantiating h6")
    h6.instantiate()
    print(" ... Instantiating h7")
    h7.instantiate()
    print(" ... Instantiating h8")
    h8.instantiate()
    print(" ... Instantiating h9")
    h9.instantiate()
    print(" ... Instantiating h10")
    h10.instantiate()
    print(" ... Instantiating h11")
    h11.instantiate()
    print(" ... Instantiating middlebox")
    middlebox.instantiate()

    print("[Experiment] Connecting Nodes")
    s1.connect(h1, "s1h1", "h1s1")
    s1.connect(h2, "s1h2", "h2s1")
    s1.connect(h1, "s1h1", "h1s1")
    s1.connect(h2, "s1h2", "h2s1")
    s1.connect(h3, "s1h3", "h3s1")
    s1.connect(h4, "s1h4", "h4s1")
    s1.connect(h5, "s1h5", "h5s1")
    s1.connect(h6, "s1h6", "h6s1")
    s1.connect(h7, "s1h7", "h7s1")
    s1.connect(h8, "s1h8", "h8s1")
    s1.connect(h9, "s1h9", "h9s1")
    s1.connect(h10, "s1h10", "h10s1")
    s1.connect(h11, "s1h11", "h11s1")

    s2.connect(h3, "s2h3", "h3s2")
    s2.connect(middlebox, "s2middlebox", "middleboxs2")

    s1.connect(s2, "s1s2", "s2s1")
    
    h1.setIp("192.168.0.1", 24, "h1s1")
    h2.setIp("192.168.0.2", 24, "h2s1")
    h4.setIp("192.168.0.4", 24, "h4s1")
    h5.setIp("192.168.0.5", 24, "h5s1")
    h6.setIp("192.168.0.6", 24, "h6s1")
    h7.setIp("192.168.0.7", 24, "h7s1")
    h8.setIp("192.168.0.8", 24, "h8s1")
    h9.setIp("192.168.0.9", 24, "h9s1")
    h10.setIp("192.168.0.10", 24, "h10s1")
    h11.setIp("192.168.0.11", 24, "h11s1")
    # Other subnetwork
    h3.setIp("192.168.1.3", 24, "h3s2")
    middlebox.setIp("192.168.1.4", 24, "middleboxs2")

    s1.addRoute("192.168.1.0", 24, "s1s2")
    s2.addRoute("192.168.0.0", 24, "s2s1")

    print("[Experiment] Generating simple traffic for host detection")
    subprocess.run(f"docker exec h1 ping 192.168.0.2 -c 2", shell=True)
    subprocess.run(f"docker exec h1 ping 192.168.0.4 -c 2", shell=True)
    subprocess.run(f"docker exec h1 ping 192.168.0.5 -c 2", shell=True)
    subprocess.run(f"docker exec h1 ping 192.168.0.6 -c 2", shell=True)
    subprocess.run(f"docker exec h1 ping 192.168.0.7 -c 2", shell=True)
    subprocess.run(f"docker exec h1 ping 192.168.0.8 -c 2", shell=True)
    subprocess.run(f"docker exec h1 ping 192.168.0.9 -c 2", shell=True)
    subprocess.run(f"docker exec h1 ping 192.168.0.10 -c 2", shell=True)
    subprocess.run(f"docker exec h1 ping 192.168.0.11 -c 2", shell=True)
    subprocess.run(f"docker exec h3 ping 192.168.1.4 -c 2", shell=True)

except Exception as e:
    [node.delete() for _,node in nodes.items()]
    s1.delete()
    s2.delete()
    h1.delete()
    h2.delete()
    h3.delete()
    middlebox.delete()
    raise(e)

print("[Experiment] Press ctrl+c to stop the program")
signal.pause()
