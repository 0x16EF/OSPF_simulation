from Packet import *


class Router:
    def __init__(self, id):
        self.id = id
        self.neighbours = []
        self.LSBD = []
        self.routingTable = []
        self.monitoringIsOn = True
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

    def addLinkToLSBD(self, link):
        self.LSBD.append(link)

    def connectToOther(self, link):
        self.addLinkToLSBD(link)
        message = {
            self.CATEGORY:self.HELLO_CATEGORY,
            self.TYPE: self.INITIAL_CONNECT,
            self.BODY: "Hello",
            self.ID: self.id,
            self.NEIGHBOURS: self.neighbours
        }
        if link.firstNode == self.id:
            packet = Packet(message, self.id, link.secondNode)
        elif link.secondNode == self.id:
            packet = Packet(message, self.id, link.firstNode)
        else:
            raise Exception("link is not for router")
        link.sendMessageFrom(self.id, packet)

    def processInputMessage(self, packet, link=None):
        self.monitorInputMessage(packet)
        if packet.message[self.TYPE] == self.INITIAL_CONNECT:
            self.addLinkToLSBD(link)
            self.processInitialConnect(packet, link)
        elif packet.message[self.TYPE] == self.ACK_INITIAL:
            self.processInitial2way(packet, link)
        elif packet.message[self.TYPE] == self.TWO_WAY:
            self.processAck2way(packet, link)
        elif packet.message[self.TYPE] == self.INITIAL_SHARE_LSBD:
            self.processInitalShareLSBD(packet, link)
        elif packet.message[self.TYPE] == self.ACK_INITAIL_SHARED_LSBD:
            self.processAckShsredLSBD(packet)

    def notExistInNeighbour(self, idOfRouter):
        for router in self.neighbours:
            if idOfRouter == router:
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
            self.neighbours.append(srcRouter)
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
        if self.id not in packet.message[self.NEIGHBOURS]:
            return
        srcRouterId = packet.message[self.ID]
        if self.notExistInNeighbour(srcRouterId):
            self.neighbours.append(srcRouterId)
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
        if self.id not in packet.message[self.NEIGHBOURS]:
            return
        message = {
            self.CATEGORY: self.DBD_CATEGORY,
            self.ID: self.id,
            self.TYPE: self.INITIAL_SHARE_LSBD,
            self.LSBD_STRING: self.LSBD
        }
        packet = Packet(message, self.id, packet.message[self.ID])
        link.sendMessageFrom(self.id, packet)


    def findLinkToNeighbour(self, desRouterId):
        for link in self.LSBD:
            if (link.firstNode == self.id and link.secondNode == desRouterId) or (link.secondNode == self.id and
            link.firstNode == desRouterId):
                return link


    def updateLSBD(self, newLSBD):
        for link in newLSBD:
            if link not in self.LSBD:
                self.LSBD.append(link)

    def processInitalShareLSBD(self, packet, link):
        newLSDB = packet.message[self.LSBD_STRING]
        self.updateLSBD(newLSDB)
        message = {
            self.CATEGORY: self.DBD_CATEGORY,
            self.ID: self.id,
            self.TYPE: self.UPDATE_LSBD,
            self.LSBD_STRING: self.LSBD
        }
        packet = Packet(message, self.id, packet.message[self.ID])
        link.sendMessageFrom(self.id, packet)

    def processAckShsredLSBD(self, packet, link):
        newLSBD = packet.message[self.LSBD_STRING]
        self.updateLSBD(newLSBD)