Python client for the Ouster Lidar OS-1
Compatable and tested with Firmware Version 1.5.2


This package provides a simple synchronous client for the Ouster Lidar OS-1.

> With minimal effort it should be possible to change it to be a forking or threading client.


Quick start:
```python
from os1 import OS1

def handler(raw_packet):
    """Takes each unprocessed packet and logs it to a file"""
    with open('packets.bin', 'ab') as f:
        f.write(raw_packet)


os1 = OS1(device_host, computers_host)
# Inform the device of the computer host and reintialize it
os1.start()
# start the loop which will dispatch each packet to the handler function for processing
os1.run_forever(handler)
```

The os1 module comes with a few utilities to process the raw packet into
something more meaningful to work with. `unpack` and `deserialize`.

`unpack` returns a simple flat tuple representing the packet.
`deserialize` returns a list of namedtuples representing each azimuth blocks.
```python
from os1 import OS1
from os1.packet import deserialize

def handler(raw_packet):
    """Throws away packets with bad azimuth blocks"""
    packet = deserialize(raw_packet)
    
    for azimuth in packet:
      if not azimuth.status:  # status is 0 (bad)
        return

    # all azimuth blocks are good
    do_work(packet)


os1 = OS1(device_host, computers_host)
os1.start()
os1.run_forever(handler)
```

You can also interact with the TCP api via the `OS1` object.
```python
from os1 import OS1

os1 = OS1(device_host, computers_host)
os1.api.get_config_txt()

os1.api.set_config_param("udp_ip", some_new_host)
os1.api.get_config_param('staged', 'udp_ip')
os1.api.reinitialize()
os1.api.get_config_param('active', 'udp_ip')
```
> os1.start() automatically sets the udp_ip and reinitializes 
