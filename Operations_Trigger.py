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
import logging
from logging.handlers import RotatingFileHandler
from Operations_DB import SensorData
import sensor_modules.Linux_System as Linux_System
from sensor_modules.Linux_System import get_hostname, get_ip

logger = logging.getLogger(__name__)

logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(funcName)s:  %(message)s', '%Y-%m-%d %H:%M:%S')

file_handler = RotatingFileHandler('/home/pi/KootNetSensors/logs/Trigger_DB_log.txt', maxBytes=256000, backupCount=5)
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)

trigger_db_location = '/home/sensors/data/SensorTriggerDatabase.sqlite'


def get_rp_system_readings():
    logger.info("Retrieving Raspberry Pi System Readings")
    rp_sensor_data = SensorData()
    rp_sensor_data.sensor_types = "SensorName, IP"

    rp_sensor_data.sensor_readings = "'" + str(Linux_System.get_hostname()) + "', '" + \
        str(Linux_System.get_ip()) + "'"

    return rp_sensor_data


def get_accelerometer_xyz():
    pass


def get_magnetometer_xyz():
    pass


def get_distance():
    pass

