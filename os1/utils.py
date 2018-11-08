import math

from os1.packet import (
    AZIMUTH_BLOCK_COUNT,
    CHANNEL_BLOCK_COUNT,
    azimuth_angle,
    azimuth_block,
    azimuth_valid,
    channel_block,
    channel_range,
    unpack,
)


class UninitializedTrigTable(Exception):
    def __init__(self):
        msg = (
            "You must build_trig_table prior to calling xyz_point or"
            "xyz_points.\n\n"
            "This is likely because you are in a multiprocessing environment."
        )
        super(UninitializedTrigTable, self).__init__(msg)


_trig_table = []


def build_trig_table(beam_altitude_angles, beam_azimuth_angles):
    if not _trig_table:
        for i in range(CHANNEL_BLOCK_COUNT):
            _trig_table.append(
                [
                    math.sin(beam_altitude_angles[i] * math.radians(1)),
                    math.cos(beam_altitude_angles[i] * math.radians(1)),
                    beam_azimuth_angles[i] * math.radians(1),
                ]
            )


def xyz_point(channel_n, azimuth_block):
    if not _trig_table:
        raise UninitializedTrigTable()

    channel = channel_block(channel_n, azimuth_block)
    table_entry = _trig_table[channel_n]
    range = channel_range(channel) / 1000  # to meters
    adjusted_angle = table_entry[2] + azimuth_angle(azimuth_block)
    x = -range * table_entry[1] * math.cos(adjusted_angle)
    y = range * table_entry[1] * math.sin(adjusted_angle)
    z = range * table_entry[0]

    return x, y, z


def xyz_points(packet):
    """3D cartesian x, y, z coordinates."""
    if not isinstance(packet, tuple):
        packet = unpack(packet)

    x = []
    y = []
    z = []

    for b in range(AZIMUTH_BLOCK_COUNT):
        block = azimuth_block(b, packet)

        if not azimuth_valid(block):
            continue

        for c in range(CHANNEL_BLOCK_COUNT):
            point = xyz_point(c, block)
            x.append(point[0])
            y.append(point[1])
            z.append(point[2])
    return x, y, z
