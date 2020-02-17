"""
    KootNet Sensors is a collection of programs and scripts to deploy,
    interact with, and collect readings from various Sensors.
    Copyright (C) 2018  Chad Ermacora  chad.ermacora@gmail.com

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
import unittest
from . import server_http_self_diagnostics


class TestApp(unittest.TestCase):
    def test_html_get_hostname(self):
        self.assertTrue(server_http_self_diagnostics.test_html_get_hostname())

    def test_html_system_uptime(self):
        self.assertTrue(server_http_self_diagnostics.test_html_system_uptime())

    def test_html_get_cpu_temperature(self):
        self.assertTrue(server_http_self_diagnostics.test_html_get_cpu_temperature())

    def test_html_get_env_temperature(self):
        self.assertTrue(server_http_self_diagnostics.test_html_get_env_temperature())

    def test_html_get_env_temp_offset(self):
        self.assertTrue(server_http_self_diagnostics.test_html_get_env_temp_offset())

    def test_html_get_pressure(self):
        self.assertTrue(server_http_self_diagnostics.test_html_get_pressure())

    def test_html_get_altitude(self):
        self.assertTrue(server_http_self_diagnostics.test_html_get_altitude())

    def test_html_get_humidity(self):
        self.assertTrue(server_http_self_diagnostics.test_html_get_humidity())

    def test_html_get_distance(self):
        self.assertTrue(server_http_self_diagnostics.test_html_get_distance())

    def test_html_get_gas_resistance_index(self):
        self.assertTrue(server_http_self_diagnostics.test_html_get_gas_resistance_index())

    def test_html_get_gas_oxidised(self):
        self.assertTrue(server_http_self_diagnostics.test_html_get_gas_oxidised())

    def test_html_get_gas_reduced(self):
        self.assertTrue(server_http_self_diagnostics.test_html_get_gas_reduced())

    def test_html_get_gas_nh3(self):
        self.assertTrue(server_http_self_diagnostics.test_html_get_gas_nh3())

    def test_html_get_particulate_matter1(self):
        self.assertTrue(server_http_self_diagnostics.test_html_get_particulate_matter1())

    def test_html_get_particulate_matter2_5(self):
        self.assertTrue(server_http_self_diagnostics.test_html_get_particulate_matter2_5())

    def test_html_get_particulate_matter10(self):
        self.assertTrue(server_http_self_diagnostics.test_html_get_particulate_matter10())

    def test_html_get_lumen(self):
        self.assertTrue(server_http_self_diagnostics.test_html_get_lumen())

    def test_html_get_visible_ems(self):
        self.assertTrue(server_http_self_diagnostics.test_html_get_visible_ems())

    def test_html_get_uva(self):
        self.assertTrue(server_http_self_diagnostics.test_html_get_uva())

    def test_html_get_uvb(self):
        self.assertTrue(server_http_self_diagnostics.test_html_get_uvb())

    def test_html_get_accelerometer(self):
        self.assertTrue(server_http_self_diagnostics.test_html_get_accelerometer())

    def test_html_get_magnetometer(self):
        self.assertTrue(server_http_self_diagnostics.test_html_get_magnetometer())

    def test_html_get_gyroscope(self):
        self.assertTrue(server_http_self_diagnostics.test_html_get_gyroscope())

    def test_html_display_text(self):
        self.assertTrue(server_http_self_diagnostics.http_display_text_on_sensor("This is a Test Message"))


if __name__ == '__main__':
    unittest.main()
