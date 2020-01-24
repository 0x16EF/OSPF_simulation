class Link:
    def __init__(self, start, end, weight, network):
        self.firstNode = start
        self.secondNode = end
        self.weight = weight
        self.isOk = True
        self.network = network

    def sendMessageFrom(self, routerId, message):
        if not self.isOk:
            return False
        if routerId == self.firstNode:
            desRouterId = self.secondNode
        elif routerId == self.secondNode:
            desRouterId = self.firstNode
        else:
            raise Exception("something wrong in link 1!")
        desRouter = self.network.getRouter(desRouterId)
        desRouter.processInputMessage(message, self)
