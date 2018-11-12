from socketserver import BaseRequestHandler, UDPServer, ThreadingUDPServer

from os1.packet import PACKET_SIZE

UDPServer.max_packet_size = PACKET_SIZE
ThreadingUDPServer.max_packet_size = PACKET_SIZE


class RequestHandler(BaseRequestHandler):
    def __init__(self, handler, *args, **kwargs):
        self.handler = handler
        super(RequestHandler, self).__init__(*args, **kwargs)

    def handle(self):
        data = self.request[0]
        if len(data) == PACKET_SIZE:
            self.handler(data)
