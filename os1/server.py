from socketserver import BaseRequestHandler, UDPServer

from os1.packet import PACKET_SIZE

UDPServer.max_packet_size = PACKET_SIZE


class SynchronousRequestHandler(BaseRequestHandler):
    def __init__(self, handler, *args, **kwargs):
        self.handler = handler
        super(SynchronousRequestHandler, self).__init__(*args, **kwargs)

    def handle(self):
        data = self.request[0]
        if len(data) == PACKET_SIZE:
            self.handler(data)
        else:
            print(
                "dropped packet of size: {} should be {}".format(len(data), PACKET_SIZE)
            )
