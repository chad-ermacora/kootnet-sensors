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

--------------------------------------------------------------------------
DEBUG - Detailed information, typically of interest only when diagnosing problems. test
INFO - Confirmation that things are working as expected.
WARNING - An indication that something unexpected happened, or indicative of some problem in the near future
ERROR - Due to a more serious problem, the software has not been able to perform some function.
CRITICAL - A serious error, indicating that the program itself may be unable to continue running.
"""
import logging
import os
from logging.handlers import RotatingFileHandler

_log_directory = "/home/pi/KootNetSensors/logs/"
primary_log = _log_directory + "Primary_log.txt"
sensors_log = _log_directory + "Sensors_log.txt"
network_log = _log_directory + "Network_log.txt"

if not os.path.exists(os.path.dirname(_log_directory)):
    os.makedirs(os.path.dirname(_log_directory))

# Primary Log
primary_logger = logging.getLogger("PrimaryLog")
primary_logger.setLevel(logging.INFO)

formatter_operations = logging.Formatter("%(asctime)s - %(levelname)s:  %(message)s", "%Y-%m-%d %H:%M:%S")

file_handler_main = RotatingFileHandler(primary_log,
                                        maxBytes=256000,
                                        backupCount=5)
file_handler_main.setFormatter(formatter_operations)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter_operations)

primary_logger.addHandler(file_handler_main)
primary_logger.addHandler(stream_handler)

# Sensors Log
sensors_logger = logging.getLogger("SensorsLog")
sensors_logger.setLevel(logging.INFO)

formatter_sensor = logging.Formatter("%(asctime)s - %(levelname)s - %(funcName)s:  %(message)s", "%Y-%m-%d %H:%M:%S")

file_handler_sensor = RotatingFileHandler(sensors_log,
                                          maxBytes=256000,
                                          backupCount=5)
file_handler_sensor.setFormatter(formatter_sensor)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter_sensor)

sensors_logger.addHandler(file_handler_sensor)
sensors_logger.addHandler(stream_handler)

# Network Commands Log
network_logger = logging.getLogger("NetworkLog")
network_logger.setLevel(logging.INFO)

formatter_network = logging.Formatter("%(asctime)s - %(levelname)s:  %(message)s", "%Y-%m-%d %H:%M:%S")

file_handler_network = RotatingFileHandler(network_log,
                                           maxBytes=256000,
                                           backupCount=5)
file_handler_network.setFormatter(formatter_network)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter_network)

network_logger.addHandler(file_handler_network)
network_logger.addHandler(stream_handler)
