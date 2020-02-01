from Entity.Router import *
from Entity.Client import *
from Entity.Link import *
from Entity.Packet import *
import time


class Network:
    def __init__(self):
        self.routers = []
        self.clients = []
        self.links = []
        self.monitoringIsOn = True
        self.timer = 0

    def increaseTimes(self, second):
        for i in range(second):
            self.increaseTime()

    def existIdOfRouter(self, id):
        for router in self.routers:
            if router.id == id:
                return True
        return False

    def addRouter(self, idOfRouter):
        if self.existIdOfRouter(idOfRouter):
            raise Exception("router " + str(idOfRouter) + " is exist!")
            return False
        else:
            self.routers.append(Router(str(idOfRouter), self))

    def getRouter(self, id):
        for router in self.routers:
            if router.id == str(id):
                return router
        raise Exception("perhaps something is wrong1")
        return None

    def getClient(self, ip):
        for client in self.clients:
            if client.ip == str(ip):
                return client
        return None
    def addLink(self, link):
        if not link in self.links:
            self.links.append(link)

    def connectTwoRouter(self, idOfRouter1, idOfRouter2, wieghtOfLink):
        router1 = self.getRouter(idOfRouter1)
        router2 = self.getRouter(idOfRouter2)
        link = Link(idOfRouter1, idOfRouter2, wieghtOfLink, self)
        self.addLink(link)
        router1.connectToOther(link)

    def connectClientToRouter(self, ipOfClient, idOfRouter, weigthOfLink):
        client = self.getClient(ipOfClient)
        router = self.getRouter(idOfRouter)
        link = Link(ipOfClient, idOfRouter, weigthOfLink)
        self.addLink(link)
        router.connectToOther(link)

    def getLink(self, id1, id2):
        for link in self.links:
            if (link.firstNode == id1 and link.secondNode == id2) or (link.secondNode == id1 and link.firstNode == id2):
                return link
        return None

    def breakLink(self, router1, router2):
        link = self.getLink(str(router1), str(router2))
        link.isOk = False

    def repairLink(self, router1Id, router2Id):
        link = self.getLink(str(router1Id), str(router2Id))
        router1 = self.getRouter(router1Id)
        link.isOk = True
        router1.repairLink(link)

    def ping(self, client1, client2):
        router1 = self.getRouter(client1)
        router1.ping(client2)

    def enableMonitoring(self):
        self.monitoringIsOn = True

    def disableMonitoring(self):
        self.monitoringIsOn = False

    def increaseTime(self):
        self.timer += 1
        for router in self.routers:
            router.increaseTime()



network = Network()
network.disableMonitoring()

file = open("test.txt", 'r')
nextLing = file.readline()
while nextLing != "":
    inp = nextLing.split(" ")
    for i in range(len(inp)):
        inp[i] = inp[i].strip()
    if inp[0] == "add":
        network.addRouter(inp[2])
    elif inp[0] == "connect":
        network.connectTwoRouter(inp[1], inp[2], int(inp[3]))
    elif inp[0] == "sec":
        network.increaseTimes(int(inp[1]))
    elif inp[0] == "ping":
        network.ping(inp[1], inp[2])
    elif inp[0] == "link":
        if inp[3] == "e":
            network.repairLink(inp[1], inp[2])
        elif inp[3] == "d":
            network.breakLink(inp[1], inp[2])
        else:
            raise Exception("something wrong2")
    else:
        raise Exception("something wrong3")
    nextLing = file.readline()