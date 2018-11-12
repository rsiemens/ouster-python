import json
import sys
from functools import reduce

from os1 import OS1


class Recorder(object):
    SENTINEL = "::"

    def __init__(self, device_ip, host_ip):
        self.os1 = OS1(device_ip, host_ip)
        self.senor_info = json.loads(self.os1.api.get_sensor_info())

    def record(self, count=5):
        image_rev = self.senor_info["image_rev"]
        build_rev = self.senor_info["build_rev"]
        fname = "{}_{}.bin".format(image_rev, build_rev)
        packets = []

        def handler(packet):
            packets.append(packet)

        self.os1.start()
        for i in range(count):
            self.os1.handle_request(handler)

        headers = self._build_headers(packets)
        with open("packets/{}".format(fname), "wb") as f:
            f.write("{}{}".format(headers, self.SENTINEL).encode("utf8"))
            for packet in packets:
                f.write(packet)

    def _build_headers(self, packets):
        headers = {
            "packet_count": len(packets),
            "total_size": reduce(lambda x, y: x + len(y), packets, 0),
            "image_rev": self.senor_info["image_rev"],
            "build_rev": self.senor_info["build_rev"],
            "proto_rev": self.senor_info["proto_rev"],
        }
        return json.dumps(headers)


if __name__ == "__main__":
    device, host = sys.argv[1:3]
    count = 5
    try:
        count = sys.argv[4]
    except IndexError:
        pass

    recorder = Recorder(device, host)
    print("Recording {} packets from device".format(count))
    print("Image Revision: {}".format(recorder.senor_info["image_rev"]))
    print("Build Revision: {}".format(recorder.senor_info["build_rev"]))
    recorder.record(count=5)
    print("Done!")
