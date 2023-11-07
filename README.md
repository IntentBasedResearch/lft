# LFT
From: https://github.com/alexandrekaihara/lft

## System Requirements
Your machine must be using a Linux distribution. In our experiments, were used a Ubuntu Server version 20.04.2 LTS virtual machine installed on Virtualbox version 6.1.26 configured with 15 GB RAM, 4 CPU cores e 32 GB memory disk space.

## Installation
All the dependencies consist of:
- Docker (version 20.10.7)
- Python (version 3.8.10)

We provide a Bash script to install all the needed dependencies. To install all dependencies, execute:

> sudo git clone https://github.com/IntentBasedResearch/lft.git OR git@github.com:IntentBasedResearch/lft.git

> cd lft/src

> sudo chmod +x dependencies.sh

> sudo ./dependencies.sh

### Python package
The Paramiko package is used for running ONOS cli commands via ssh. It can be installed with pip.
> pip install paramiko

## Execution
We provide a script to create a small organization topology made by servers and clients (which is possible to define its behavior). To set up the experiment, execute these commands:

> cd lft/src

> sudo python3 demonstration.py

If you want to finish the experiment, press CTRL + C once. If it is the first time you are executing the experiment, it will take longer to instantiate the containers because the images need to be pulled from the Docker Hub.

At the end of execution, there will be generated a report of the execution by [CICFlowMeter](https://www.unb.ca/cic/research/applications.html) that will be located in "lft/demonstration/flows/final_report.csv"

### Define Client's Behavior
All the clients will receive a copy of the folder "lst2.0/demonstration/automation", which contiains all the scripts to simulate a worker during the working hour. Basically, the Client is able to execute 6 tasks inside the network, that is: Browsing the internet; Copying files from the File Server; Access the Email from  the Email Server; Make requests to the Printer; Open SSH sessions with the local Servers; And make Attacks inside the Network.

To change the Client's behavior it is necessary to change create a new client EDIT

## Docker image build
If it is necessary to make any changes to the docker images, check the "docker" folder located in the root directory of this repository. To build any docker image, access the folder containing its "Dockerfile" file and execute:

> docker build --network=host --tag=NEWNAME .

To use the newly built image in the experiment, access the "lft/src/demonstration.py" file and set "dockerImage" parameter of the "instantiate" method with NEWNAME.

## Creating Your Own Experiment
As shown in the section above, the "cidds.py" is an example of how to create a topology with LFT. The following subsections will explain how to execute the basic configurations to instantiate a linear SDN topology with two nodes.

It is important to mention that all the configuration methods must be used after creating the container using the "instantiate" method.

### Create a network node
To create a network node it is necessary to create an instance of [Switch](https://github.com/alexandrekaihara/lst2.0/blob/main/src/switch.py), [Host](https://github.com/alexandrekaihara/lst2.0/blob/main/src/host.py) or [Controller](https://github.com/alexandrekaihara/lst2.0/blob/main/src/controller.py), passing the name of the node as a parameter.

> cd lft/src

> python3

Then execute the following commands:

```
from host import Host
from switch import Switch
from controller import Controller

h1 = Host('h1')
h2 = Host('h2')
s1 = Switch('s1')
c1 = Controller('c1')
```

PS: You are responsible for keeping the instance of each node class in order to delete them at the end

Then is necessary to instantiate the controller using the instance of the class.

```
h1.instantiate()
h2.instantiate()
s1.instantiate()
c1.instantiate()
```

### Connect nodes
After instantiating nodes, you can connect them by using the "connect" method passing the instance of another node.

```
h1.connect(s1, "h1s1")
h2.connect(s1, "h2s2")
s1.connect(c1, "s1c1")
```

### Setting IP into nodes
To set the IP into the nodes you must pass the IP address, its network mask, and the reference to the node to that it is connected. The network mask is an integer that represents the network mask, for example, the network mask '255.255.255.0' corresponds to 24.

```
h1.setIp('10.0.0.1', 24, s1)
h2.setIp('10.0.0.2', 24, s1)
s1.setIp('10.0.0.3', 24)
c1.setIp('10.0.0.4', 24, s1)
```

### Set up the controller
By default, the Controller instance creates a Docker container with the Ryu controller installer inside of it. To instantiate the controller and connect it to a switch you must execute:

```
c1.initController('10.0.0.4', 9001)
s1.setController('10.0.0.4', 9001)
```

Verify if the controller and the switch can communicate successfully with each other.

### Enable connection to Internet
To enable connection to the Internet, the tool must create an interface from the container to the host. The IP parameter of "connectToInternet" can be any address that does not conflict with another already existing subnet on the host and this address will be the default gateway for all the other nodes.

```
s1.connectToInternet('10.0.0.5', 24)
```

### Set Default Gateway
To enable all the other nodes to have access to the Internet, it must be defined the default gateway inside each container to the configured address in the previous section.

```
h1.setDefaultGateway('10.0.0.5', s1)
h2.setDefaultGateway('10.0.0.5', s1)
c1.setDefaultGateway('10.0.0.5', s1)
```

### Enable Network Monitoring
To enable the Netflow, sFlow or IPFIX to monitor the network, you must use either "Switch.enableNetflow()", "Switch.enablesFlow()" or "Switch.enableIPFIX()". For example:

```
s1.enableNetflow('10.0.0.5', 9001)
```

Then Netflow packets will be sent to "10.0.0.5" on port 9001. To end the monitoring, it is necessary to clear the Netflow in the Open vSwitch, by using:

```
s1.clearNetflow()
```


### Deleting Nodes
To delete the nodes execute the following commands:

```
h1.delete()
h2.delete()
s1.delete()
c1.delete()
```
