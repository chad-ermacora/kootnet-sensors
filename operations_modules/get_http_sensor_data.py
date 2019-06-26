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
import requests
from operations_modules import logger


class CreateSensorCommands:
    """ Create a object instance holding available network "Get" commands (AKA expecting data back). """
    def __init__(self):
        self.sensor_name = "GetHostName"
        self.system_uptime = "GetSystemUptime"
        self.cpu_temp = "GetCPUTemperature"
        self.environmental_temp = "GetEnvTemperature"
        self.env_temp_offset = "GetTempOffsetEnv"
        self.pressure = "GetPressure"
        self.humidity = "GetHumidity"
        self.lumen = "GetLumen"
        self.electromagnetic_spectrum = "GetEMS"
        self.accelerometer_xyz = "GetAccelerometerXYZ"
        self.magnetometer_xyz = "GetMagnetometerXYZ"
        self.gyroscope_xyz = "GetGyroscopeXYZ"
        self.display_text = "DisplayText"


def get_sensor_reading(command):
    """ Returns requested sensor data (based on the provided command data). """
    url = "http://127.0.0.1:10065/" + command

    try:
        tmp_return_data = requests.get(url=url)
        return_data = tmp_return_data.text
        logger.primary_logger.debug("* Sensor Interval Data Retrieval OK")
    except Exception as error:
        return_data = "Sensor Offline"
        logger.primary_logger.error("* Sensor Interval Data Retrieval Failed - " + str(error))
    return return_data


def get_interval_sensor_data():
    """ Returns requested sensor data (based on the provided command data). """
    url = "http://127.0.0.1:10065/GetIntervalSensorReadings"
    command_data_separator = "[new_data_section]"

    try:
        tmp_return_data = requests.get(url=url)
        logger.primary_logger.debug("* Sensor Interval Data Retrieval OK")
        return_data = tmp_return_data.text.split(command_data_separator)
        sensor_types = str(return_data[0])
        sensor_readings = str(return_data[1])
    except Exception as error:
        sensor_types = "Sensor Offline"
        sensor_readings = "Sensor Offline"
        logger.primary_logger.error("* Sensor Interval Data Retrieval Failed - " + str(error))
    return [sensor_types, sensor_readings]


def display_text_on_sensor(text_message):
    """ Returns requested sensor data (based on the provided command data). """
    url = "http://127.0.0.1:10065/DisplayText"

    try:
        requests.put(url=url, data={'command_data': text_message})
        logger.primary_logger.debug("* Sent Command: " + url + " to Sensor OK")
    except Exception as error:
        logger.primary_logger.error("* Sensor Command Failed: " + url + " - " + str(error))
