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

log_directory = "/home/pi/KootNetSensors/logs/"
if not os.path.exists(os.path.dirname(log_directory)):
    os.makedirs(os.path.dirname(log_directory))

# Sensor Operations Log
operations_logger = logging.getLogger("OperationsLog")
operations_logger.setLevel(logging.INFO)

formatter = logging.Formatter("%(asctime)s - %(levelname)s:  %(message)s", "%Y-%m-%d %H:%M:%S")

file_handler_main = RotatingFileHandler(log_directory + "Operations_log.txt",
                                        maxBytes=256000,
                                        backupCount=5)
file_handler_main.setFormatter(formatter)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

operations_logger.addHandler(file_handler_main)
operations_logger.addHandler(stream_handler)

# Sensors Readings Log
sensors_logger = logging.getLogger("SensorLog")
sensors_logger.setLevel(logging.INFO)

formatter_sensor = logging.Formatter("%(asctime)s - %(levelname)s - %(funcName)s:  %(message)s", "%Y-%m-%d %H:%M:%S")

file_handler_sensor = RotatingFileHandler(log_directory + "Sensor_readings_log.txt",
                                          maxBytes=256000,
                                          backupCount=5)
file_handler_sensor.setFormatter(formatter_sensor)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter_sensor)

sensors_logger.addHandler(file_handler_sensor)
sensors_logger.addHandler(stream_handler)
