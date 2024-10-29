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

h1 = Host("h1")
h2 = Host("h2")
h3 = Host("h3")
middlebox = Host("middlebox")

s1 = Switch("s1") #getcwd() +'/flows/'+"s1", '/home/pcap')
s2 = Switch("s2")
s3 = Switch("s3")
s4 = Switch("s4")
s5 = Switch("s5")
s6 = Switch("s6")
s7 = Switch("s7")
s8 = Switch("s8")
s9 = Switch("s9")
s10 = Switch("s10")

nodes = {}

def createSwitch():
    print("[Experiment] Creating switch s1")
    print("... Instatiating container")
    s1.instantiate(networkMode='bridge')
    print("[Experiment] Creating switch s2")
    print("... Instatiating container")
    s2.instantiate(networkMode='bridge')
    print("[Experiment] Creating switch s3")
    print("... Instatiating container")
    s3.instantiate(networkMode='bridge')
    print("[Experiment] Creating switch s4")
    print("... Instatiating container")
    s4.instantiate(networkMode='bridge')
    print("[Experiment] Creating switch s5")
    print("... Instatiating container")
    s5.instantiate(networkMode='bridge')
    print("[Experiment] Creating switch s6")
    print("... Instatiating container")
    s6.instantiate(networkMode='bridge')
    print("[Experiment] Creating switch s7")
    print("... Instatiating container")
    s7.instantiate(networkMode='bridge')
    print("[Experiment] Creating switch s8")
    print("... Instatiating container")
    s8.instantiate(networkMode='bridge')
    print("[Experiment] Creating switch s9")
    print("... Instatiating container")
    s9.instantiate(networkMode='bridge')
    print("[Experiment] Creating switch s10")
    print("... Instatiating container")
    s10.instantiate(networkMode='bridge')
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
    s3.delete()
    s4.delete()
    s5.delete()
    s6.delete()
    s7.delete()
    s8.delete()
    s9.delete()
    s10.delete()
    h1.delete()
    h2.delete()
    h3.delete()
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
    print("[Experiment] Setting controller for all the switches")
    s1.setController("172.17.0.2", 6653) # Onos container's IP (can be obtained with docker container inspect) and default port for OpenFlow
    s2.setController("172.17.0.2", 6653)
    s3.setController("172.17.0.2", 6653)
    s4.setController("172.17.0.2", 6653)
    s5.setController("172.17.0.2", 6653)
    s6.setController("172.17.0.2", 6653)
    s7.setController("172.17.0.2", 6653)
    s8.setController("172.17.0.2", 6653)
    s9.setController("172.17.0.2", 6653)
    s10.setController("172.17.0.2", 6653)

    print(["[Experiment] Creating Hosts"])
    # Hosts inside developers subnetwork
    print(" ... Instantiating h1")
    h1.instantiate() #dockerImage="perfsonar/testpoint")
    print(" ... Instantiating h2")
    h2.instantiate()
    # Hosts in other subnetwork
    print(" ... Instantiating h3")
    h3.instantiate() #dockerImage="perfsonar/testpoint")
    print(" ... Instantiating middlebox")
    middlebox.instantiate()

    print("[Experiment] Connecting Nodes")
    s1.connect(h1, "s1h1", "h1s1")
    s1.connect(h2, "s1h2", "h2s1")

    s10.connect(h3, "s10h3", "h3s10")
    s10.connect(middlebox, "s10middlebox", "middleboxs10")

    # Connecting Switches
    s1.connect(s2, "s1s2", "s2s1")
    s2.connect(s3, "s2s3", "s3s2")
    s3.connect(s4, "s3s4", "s4s3")
    s4.connect(s5, "s4s5", "s5s4")
    s5.connect(s6, "s5s6", "s6s5")
    s6.connect(s7, "s6s7", "s7s6")
    s7.connect(s8, "s7s8", "s8s7")
    s8.connect(s9, "s8s9", "s9s8")
    s9.connect(s10, "s9s10", "s10s9")
    
    h1.setIp("192.168.0.1", 24, "h1s1")
    h2.setIp("192.168.0.2", 24, "h2s1")
    h3.setIp("192.168.1.3", 24, "h3s10")
    middlebox.setIp("192.168.1.4", 24, "middleboxs10")

    s1.addRoute("192.168.1.0", 24, "s1s2")
    s2.addRoute("192.168.0.0", 24, "s2s1")
    s2.addRoute("192.168.1.0", 24, "s2s3")
    s3.addRoute("192.168.1.0", 24, "s3s4")
    s3.addRoute("192.168.0.0", 24, "s3s2")
    s4.addRoute("192.168.1.0", 24, "s4s5")
    s4.addRoute("192.168.0.0", 24, "s4s3")
    s5.addRoute("192.168.1.0", 24, "s5s6")
    s5.addRoute("192.168.0.0", 24, "s5s4")
    s6.addRoute("192.168.1.0", 24, "s6s7")
    s6.addRoute("192.168.0.0", 24, "s6s5")
    s7.addRoute("192.168.1.0", 24, "s7s8")
    s7.addRoute("192.168.0.0", 24, "s7s6")
    s8.addRoute("192.168.1.0", 24, "s8s9")
    s8.addRoute("192.168.0.0", 24, "s8s7")
    s9.addRoute("192.168.1.0", 24, "s9s10")
    s9.addRoute("192.168.0.0", 24, "s9s8")
    s10.addRoute("192.168.0.0", 24, "s10s9")

    print("[Experiment] Generating simple traffic for host detection")
    subprocess.run(f"docker exec h1 ping 192.168.0.2 -c 2", shell=True)
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