from Packet import *


class Router:
    def __init__(self, id, network):
        self.network = network
        self.id = id
        self.neighbours = []
        self.LSBD = []
        self.routingTable = []
        self.monitoringIsOn = True
        self.timer = 0
        self.NEIGHBOURS = "neighbours"
        self.CATEGORY = "CATEGORY"
        self.DBD_CATEGORY = "DBD"
        self.LSA_CATEGORY = "LSA"
        self.HELLO_CATEGORY = "HELLO"
        self.PING_CATEGORY = "PING"
        self.INITIAL_CONNECT = "INITIAL_CONNECT"
        self.TYPE = "type"
        self.ACK_INITIAL = "ACK_INITIAL"
        self.BODY = "BODY"
        self.ID = "ID"
        self.TWO_WAY = "2WAY"
        self.SHARE_LSBD = "SHARE_LSBD"
        self.LSBD_STRING = "LSBD"
        self.INITIAL_SHARE_LSBD = "INITIAL_SHARE_LSBD"
        self.ACK_INITAIL_SHARED_LSBD = "ACK_INITAIL_SHARED_LSBD"
        self.UPDATE_LSBD = "UPDATE_LSBD"
        self.ALIVE = "ALIVE"
        self.LOST_LINK = "LOST_LINK"
        self.LINK = "LINK"
        self.NEW_LINK = "NEW_LINK"

    def removeLink(self, srcRoutr, desRouter):
        for link in self.LSBD:
            if (link.firstNode == srcRoutr and link.secondNode == desRouter) or\
                    (link.firstNode == desRouter and link.secondNode == srcRoutr):
                self.LSBD.remove(link)

    def advertiseLink(self, link):
        message = {
            self.CATEGORY: self.LSA_CATEGORY,
            self.ID: self.id,
            self.TYPE: self.LOST_LINK,
            self.BODY: "LOST",
            self.LINK: link
        }
        for neighbour in self.neighbours:
            packet = Packet(message, self.id, neighbour[0])
            self.sendMessageToRouter(neighbour[0], packet)

    def linkLost(self, id, indexInNeighbour):
        link = self.findLinkToNeighbour(id)
        self.removeLink(self.id, id)
        del self.neighbours[indexInNeighbour]
        self.advertiseLink(link)

    def increaseTime(self):
        self.timer += 1
        for i in range(len(self.neighbours)):
            self.neighbours[i][1] += 1
        for i in range(len(self.neighbours)):
            if self.neighbours[i][1] > 30:
                self.linkLost(self.neighbours[i][0], i)
        if self.timer >= 10:
            for i in range(len(self.neighbours)):
                message = {
                    self.CATEGORY: self.HELLO_CATEGORY,
                    self.ID: self.id,
                    self.TYPE: self.ALIVE,
                    self.BODY: "Hello",
                    self.LSBD_STRING: self.LSBD
                }
                packet = Packet(message, self.id, currentNeighbourId)
                currentNeighbourId = self.neighbours[i][0]
                self.sendMessageToRouter(currentNeighbourId, packet)
                self.resetTime()

    def resetTime(self):
        self.timer = 0

    def addNeighbour(self, routerId):
        self.neighbours.append([routerId, 0])

    def addLinkToLSBD(self, link):
        self.LSBD.append(link)

    def connectToOther(self, link):
        #self.updateLSBD([link], -1)
        message = {
            self.CATEGORY:self.HELLO_CATEGORY,
            self.ID: self.id,
            self.TYPE: self.INITIAL_CONNECT,
            self.BODY: "Hello",
            self.NEIGHBOURS: self.neighbours
        }
        if str(link.firstNode) == self.id:
            packet = Packet(message, self.id, link.secondNode)
        elif str(link.secondNode) == self.id:
            packet = Packet(message, self.id, link.firstNode)
        else:
            raise Exception("link is not for router")
        link.sendMessageFrom(self.id, packet)

    def processInputMessage(self, packet, link=None):
        self.monitorInputMessage(packet)
        if packet.message[self.TYPE] == self.INITIAL_CONNECT:
            self.processInitialConnect(packet, link)
        elif packet.message[self.TYPE] == self.ACK_INITIAL:
            self.processInitial2way(packet, link)
        elif packet.message[self.TYPE] == self.TWO_WAY:
            self.processAck2way(packet, link)
        elif packet.message[self.TYPE] == self.INITIAL_SHARE_LSBD:
            self.processInitalShareLSBD(packet, link)
        elif packet.message[self.TYPE] == self.ACK_INITAIL_SHARED_LSBD:
            self.processAckShsredLSBD(packet, link)
        elif packet.message[self.TYPE] == self.ALIVE:
            self.processAliveMessage(packet)
        elif packet.message[self.TYPE] == self.LOST_LINK:
            self.processLostLink(packet)
        elif packet.message[self.TYPE] == self.NEW_LINK:
            self.prcoessNewLink(packet)

    def prcoessNewLink(self, packet):
        link = packet.message[self.LINK]
        self.updateLSBD([link], packet.message[self.ID])

    def processLostLink(self, packet):
        link = packet.message[self.LINK]
        if not self.existLink(link):
            return
        else :
            self.removeLink(link.firstNode, link.secondNode)
        self.floodLostLink(link, packet.message[self.ID])

    def floodLostLink(self, lostLink, srcId):
        message = {
            self.CATEGORY: self.LSA_CATEGORY,
            self.ID: self.id,
            self.TYPE: self.LOST_LINK,
            self.BODY: "LOST",
            self.LINK: lostLink
        }
        self.floodToNetwork(message, [srcId])

    def floodToNetwork(self, message, execptionId):
        for neigbour in self.neighbours:
            if neigbour[0] in execptionId:
                continue
            packet = Packet(message, self.id, neigbour[0])
            self.sendMessageToRouter(neigbour[0], packet)

    def sendMessageToRouter(self, desId, packet):
        link = self.network.getLink(self.id, desId)
        link.sendMessageFrom(self.id, packet)

    def processAliveMessage(self, packet):
        self.updateLSBD(packet.message[self.LSBD_STRING], packet.message[self.ID])

    def notExistInNeighbour(self, idOfRouter):
        for router in self.neighbours:
            if idOfRouter == router[0]:
                return False
        return True

    def monitorInputMessage(self, packet):
        if not self.monitoringIsOn:
            return
        print(str(self.id), end=" : ")
        print(packet.message[self.CATEGORY])
        print(packet.message)

    def processInitialConnect(self, packet, link):
        srcRouter = packet.message[self.ID]
        if self.notExistInNeighbour(srcRouter):
            self.addNeighbour(srcRouter)
        replyMessage = {
            self.CATEGORY: self.HELLO_CATEGORY,
            self.ID: self.id,
            self.TYPE: self.ACK_INITIAL,
            self.BODY: "Hello",
            self.NEIGHBOURS: self.neighbours
        }
        replyPacket = Packet(replyMessage, self.id, srcRouter)
        link.sendMessageFrom(self.id, replyPacket)

    def processInitial2way(self, packet, link):
        if not self.isInNeighbours(self.id, packet.message[self.NEIGHBOURS]):
            return
        srcRouterId = packet.message[self.ID]
        if self.notExistInNeighbour(srcRouterId):
            self.addNeighbour(srcRouterId)
        replayMessage = {
            self.CATEGORY: self.HELLO_CATEGORY,
            self.ID: self.id,
            self.TYPE: self.TWO_WAY,
            self.BODY: "Hello",
            self.NEIGHBOURS: self.neighbours
        }
        replayPacket = Packet(replayMessage, self.id, srcRouterId)
        link.sendMessageFrom(self.id, replayPacket)

    def processAck2way(self, packet, link):
        if not self.isInNeighbours(self.id, packet.message[self.NEIGHBOURS]):
            return
        message = {
            self.CATEGORY: self.DBD_CATEGORY,
            self.ID: self.id,
            self.TYPE: self.INITIAL_SHARE_LSBD,
            self.LSBD_STRING: self.LSBD
        }
        packet = Packet(message, self.id, packet.message[self.ID])
        link.sendMessageFrom(self.id, packet)

    def isInNeighbours(self, id, allNeigbours):
        for neighbour in allNeigbours:
            if neighbour[0] == id:
                return True
        return False

    def findLinkToNeighbour(self, desRouterId):
        for link in self.LSBD:
            if (link.firstNode == self.id and link.secondNode == desRouterId) or (link.secondNode == self.id and
            link.firstNode == desRouterId):
                return link

    def floodNewLink(self, link, srcId):
        message = {
            self.CATEGORY: self.LSA_CATEGORY,
            self.ID: self.id,
            self.TYPE: self.NEW_LINK,
            self.BODY: "NEW",
            self.LINK: link
        }
        self.floodToNetwork(message, [srcId])

    def updateLSBD(self, newLSBD, srcId):
        for link in newLSBD:
            if not self.existLink(link):
                self.addLinkToLSBD(link)
                self.floodNewLink(link, srcId)

    def processInitalShareLSBD(self, packet, link):
        newLSDB = packet.message[self.LSBD_STRING]
        self.updateLSBD(newLSDB, packet.message[self.ID])
        message = {
            self.CATEGORY: self.DBD_CATEGORY,
            self.ID: self.id,
            self.TYPE: self.ACK_INITAIL_SHARED_LSBD,
            self.LSBD_STRING: self.LSBD
        }
        packet = Packet(message, self.id, packet.message[self.ID])
        link.sendMessageFrom(self.id, packet)


    def processAckShsredLSBD(self, packet, link):
        newLSBD = packet.message[self.LSBD_STRING]
        self.updateLSBD(newLSBD, packet.message[self.ID])
        self.updateLSBD([link], self.id)

    def existLink(self, link):
        for l in self.LSBD:
            if (l.firstNode == link.firstNode and l.secondNode == link.secondNode) or (l.firstNode == link.secondNode and l.secondNode == link.firstNode):
                return True
        return False