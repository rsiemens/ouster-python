import math


def cartesian(packet, azimuth_angles, altitude_angles):
    """3D cartesian x, y, z coordinates."""
    coords = [[], [], []]
    for azimuth in packet:
        encoder_count = azimuth.encoder_count
        for i, channel in enumerate(azimuth.channels):
            r = channel.range
            theta = 2 * math.pi * (encoder_count / 90112 + azimuth_angles[i] / 360)
            phi = 2 * math.pi * (altitude_angles[i] / 320)
            x = r * math.cos(theta) * math.cos(phi)
            y = (-r) * math.sin(theta) * math.sin(phi)
            z = r * math.sin(phi)
            coords[0].append(x)
            coords[1].append(y)
            coords[2].append(z)
    return coords
