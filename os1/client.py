from socketserver import (
    BaseRequestHandler,
    ThreadingMixIn,
    UDPServer,
)


class QueingRequestHandler(BaseRequestHandler):
    def __init__(self, unpacker, queue):
        self.unpack = unpacker
        self.queue = queue

    def handle(self):
        data = self.request[0]
        packet = self.unpack(data)
        self.queue.put(packet)

