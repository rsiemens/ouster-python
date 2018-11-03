from struct import unpack

CHANNEL_BLOCK = (
    "I"  # Range (20 bits, 12 unused)
    "H"  # Reflectivity
    "H"  # Signal photons
    "H"  # Noise photons
    "H"  # Unused
) * 64
AZIMUTH_BLOCK = (
    ">"  # Network byte order
    "Q"  # Timestamp
    "I"  # Measurement ID
    "I"  # Encoder Count
    "{}"  # Channel Data
    "I"  # Status
).format(CHANNEL_BLOCK)
PACKET = AZIMUTH_BLOCK * 64


def unpacker(packet):
    return unpack(AZIMUTH_BLOCK, packet)
