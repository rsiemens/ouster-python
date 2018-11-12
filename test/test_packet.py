import unittest

from os1.packet import unpack

from .utils import FIXTURE_DIR, Recorder


class PacketTestCase(unittest.TestCase):
    def setUp(self):
        self.record = "{}/ousteros-image-prod-aries-v1.6.0-20180816163617_v1.6.0.bin".format(
            FIXTURE_DIR
        )
        self.recorder = Recorder()

    def iter_packets(self):
        for packet in self.recorder.play(self.record):
            yield unpack(packet)

    def test_unpack(self):
        for packet in self.recorder.play(self.record):
            try:
                unpack(packet)
            except Exception:
                self.fail("Couldn't unpack packet")
