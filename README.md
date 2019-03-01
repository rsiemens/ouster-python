# Python client for the Ouster Lidar OS-1

Compatible with Firmware Version 1.10.0 and python 3
> Your milage may vary with other versions, it was tested against a device OS1-16
> device running 1.10.0

## Installing
`pip install --upgrade ouster-os1`

## Quick start
```python
from os1 import OS1
from os1.utils import xyz_points


def handler(raw_packet):
    """Takes each packet and log it to a file as xyz points"""
    with open('points.csv', 'a') as f:
        x, y, z = xyz_points(raw_packet)
        for coords in zip(x, y, z):
            f.write("{}\n".format(','.join(coords)))


os1 = OS1('10.0.0.3', '10.0.0.1', mode='1024x10')  # OS1 sensor IP, destination IP, and resolution
# Inform the sensor of the destination host and reintialize it
os1.start()
# Start the loop which will handle and dispatch each packet to the handler
# function for processing
os1.run_forever(handler)
```

> You can run the server as threaded with `os1.run_forever(handler, threaded=True)`

## Recipes
Generally speed is a concern since the OS1 is sending 12,608 bytes/packet at a
rate of 1280 packets/sec (in 1024x20 or 2048x10 mode).
So a multiprocessing producer consumer model works well.
```python
import json
from multiprocessing import Process, Queue

from os1 import OS1
from os1.utils import build_trig_table, xyz_points


OS1_IP = '10.0.0.3'
HOST_IP = '10.0.0.2'
unprocessed_packets = Queue()


def handler(packet):
    unprocessed_packets.put(packet)
    
    
def worker(queue, beam_altitude_angles, beam_azimuth_angles) :
    build_trig_table(beam_altitude_angles, beam_azimuth_angles)
    while True:
        packet = queue.get()
        coords = xyz_points(packet) 
        # do work...


def spawn_workers(n, worker, *args, **kwargs):
    processes = []
    for i in range(n):
        process = Process(
            target=worker,
            args=args,
            kwargs=kwargs
        )
        process.start()
        processes.append(process)
    return processes
    
    
os1 = OS1(OS1_IP, HOST_IP)
beam_intrinsics = json.loads(os1.get_beam_intrinsics())
beam_alt_angles = beam_intrinsics['beam_altitude_angles']
beam_az_angles = beam_intrinsics['beam_azimuth_angles']
workers = spawn_workers(4, worker, unprocessed_packets, beam_alt_angles, beam_az_angles)
os1.start()
try:
    os1.run_forever(handler)
except KeyboardInterrupt:
    for w in workers:
        w.terminate()
```

## TCP API Commands

The TCP API commands can be accessed through an instance of the `OS1` object.

The following methods are supported:

* `get_config_txt`
* `get_sensor_info`
* `get_beam_intrinsics`
* `get_imu_intrinsics`
* `get_lidar_intrinsics`
* `get_config_param` - Supports querying active and staged parameters. Example: `os1.get_config_param('active', 'udp_ip')`
* `set_config_param` - Supports settings parameters to be staged. Example: `os1.set_config_param('udp_ip', '10.0.0.1')`
* `reinitialize` - Will reinitialize the sensor and apply all staged parameters to be active.
