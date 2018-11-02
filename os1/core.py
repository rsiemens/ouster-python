import socket


class OS1(object):
    def __init__(self, host, dest_host, queue, mode=16, api_client=None):
        self.queue = queue
        self.mode = mode
        self.api_client = api_client

    def start(self):
        pass

    def stop(self):
        pass

    def __getattr__(self, name):
        return getattr(self.api_client, name)
