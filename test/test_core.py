import unittest
from unittest.mock import MagicMock, patch

from os1.core import OS1, OS1API, OS1ConfigurationError


class OS1TestCase(unittest.TestCase):
    @patch("os1.core.OS1API")
    @patch("os1.core.build_trig_table")
    def test_start(self, mock_trig_table, mock_OS1API):
        mock = MagicMock(
            get_beam_intrinsics=MagicMock(
                return_value='{"beam_altitude_angles":[], "beam_azimuth_angles":[]}'
            )
        )
        mock_OS1API.return_value = mock

        device_ip = "10.0.0.3"
        host_ip = "10.0.0.2"
        os1 = OS1(device_ip, host_ip)
        os1.start()
        mock.set_config_param.assert_called_once_with("udp_ip", host_ip)
        mock.reinitialize.assert_called_once()
