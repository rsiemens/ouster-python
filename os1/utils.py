import math
import struct
import sys

from os1.packet import (
    AZIMUTH_BLOCK_COUNT,
    CHANNEL_BLOCK_COUNT,
    azimuth_angle,
    azimuth_block,
    azimuth_measurement_id,
    azimuth_timestamp,
    azimuth_valid,
    channel_block,
    channel_range,
    unpack,
)

# The OS-16 will still contain 64 channels in the packet, but only
# every 4th channel starting at the 2nd will contain data .
OS_16_CHANNELS = (2, 6, 10, 14, 18, 22, 26, 30, 34, 38, 42, 46, 50, 54, 58, 62)
OS_64_CHANNELS = tuple(i for i in range(CHANNEL_BLOCK_COUNT))


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

    return [x, y, z]


def xyz_points(packet, os16=False):
    """
    Returns a tuple of x, y, z points where each x, y, z is a list of
    all the x, y or z points in the packet

        (
            [x1, x2, ...],
            [y1, y2, ...],
            [z1, z2, ...],
        )
    """
    channels = OS_16_CHANNELS if os16 else OS_64_CHANNELS
    if not isinstance(packet, tuple):
        packet = unpack(packet)

    x = []
    y = []
    z = []

    for b in range(AZIMUTH_BLOCK_COUNT):
        block = azimuth_block(b, packet)

        if not azimuth_valid(block):
            continue

        for c in channels:
            point = xyz_point(c, block)
            x.append(point[0])
            y.append(point[1])
            z.append(point[2])
    return x, y, z


def xyz_columns(packet, os16=False):
    """
    Similar to xyz_points except the x, y, z values are ordered by
    column. This is convenient if you only want to render a specific
    column.

    The structure of it will be be columns containing channels. It
    looks like...

        [
            # column 1
            [
                [channel1_x, channel2_x, ...],
                [channel1_y, channel2_y, ...],
                [channel1_z, channel2_z, ...],
            ],
            # column 2
            [
                [channel1_x, channel2_x, ...],
                [channel1_y, channel2_y, ...],
                [channel1_z, channel2_z, ...],
            ],
        ]
    """
    channels = OS_16_CHANNELS if os16 else OS_64_CHANNELS
    if not isinstance(packet, tuple):
        packet = unpack(packet)

    points = []
    for b in range(AZIMUTH_BLOCK_COUNT):
        block = azimuth_block(b, packet)
        x = []
        y = []
        z = []

        for channel in channels:
            point = xyz_point(channel, block)
            x.append(point[0])
            y.append(point[1])
            z.append(point[2])
        points.append([x, y, z])
    return points


_unpack = struct.Struct("<I").unpack


def peek_encoder_count(packet):
    return _unpack(packet[12:16])[0]


def frame_handler(queue):
    """
    Handler that buffers packets until it has a full frame then puts
    them into a queue. Queue must have a put method.

    The data put into the queue will be a dict that contains a buffer
    of packets making up a frame and the rotation number.

        {
            'buffer': [packet1, packet2, ...],
            'rotation': 1
        }
    """
    buffer = []
    rotation_num = 0
    sentinel = None
    last = None

    def handler(packet):
        nonlocal rotation_num, sentinel, last, buffer

        encoder_count = peek_encoder_count(packet)
        if sentinel is None:
            sentinel = encoder_count

        if buffer and last and encoder_count >= sentinel and last <= sentinel:
            rotation_num += 1
            queue.put({"buffer": buffer, "rotation": rotation_num})
            buffer = []

        buffer.append(packet)
        last = encoder_count

    return handler
