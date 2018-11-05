import math

from os1.packet import CHANNEL_BLOCK_COUNT, TICKS_PER_REVOLUTION

beam_altitude_angles = [
    16.611,  16.084,  15.557,  15.029,  14.502,  13.975,  13.447,  12.920,
    12.393,  11.865,  11.338,  10.811,  10.283,  9.756,   9.229,   8.701,
    8.174,   7.646,   7.119,   6.592,   6.064,   5.537,   5.010,   4.482,
    3.955,   3.428,   2.900,   2.373,   1.846,   1.318,   0.791,   0.264,
    -0.264,  -0.791,  -1.318,  -1.846,  -2.373,  -2.900,  -3.428,  -3.955,
    -4.482,  -5.010,  -5.537,  -6.064,  -6.592,  -7.119,  -7.646,  -8.174,
    -8.701,  -9.229,  -9.756,  -10.283, -10.811, -11.338, -11.865, -12.393,
    -12.920, -13.447, -13.975, -14.502, -15.029, -15.557, -16.084, -16.611,
]

beam_azimuth_angles = [
    3.164, 1.055, -1.055, -3.164, 3.164, 1.055, -1.055, -3.164,
    3.164, 1.055, -1.055, -3.164, 3.164, 1.055, -1.055, -3.164,
    3.164, 1.055, -1.055, -3.164, 3.164, 1.055, -1.055, -3.164,
    3.164, 1.055, -1.055, -3.164, 3.164, 1.055, -1.055, -3.164,
    3.164, 1.055, -1.055, -3.164, 3.164, 1.055, -1.055, -3.164,
    3.164, 1.055, -1.055, -3.164, 3.164, 1.055, -1.055, -3.164,
    3.164, 1.055, -1.055, -3.164, 3.164, 1.055, -1.055, -3.164,
    3.164, 1.055, -1.055, -3.164, 3.164, 1.055, -1.055, -3.164,
]

trig_table = []
for i in range(CHANNEL_BLOCK_COUNT):
    trig_table.append([
        math.sin(beam_altitude_angles[i] * 2 * math.pi / 360),
        math.cos(beam_altitude_angles[i] * 2 * math.pi / 360),
        beam_azimuth_angles[i] * 2 * math.pi / 360
    ])


def horizontal_angle(azimuth):
    return 2 * math.pi * azimuth.encoder_count / TICKS_PER_REVOLUTION


def xyz(packet):
    """3D cartesian x, y, z coordinates."""
    coords = [[], [], []]
    for azimuth in packet:
        h_angle = horizontal_angle(azimuth)
        for i, channel in enumerate(azimuth.channels):
            trig_entry = trig_table[i]
            r = channel.range
            h_angle = trig_entry[2] + h_angle
            x = -r * trig_entry[1] + math.cos(h_angle)
            y = r * trig_entry[1] + math.sin(h_angle)
            z = r * trig_entry[0]
            coords[0].append(x)
            coords[1].append(y)
            coords[2].append(z)
    return coords
