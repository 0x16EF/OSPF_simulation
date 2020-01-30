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

    def increaseTimes(self, second):
        for i in range(second):
            self.increaseTime()
            time.sleep(0.005)

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
        raise Exception("router not exist")

    def addLink(self, link):
        if not link in self.links:
            self.links.append(link)

    def connectTwoRouter(self, idOfRouter1, idOfRouter2, wieghtOfLink):
        router1 = self.getRouter(idOfRouter1)
        router2 = self.getRouter(idOfRouter2)
        link = Link(idOfRouter1, idOfRouter2, wieghtOfLink, self)
        self.addLink(link)
        router1.connectToOther(link)

    def getLink(self, id1, id2):
        for link in self.links:
            if (link.firstNode == id1 and link.secondNode == id2) or (link.secondNode == id1 and link.firstNode == id2):
                return link
        return None

    def breakLink(self, router1, router2):
        link = self.getLink(router1, router2)
        link.isOk = False

    def repairLink(self, router1, router2):
        link = self.getLink(router1, router2)
        link.isOk = True

    def ping(self, client1, client2):
        raise Exception("not implement")

    def enableMonitoring(self):
        for router in self.routers:
            router.monitoringIsOn = True
        for client in self.clients:
            client.monitoringIsOn = True

    def disableMonitoring(self):
        for router in self.routers:
            router.monitoringIsOn = False
        for client in self.clients:
            client.monitoringIsOn = False

    def increaseTime(self):
        for router in self.routers:
            router.increaseTime()



network = Network()
network.addRouter(0)
network.addRouter(1)
network.addRouter(2)
network.connectTwoRouter(0, 1, 1)
network.connectTwoRouter(1, 2, 1)
network.connectTwoRouter(0, 2, 3)
#network.breakLink(0, 1)
#network.increaseTimes(15)
print()
