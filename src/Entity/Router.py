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
        self.TYPE_ENTITY = "TYPE_ENTITY"
        self.CLIETN_TYPE = "CLIENT_ENTITY"
        self.ROUTER_TYPE = "ROUTER_ENTITY"
        self.PING_TYPE = "PING_TYPE"
        self.DES_ID = "DESINATION_ID"
        self.routingTable = {}

    def findAllNodes(self):
        allNodes = []
        present = []
        for link in self.LSBD:
            if link.firstNode not in present:
                present.append(link.firstNode)
                allNodes.append([link.firstNode, float("inf"), None, True])
            if link.secondNode not in present:
                present.append(link.secondNode)
                allNodes.append([link.secondNode, float("inf"), None, True])
        return allNodes

    def findIndexOfNode(self, id, list):
        for i in range(len(list)):
            if list[i][0] == id:
                return i
        raise Exception("can't find")

    def updateCost(self, currentNode, link, allNode):
        if link.firstNode == currentNode:
            targetNode = link.secondNode
        else:
            targetNode = link.firstNode
        indexOfCurrentNode = self.findIndexOfNode(currentNode, allNode)

        newCost = allNode[indexOfCurrentNode][1] + link.weight
        indexOfTargetnode = self.findIndexOfNode(targetNode, allNode)
        if allNode[indexOfTargetnode][1] > newCost:
            allNode[indexOfTargetnode][1] = newCost
            allNode[indexOfTargetnode][2] = currentNode


    def createRoutingTable(self):
        allNode = self.findAllNodes()
        links = self.LSBD
        currentNode = self.id
        continueCondition = True
        indexOfCurrentNode = self.findIndexOfNode(self.id, allNode)
        allNode[indexOfCurrentNode][1] = 0
        allNode[indexOfCurrentNode][3] = False
        while continueCondition:
            for link in links:
                if link.firstNode == currentNode or link.secondNode == currentNode:
                    self.updateCost(currentNode, link, allNode)
            minIndex = -1
            minValue = float('inf')
            for i in range(len(allNode)):
                if allNode[i][3] and allNode[i][1] < minValue:
                    minValue = allNode[i][1]
                    minIndex = i
            if minIndex == -1:
                continueCondition = False
            else:
                currentNode = allNode[minIndex][0]
                allNode[minIndex][3] = False
        for node in allNode:
            self.routingTable[node[0]] = node[2]

    def findNextRouter(self, id):
        continueCondition = True
        currentTarget = id
        while continueCondition:
            before = self.routingTable[currentTarget]
            if before == None:
                return None
            elif before == self.id:
                return currentTarget
            currentTarget = before
        raise Exception("something going wrong")

    def processPingMessage(self, packet):
        desId = packet.message[self.DES_ID]
        self.ping(desId)

    def ping(self, desId):
        print(self.id, end=" ")
        if self.id == desId:
            print()
            return
        if desId not in self.routingTable.keys():
            print("invalid")
            return
        nextRouter = self.findNextRouter(desId)
        if nextRouter == None:
            print("invalid")
            return
        link = self.network.getLink(self.id, nextRouter)
        message = {
            self.CATEGORY: self.PING_CATEGORY,
            self.ID: self.id,
            self.TYPE: self.PING_TYPE,
            self.BODY: "Ping",
            self.DES_ID: desId
        }
        packet = Packet(message, self.id, nextRouter)
        link.sendMessageFrom(self.id, packet)

    def removeLink(self, srcRoutr, desRouter):
        update = False
        for link in self.LSBD:
            if (link.firstNode == srcRoutr and link.secondNode == desRouter) or\
                    (link.firstNode == desRouter and link.secondNode == srcRoutr):
                self.LSBD.remove(link)
                update = True
        if update:
            self.createRoutingTable()

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
        if link != None:
            self.advertiseLink(link)

    def increaseTime(self):
        self.timer += 1
        for i in range(len(self.neighbours)):
            self.neighbours[i][1] += 1
        i = 0
        while i < len(self.neighbours):
            if self.neighbours[i][1] >= 30:
                self.linkLost(self.neighbours[i][0], i)
            else:
                i += 1
        if self.timer >= 10:
            for i in range(len(self.neighbours)):
                message = {
                    self.CATEGORY: self.HELLO_CATEGORY,
                    self.ID: self.id,
                    self.TYPE: self.ALIVE,
                    self.BODY: "Hello",
                    self.LSBD_STRING: self.LSBD
                }
                currentNeighbourId = self.neighbours[i][0]
                packet = Packet(message, self.id, currentNeighbourId)
                self.sendMessageToRouter(currentNeighbourId, packet)
                self.resetTime()

    def resetTime(self):
        self.timer = 0

    def addNeighbour(self, routerId):
        self.neighbours.append([routerId, 0])

    def addLinkToLSBD(self, link):
        if link.firstNode == self.id:
            target = link.secondNode
        else:
            target = link.firstNode
        if self.notExistInNeighbour(target) and (link.firstNode == self.id or link.secondNode == self.id):
            self.addNeighbour(target)
        self.LSBD.append(link)

    def connectToOther(self, link):
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
        elif packet.message[self.TYPE] == self.PING_TYPE:
            self.processPingMessage(packet)
        else:
            raise Exception("something is wrong 4")

    def prcoessNewLink(self, packet):
        link = packet.message[self.LINK]
        self.updateLSBD([link], packet.message[self.ID])

    def removeFromNeigbourIfNotOnotherLink(self, link):
        if link.firstNode != self.id and link.secondNode != self.id:
            return
        if link.firstNode == self.id:
            targetRouter = link.secondNode
        else:
            targetRouter = link.firstNode
        if not self.existLink(link):
            for neighbour in self.neighbours:
                if neighbour[0] == targetRouter:
                    self.neighbours.remove(neighbour)

    def processLostLink(self, packet):
        link = packet.message[self.LINK]
        if not self.existLink(link):
            return
        else :
            self.removeLink(link.firstNode, link.secondNode)
        self.removeFromNeigbourIfNotOnotherLink(link)
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

    def resetTimerOfNeighbour(self, id):
        for neigbour in self.neighbours:
            if neigbour[0] == id:
                neigbour[1] = 0


    def processAliveMessage(self, packet):
        self.updateLSBD(packet.message[self.LSBD_STRING], packet.message[self.ID])
        srcId = packet.message[self.ID]
        self.resetTimerOfNeighbour(srcId)


    def notExistInNeighbour(self, idOfRouter):
        for router in self.neighbours:
            if idOfRouter == router[0]:
                return False
        return True

    def monitorInputMessage(self, packet):
        if not self.network.monitoringIsOn:
            return
        print(self.network.timer)
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

    def repairLink(self, link):
        if self.existLink(link):
            self.floodNewLink(link, self.id)
        else:
            self.updateLSBD([link], self.id)

    def updateLSBD(self, newLSBD, srcId, updateRoutingTable=True):
        update = False
        for link in newLSBD:
            if not self.existLink(link):
                self.addLinkToLSBD(link)
                update = True
                self.floodNewLink(link, srcId)
        if update and updateRoutingTable:
            self.createRoutingTable()

    def processInitalShareLSBD(self, packet, link):
        newLSDB = packet.message[self.LSBD_STRING]
        self.updateLSBD(newLSDB, packet.message[self.ID], False)
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
        self.updateLSBD([link], self.id)
        self.updateLSBD(newLSBD, packet.message[self.ID])


    def existLink(self, link):
        for l in self.LSBD:
            if (l.firstNode == link.firstNode and l.secondNode == link.secondNode) or (l.firstNode == link.secondNode and l.secondNode == link.firstNode):
                return True
        return False