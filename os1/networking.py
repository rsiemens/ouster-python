from socketserver import BaseRequestHandler, ThreadingMixIn, UDPServer


class QueingRequestHandler(BaseRequestHandler):
    def __init__(self, queue, *args, **kwargs):
        self.queue = queue
        super(QueingRequestHandler, self).__init__(*args, **kwargs)

    def handle(self):
        data = self.request[0]
        self.queue.put(data)


class SynchronousRequestHandler(BaseRequestHandler):
    def __init__(self, handler, *args, **kwargs):
        self.handler = handler
        super(SynchronousRequestHandler, self).__init__(*args, **kwargs)

    def handle(self):
        data = self.request[0]
        self.handler(data)
