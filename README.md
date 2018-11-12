# Python client for the Ouster Lidar OS-1

Compatible with Firmware Version 1.6.0 and python 3
> Your milage may vary with other versions, it was tested against on a device running 1.6.0


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


os1 = OS1('10.0.0.3', '10.0.0.1')  # OS1 sensor IP and destination IP
# Inform the sensor of the destination host and reintialize it
os1.start()
# Start the loop which will handle and dispatch each packet to the handler
# function for processing
os1.run_forever(handler)
```

> You run the server as threaded with `os1.run_forever(handler, threaded=True)`

## Recipes
Generally speed is a concern since the OS1 is sending 12,608 bytes/packet at a rate of 1280 packets/sec.
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
beam_intrinsics = json.loads(os1.api.get_beam_intrinsics())
beam_alt_angles = beam_intrinsics['beam_altitude_angles']
beam_az_angles = beam_intrinsics['beam_azimuth_angles']
spawn_workers(4, worker, unprocessed_packets, beam_alt_angles, beam_az_angles)
os1.start()
os1.run_forever(handler)
```
