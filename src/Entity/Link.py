class Link:
    def __init__(self, start, end, weight, network):
        self.firstNode = str(start)
        self.secondNode = str(end)
        self.weight = weight
        self.isOk = True
        self.network = network

    def sendMessageFrom(self, routerId, packet):
        if not self.isOk:
            if packet.message["type"] == "PING_TYPE":
                print("unreachable")
            return False
        if routerId == self.firstNode:
            desRouterId = self.secondNode
        elif routerId == self.secondNode:
            desRouterId = self.firstNode
        else:
            raise Exception("something wrong in link 1!")
        desRouter = self.network.getRouter(desRouterId)
        if desRouter is not None:
            desRouter.processInputMessage(packet, self)
        else:
            desClient = self.network.getClient(desRouterId)
            if desClient is not None:
                desClient.processInputMessage(packet, self)