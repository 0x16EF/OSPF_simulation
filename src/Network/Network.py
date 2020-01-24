from Entity.Router import *
from Entity.Client import *
from Entity.Link import *
from Entity.Packet import *


class Network:
    def __init__(self):
        self.routers = []
        self.clients = []
        self.links = []

    def nexSecond(self):
        raise Exception("not implement")

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
            self.routers.append(Router(idOfRouter))

    def getRouter(self, id):
        for router in self.routers:
            if router.id == id:
                return router
        raise Exception("router not exist")

    def connectTwoRouter(self, idOfRouter1, idOfRouter2, wieghtOfLink):
        router1 = self.getRouter(idOfRouter1)
        link = Link(idOfRouter1, idOfRouter2, wieghtOfLink, self)
        router1.connectToOther(link)

    def breakLink(self, router1, router2):
        raise Exception("not implement")

    def repairLink(self, router1, router2):
        raise Exception("not implement")

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



network = Network()
network.addRouter(0)
network.addRouter(1)
network.connectTwoRouter(0, 1, 5)

