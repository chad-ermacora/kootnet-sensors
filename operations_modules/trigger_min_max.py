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
# import os
#
# import operations_modules.operations_file_locations as file_locations
# import operations_modules.operations_logger as operations_logger


class CreateTriggerVariances:
    def __init__(self):
        self.delay_between_readings = 300.0
        self.delay_before_new_write = 0.0

        self.cpu_temperature_enabled = 0
        self.cpu_temperature_low = 0
        self.cpu_temperature_high = 100

        self.env_temperature_enabled = 0
        self.env_temperature_low = -20
        self.env_temperature_high = 60

        self.pressure_enabled = 0
        self.pressure_low = 300
        self.pressure_high = 1400

        self.humidity_enabled = 0
        self.humidity_low = 10
        self.humidity_high = 90

        self.lumen_enabled = 0
        self.lumen_low = 0
        self.lumen_high = 600

        self.red_enabled = 0
        self.red_low = 0
        self.red_high = 600

        self.orange_enabled = 0
        self.orange_low = 0
        self.orange_high = 600

        self.yellow_enabled = 0
        self.yellow_low = 0
        self.yellow_high = 600

        self.green_enabled = 0
        self.green_low = 0
        self.green_high = 600

        self.blue_enabled = 0
        self.blue_low = 0
        self.blue_high = 600

        self.violet_enabled = 0
        self.violet_low = 0
        self.violet_high = 600

        self.accelerometer_enabled = 0
        self.accelerometer_low = 0
        self.accelerometer_high = 600

        self.magnetometer_enabled = 0
        self.magnetometer_low = 0
        self.magnetometer_high = 600

        self.gyroscope_enabled = 0
        self.gyroscope_low = 0
        self.gyroscope_high = 600
