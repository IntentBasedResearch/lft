# Copyright (C) 2022 Alexandre Mitsuru Kaihara
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.


import logging
from constants import *
import json
import subprocess
from exceptions import *
import json


# Just to enable the declaration of Type in methods
class Node:
    pass


# Brief: This is a super class that define methods common for network nodes
class Node:
    # Brief: Constructor of Node super class
    # Params:
    #   String containerName: Name of the container
    # Return:
    #   None
    def __init__(self, nodeName: str) -> None:
        self.__nodeName = nodeName
        self.memory = ''
        self.cpu = ''

    # OBS: Create nodes with short name lenght due to a restriction on a iproute2 to define and create interfaces.
    # Brief: Instantiate the container
    # Params:
    #   String dockerImage: Name of the container of a local image or in a Docker Hub repository
    #   String DockerCommand: String to be used to instantiate the container instead of the standard command
    #   String memory: It is the amount of memory to be allocated to the container (e.g. "512m", which is 512 MB)
    #   String cpus: It is the amount of cpu dedicated to the container, can be a fractional value such as "0.5"
    # Return:
    #   None
    def instantiate(self, dockerImage="alexandremitsurukaihara/lst2.0:host", dockerCommand='', dns='8.8.8.8', memory='', cpus='') -> None:        
        def addDockerRun(command):
            command.append(DOCKER_RUN)

        def addRunOptions(command):
            command.append("-d")

        def addNetwork(command):
            command.append(NETWORK + "=none")

        def addContainerName(command):
            command.append(NAME + '=' + self.getNodeName())

        def addPrivileged(command):
            command.append(PRIVILEGED)

        def addDNS(command, dns):
            command.append(DNS + '=' + dns)

        def addContainerMemory(command, memory):
            if memory != '': 
                command.append(MEMORY + '=' + memory)

        def addContainerCPUs(command, cpus):
            if cpus != '': 
                command.append(CPUS + '=' + cpus)

        def addContainerImage(command, image):
            command.append(image)

        def buildCommand(command):
            return " ".join(command)

        
        if not self.__imageExists(dockerImage):
            logging.info(f"Image {dockerImage} not found, pulling from remote repository...")
            self.__pullImage(dockerImage)
        
        if dockerCommand == '':
            command = []
            addDockerRun(command)
            addRunOptions(command)
            addNetwork(command)
            addContainerName(command)
            addPrivileged(command)
            addDNS(command, dns)
            addContainerMemory(command, memory)
            addContainerCPUs(command, cpus)
            addContainerImage(command, dockerImage)
    
        try:    
            if dockerCommand != '':
                subprocess.run(dockerCommand, shell=True, capture_output=True)            
            else:
                subprocess.run(buildCommand(command), shell=True, capture_output=True)
        except Exception as ex:
            logging.error(f"Error while criating the container {self.getNodeName()}: {str(ex)}")
            raise NodeInstantiationFailed(f"Error while criating the container {self.getNodeName()}: {str(ex)}")
        
        self.__enableNamespace(self.getNodeName())

    # Brief: Verifies if the image exists
    # Params:
    #   String image: Tag of the Docker image 
    # Return:
    #   True if the image exists locally
    def __imageExists(self, image: str) -> bool:
        out = subprocess.run(f"docker inspect --type=image {image}", shell=True, capture_output=True)
        outJson = json.loads(out.stdout.decode('utf-8'))
        if outJson == []: return False
        else: return True

            
    # Brief: Pulls the image from a Docker Hub repository
    # Params:
    #   String image: Tag of the Docker image 
    # Return:
    #   True if the image exists locally
    def __pullImage(self, image):
        try: 
            subprocess.run(f"docker pull {image}", shell=True)
        except Exception as ex:
            logging.error(f"Error pulling non-existing {image} image: {str(ex)}")
            raise NodeInstantiationFailed(f"Error pulling non-existing {image} image: {str(ex)}")

    # Brief: Instantiate the container
    # Params:
    #   String dockerImage: Name of the container of a local image or in a Docker Hub repository
    #   String DockerCommand: String to be used to instantiate the container instead of the standard command
    # Return:
    #   None
    def delete(self) -> None:
        try:    
            subprocess.run(f"docker kill {self.getNodeName()} && docker rm {self.getNodeName()}", shell=True, capture_output=True)
        except Exception as ex:
            logging.error(f"Error while deleting the host {self.getNodeName()}: {str(ex)}")
            raise NodeInstantiationFailed(f"Error while deleting the host {self.getNodeName()}: {str(ex)}")

    # Brief: Set Ip to an interface (the ip must be set only after connecting it to a container)
    # Params:
    #   String ip: IP address to be set to peerName interface
    #   int mask: Integer that represents the network mask
    #   String node: Reference to the node it is connected to this container to discover the intereface to set the ip to
    # Return:
    #   None
    def setIp(self, ip: str, mask: int, interfaceName: str) -> None:
        #if not self.__interfaceExists(interfaceName):
            #logging.error(f"Network interface {interfaceName} does not exist")
            #raise Exception(f"Network interface {interfaceName} does not exist")

        self.__setIp(ip, mask, interfaceName)

    # Brief: Creates Linux virtual interfaces and connects peers to the nodes, in case of one of the nodes is a switch, it also creates a port in bridge
    # Params:
    #   Node node: Reference of another node to connect to
    # Return:
    #   None
    def connect(self, node: Node, interfaceName: str, peerInterfaceName: str) -> None:
        if self.__interfaceExists(interfaceName) or self.__interfaceExists(peerInterfaceName):
            logging.error(f"Cannot connect to {node.getNodeName()}, {interfaceName} or {peerInterfaceName} already exists")
            raise Exception(f"Cannot connect to {node.getNodeName()}, {interfaceName} or {peerInterfaceName} already exists")

        self.__create(interfaceName, peerInterfaceName)
        self.__setInterface(self.getNodeName(), interfaceName)
        self.__setInterface(node.getNodeName(), peerInterfaceName)

        if self.__class__.__name__ == 'Switch':
            self._Switch__createPort(self.getNodeName(), self.__getThisInterfaceName(node))
        if node.__class__.__name__ == 'Switch':
            node._Switch__createPort(node.getNodeName(), node.__getThisInterfaceName(self))
    
    def connectToInternet(self, hostIP: str, hostMask: int, interfaceName: str, hostInterfaceName: str) -> None:
        self.__create(interfaceName, hostInterfaceName)
        self.__setInterface(self.getNodeName(), interfaceName)
        if self.__class__.__name__ == 'Switch':
            self._Switch__createPort(self.getNodeName(), interfaceName)
        
        subprocess.run(f"ip link set {hostInterfaceName} up", shell=True)
        subprocess.run(f"ip addr add {hostIP}/{hostMask} dev {hostInterfaceName}", shell=True)

        # Enable forwading packets from host to interface
        hostGatewayInterfaceName = subprocess.run(f"route | grep \'^default\' | grep -o \'[^ ]*$\'", shell=True, capture_output=True).stdout.decode('utf8').replace("\n", '')
        subprocess.run(f"iptables -t nat -I POSTROUTING -o {hostGatewayInterfaceName} -j MASQUERADE", shell=True)
        subprocess.run(f"iptables -t nat -I POSTROUTING -o {hostInterfaceName} -j MASQUERADE", shell=True)
        subprocess.run(f"iptables -A FORWARD -i {hostInterfaceName} -o {hostGatewayInterfaceName} -j ACCEPT", shell=True)
        subprocess.run(f"iptables -A FORWARD -i {hostGatewayInterfaceName} -o {hostInterfaceName} -j ACCEPT", shell=True)

    def enableForwarding(self, interfaceName: str, otherInterfaceName: str) -> None:
        self.run(f"iptables -t nat -I POSTROUTING -o {otherInterfaceName} -j MASQUERADE")
        self.run(f"iptables -t nat -I POSTROUTING -o {interfaceName} -j MASQUERADE")
        self.run(f"iptables -A FORWARD -i {interfaceName} -o {otherInterfaceName} -j ACCEPT")
        self.run(f"iptables -A FORWARD -i {otherInterfaceName} -o {interfaceName} -j ACCEPT")

    # Brief: Returns the value of the container name
    # Params:
    # Return:
    #   Returns the name of the node
    def getNodeName(self) -> str:
        return self.__nodeName

    # Brief: Add a route in routing table of container
    # Params:
    #   String ip: IP address of the route
    #   String mask: Network mask for the IP address route
    #   String interfaceName: Name of the interface to forward to
    # Return:
    #   None
    def addRoute(self, ip: str, mask: int,  interfaceName: str):
        if not self.__interfaceExists(interfaceName):
            logging.error(f"Network interface {interfaceName} does not exist")
            raise Exception(f"Network interface {interfaceName} does not exist")
        try:
            subprocess.run(f"docker exec {self.getNodeName()} ip route add {ip}/{mask} dev {interfaceName}", shell=True)
        except Exception as ex:
            logging.error(f"Error adding route {ip}/{mask} via {interfaceName} in {self.getNodeName()}: {str(ex)}")
            raise Exception(f"Error adding route {ip}/{mask} via {interfaceName} in {self.getNodeName()}: {str(ex)}")

    # Brief: Set Ip to an interface (the ip must be set only after connecting it to a container, because)
    # Params:
    #   String destinationIp: The destination IP address of the gateway in format "XXX.XXX.XXX.XXX"
    #   String node: Reference to node that will serve as the first hop to forward the packets to the gateway, this reference node must be already connected to it
    # Return:
    #   None
    def setDefaultGateway(self, destinationIp: str, interfaceName: str) -> None:
        if not self.__interfaceExists(interfaceName):
            logging.error(f"Network interface {interfaceName} does not exist")
            raise Exception(f"Network interface {interfaceName} does not exist")
        
        self.addRoute(destinationIp, 32, interfaceName)
        try:
            subprocess.run(f"docker exec {self.getNodeName()} route add default gw {destinationIp} dev {interfaceName}", shell=True)
        except Exception as ex:
            logging.error(f"Error while setting gateway {destinationIp} on device {interfaceName} in {self.getNodeName()}: {str(ex)}")
            raise Exception(f"Error while setting gateway {destinationIp} on device {interfaceName} in {self.getNodeName()}: {str(ex)}")

    # Brief: Runs a command inside the container
    # Params:
    #   String command: String containing the command to run inside the container
    # Return:
    #   Returns variable that contains stdout and stderr (more information in subprocess documentation)
    def run(self, command: str) -> str:
        try:
            command = command.replace('\"', 'DOUBLEQUOTESDELIMITER')
            command = f"docker exec {self.getNodeName()} bash -c \"" + command + f"\""
            command = command.replace('DOUBLEQUOTESDELIMITER','\\"')
            return subprocess.Popen(command, shell=True)#, capture_output=True)
        except Exception as ex:
            logging.error(f"Error executing command {command} in {self.getNodeName()}: {str(ex)}")
            raise Exception(f"Error executing command {command} in {self.getNodeName()}: {str(ex)}")

    # Brief: Runs multiple commands inside the container
    # Params:
    #   List<String> commands: Runs multiple comands inside the container
    # Return:
    #   Returns a list with the variable that contains stdout and stderr (more information in subprocess documentation)
    def runs(self, commands: list) -> list:
        return [self.run(command) for command in commands]     

    # Brief: Copy local file into container
    # Params:
    #   String path: Absolute or relative path to the file to be copied from local (path+filename)
    #   String destPath: Absolute path to copy the file to the container (path+filename)
    # Return:
    def copyLocalToContainer(self, path: str, destPath: str) -> None:
        try:
            subprocess.run(f"docker cp {path} {self.getNodeName()}:{destPath}", shell=True, capture_output=True)
        except Exception as ex:
            logging.error(f"Error copying file from {path} to {destPath}: {str(ex)}")
            raise Exception(f"Error copying file from {path} to {destPath}: {str(ex)}")

    # Brief: Copy local file into container
    # Params:
    #   String path: Absolute path to the file to be copied from container (path+filename)
    #   String destPath: Absolute or relative path to copy to local (path+filename)
    # Return:
    def copyContainerToLocal(self, path: str, destPath: str) -> None:
        try:
            subprocess.run(f"docker cp {self.getNodeName()}:{path} {destPath}", shell=True, capture_output=True)
        except Exception as ex:
            logging.error(f"Error copying file from {path} to {destPath}: {str(ex)}")
            raise Exception(f"Error copying file from {path} to {destPath}: {str(ex)}")

    def __interfaceExists(self, interfaceName: str) -> bool:
        out = subprocess.run(f"docker exec {self.getNodeName()} ip link | grep {interfaceName}", shell=True, capture_output=True)
        if out.stdout.decode("utf8") != '':
            return True
        return False

    # Brief: Returns the name of the interface to be created on this node
    # Params:
    #   Node node: Reference of another node to connect to
    # Return:
    #   Name of the interface with pattern veth + this node name + other node name
    def __getThisInterfaceName(self, node: Node) -> str:
        return self.getNodeName()+node.getNodeName()

    # Brief: Set Ip to an interface
    # Params:
    #   String ip: IP address to be set to peerName interface
    #   int mask: Integer that represents the network mask
    #   String interfaceName: Name of the interface to set the ip
    # Return:
    #   None
    def __setIp(self, ip: str, mask: int, interfaceName: str) -> None:
        try:
            subprocess.run(f"ip -n {self.getNodeName()} addr add {ip}/{mask} dev {interfaceName}", shell=True)
        except Exception as ex:
            logging.error(f"Error while setting IP {ip}/{mask} to virtual interface {interfaceName}: {str(ex)}")
            raise Exception(f"Error while setting IP {ip}/{mask} to virtual interface {interfaceName}: {str(ex)}")

    # Brief: Returns the name of the interface to be created on other node
    # Params:
    #   Node node: Reference of another node to connect to
    # Return:
    #   Name of the interface with pattern veth + other node name + this node name
    def __getOtherInterfaceName(self, node: Node) -> str:
        return node.getNodeName()+self.getNodeName()

    # Brief: Creates the virtual interfaces and set them up (names cant be the same as some existing one in host's namespace)
    # Params:
    #   String peer1Name: Name of the interface to connect to the first peer 
    #   String peer2Name: Name of the interface to connect to the second peer 
    # Return:
    #   None
    def __create(self, peer1Name: str, peer2Name: str) -> None:
        try:
            subprocess.run(f"ip link add {peer1Name} type veth peer name {peer2Name}", shell=True)
        except Exception as ex:
            logging.error(f"Error while creating virtual interfaces {peer1Name} and {peer2Name}: {str(ex)}")
            raise Exception(f"Error while creating virtual interfaces {peer1Name} and {peer2Name}: {str(ex)}")

    # Brief: Set the interface to node
    # Params:
    #   String nodeName: Name of the node network namespace
    #   String peerName: Name of the interface to set to node
    # Return:
    #   None
    def __setInterface(self, nodeName: str, peerName: str) -> None:
        try:
            subprocess.run(f"ip link set {peerName} netns {nodeName}", shell=True)
            subprocess.run(f"ip -n {nodeName} link set {peerName} up", shell=True)
        except Exception as ex:
            logging.error(f"Error while setting virtual interfaces {peerName} to {nodeName}: {str(ex)}")
            raise Exception(f"Error while setting virtual interfaces {peerName} to {nodeName}: {str(ex)}")

    # Brief: Enable accessing the Docker node namespace directly
    # Params:
    # Return:
    #   None
    def __enableNamespace(self, nodeName) -> None:
        try:    
            subprocess.run(f"pid=$(docker inspect -f '{{{{.State.Pid}}}}' {nodeName}); mkdir -p /var/run/netns/; ln -sfT /proc/$pid/ns/net /var/run/netns/{nodeName}", shell=True)
        except Exception as ex:
            logging.error(f"Error while deleting the host {self.getNodeName()}: {str(ex)}")
            raise Exception(f"Error while deleting the host {self.getNodeName()}: {str(ex)}")

    # Brief: Get all interfaces names
    # Params:
    # Return:
    #   Return a list with the name of all interfaces
    def __getAllIntefaces(self) -> list:
        output = subprocess.run(f"docker exec {self.getNodeName()} ifconfig -a | sed 's/[ \t].*//;/^$/d'", shell=True, capture_output=True)
        interfaces=output.stdout.decode('utf8').replace(":", '').split('\n')
        return list(filter(None, interfaces)) # Remove empty strings

    # Brief: Verifies if the container is active
    # Params:
    # Return:
    #   Return true if it is active or false otherwise
    def __isActive(self) -> bool:
        if subprocess.run(f"docker ps | grep {self.getNodeName()}'", shell=True, capture_output=True).stdout.decode('utf8') != '': return True
        return False
