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


class CreateTriggerVariances:
    def __init__(self, installed_sensors):
        self.installed_sensors = installed_sensors
        self.acc = 99999.99
        self.mag = 99999.99
        self.gyro = 99999.99

        self.sensor_name = False
        self.ip = False
        self.sensor_uptime = 99999.99
        self.cpu_temperature = 99999.99
        self.env_temperature = 99999.99
        self.pressure = 99999.99
        self.humidity = 99999.99
        self.lumen = 99999.99
        self.red = 99999.99
        self.orange = 99999.99
        self.yellow = 99999.99
        self.green = 99999.99
        self.blue = 99999.99
        self.violet = 99999.99
        self.init_trigger_variances()

    def init_trigger_variances(self):
        """ Sets default values for all variances in the provided configuration object. """
        if self.installed_sensors.raspberry_pi_sense_hat:
            self.acc = 0.01
            self.mag = 2.0
            self.gyro = 0.05
        if self.installed_sensors.pimoroni_enviro:
            self.acc = 0.05
            self.mag = 600.0
        if self.installed_sensors.pimoroni_lsm303d:
            self.acc = 0.1
            self.mag = 0.02
