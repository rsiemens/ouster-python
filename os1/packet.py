import math
import struct

PACKET_SIZE = 12608
TICKS_PER_REVOLUTION = 90112
AZIMUTH_BLOCK_COUNT = 16  # Azimuth blocks per packet
CHANNEL_BLOCK_COUNT = 64  # Channel blocks per Azimuth block
RANGE_BIT_MASK = 0x000FFFFF
CHANNEL_BLOCK = (
    "I"  # Range (20 bits, 12 unused)
    "H"  # Reflectivity
    "H"  # Signal photons
    "H"  # Noise photons
    "H"  # Unused
)
CHANNEL_BLOCK_SIZE = len(CHANNEL_BLOCK)
AZIMUTH_BLOCK = (
    "Q"  # Timestamp
    "I"  # Measurement ID
    "I"  # Encoder Count
    "{}"  # Channel Data
    "I"  # Status
).format(CHANNEL_BLOCK * CHANNEL_BLOCK_COUNT)
AZIMUTH_BLOCK_SIZE = len(AZIMUTH_BLOCK)
PACKET = "<" + (AZIMUTH_BLOCK * AZIMUTH_BLOCK_COUNT)
RADIANS_360 = 2 * math.pi

# Only compile the format string once
_unpack = struct.Struct(PACKET).unpack


def unpack(raw_packet):
    return _unpack(raw_packet)


def azimuth_block(n, packet):
    offset = n * AZIMUTH_BLOCK_SIZE
    return packet[offset : offset + AZIMUTH_BLOCK_SIZE + 1]


def azimuth_timestamp(azimuth_block):
    return azimuth_block[0]


def azimuth_measurement_id(azimuth_block):
    return azimuth_block[1]


def azimuth_encoder_count(azimuth_block):
    return azimuth_block[2]


def azimuth_angle(azimuth_block):
    return RADIANS_360 * azimuth_block[2] / TICKS_PER_REVOLUTION


def azimuth_valid(azimuth_block):
    return azimuth_block[-1] != 0


def channel_block(n, azimuth_block):
    offset = 3 + n * CHANNEL_BLOCK_SIZE
    return azimuth_block[offset : offset + CHANNEL_BLOCK_SIZE + 1]


def channel_range(channel_block):
    return channel_block[0] & RANGE_BIT_MASK


def channel_reflectivity(channel_block):
    return channel_block[1]


def channel_signal_photons(channel_block):
    return channel_block[2]


def channel_noise_photons(channel_block):
    return channel_block[3]
