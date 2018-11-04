import struct
from collections import namedtuple

PACKET_SIZE = 12608
AZIMUTH_BLOCK_SIZE = 788  # Bytes per azimuth block
AZIMUTH_BLOCK_COUNT = 16  # Azimuth blocks per packet
CHANNEL_BLOCK_SIZE = 12  # Bytes per channel block
CHANNEL_BLOCK_COUNT = 64  # Channel blocks per Azimuth block
RANGE_BIT_MASK = 0x000FFFFF
CHANNEL_BLOCK = (
    "I"  # Range (20 bits, 12 unused)
    "H"  # Reflectivity
    "H"  # Signal photons
    "H"  # Noise photons
    "H"  # Unused
) * CHANNEL_BLOCK_COUNT
AZIMUTH_BLOCK = (
    "Q"  # Timestamp
    "I"  # Measurement ID
    "I"  # Encoder Count
    "{}"  # Channel Data
    "I"  # Status
).format(CHANNEL_BLOCK)
PACKET = "<" + (AZIMUTH_BLOCK * AZIMUTH_BLOCK_COUNT)

AzimuthBlock = namedtuple(
    "AzimuthBlock",
    ["timestamp", "measurement_id", "encoder_count", "channels", "status"],
)
ChannelBlock = namedtuple(
    "ChannelBlock", ["range", "reflectivity", "signal_photon", "noise_photon", "unused"]
)


def deserialize(raw_packet):
    packet = []
    unpacked = unpack(raw_packet)
    for azimuth in chunks(unpacked, 324):
        channels = []
        for channel in chunks(azimuth[3:-1], 5):
            channel_range = RANGE_BIT_MASK & channel[0]
            channels.append(
                ChannelBlock(
                    channel_range, channel[1], channel[2], channel[3], channel[4]
                )
            )
        packet.append(
            AzimuthBlock(azimuth[0], azimuth[1], azimuth[2], channels, azimuth[-1])
        )
    return packet


def unpack(raw_packet):
    return struct.unpack(PACKET, raw_packet)


def chunks(packet, size):
    for i in range(0, len(packet), size):
        yield packet[i : i + size]
