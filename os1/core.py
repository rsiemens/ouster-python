import json
import socket
from functools import partial

from os1.server import RequestHandler, UDPServer, ThreadingUDPServer
from os1.utils import build_trig_table


class OS1ConfigurationError(Exception):
    pass


class OS1(object):
    def __init__(self, sensor_ip, dest_ip, udp_port=7502, tcp_port=7501):
        self.dest_host = dest_ip
        self.udp_port = udp_port
        self.api = OS1API(sensor_ip, tcp_port)
        self._server = None

    def start(self):
        self.api.set_config_param("udp_ip", self.dest_host)
        self.api.raise_for_error()

        beam_intrinsics = json.loads(self.api.get_beam_intrinsics())
        build_trig_table(
            beam_intrinsics["beam_altitude_angles"],
            beam_intrinsics["beam_azimuth_angles"],
        )

        self.api.reinitialize()
        self.api.raise_for_error()

    def run_forever(self, handler, threaded=False):
        if self._server is None:
            self._create_server(handler, threaded)
        self._server.serve_forever()

    def handle_request(self, handler):
        if self._server is None:
            self._create_server(handler, False)
        self._server.handle_request()

    def _create_server(self, handler, threaded):
        request_handler = partial(RequestHandler, handler)
        server = ThreadingUDPServer if threaded else UDPServer
        self._server = server((self.dest_host, self.udp_port), request_handler)

    def __getattr__(self, name):
        return getattr(self.api, name)


class OS1API(object):
    def __init__(self, host, port=7501):
        self.address = (host, port)
        self._error = None

    def get_config_txt(self):
        return self._send("get_config_txt")

    def get_sensor_info(self):
        return self._send("get_sensor_info")

    def get_beam_intrinsics(self):
        return self._send("get_beam_intrinsics")

    def get_imu_intrinsics(self):
        return self._send("get_imu_intrinsics")

    def get_lidar_intrinsics(self):
        return self._send("get_lidar_intrinsics")

    def get_config_param(self, *args):
        command = "get_config_param {}".format(" ".join(args))
        return self._send(command)

    def set_config_param(self, *args):
        command = "set_config_param {}".format(" ".join(args))
        return self._send(command)

    def reinitialize(self):
        return self._send("reinitialize")

    def raise_for_error(self):
        if self.has_error:
            raise OS1ConfigurationError(self._error)

    @property
    def has_error(self):
        if self._error is not None:
            return True
        return False

    def _send(self, command, *args):
        self._error = None
        payload = " ".join([command] + list(args)).encode("utf-8") + b"\n"
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect(self.address)
            sock.sendall(payload)
            response = b""
            while not response.endswith(b"\n"):
                response += sock.recv(1024)
        self._error_check(response)
        return response

    def _error_check(self, response):
        response = response.decode("utf-8")
        if response.startswith("error"):
            self._error = response
        else:
            self._error = None
