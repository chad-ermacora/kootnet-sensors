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
Logger used throughout the program. Configuration options listed below.

DEBUG - Detailed information, typically of interest only when diagnosing problems. test
INFO - Confirmation that things are working as expected.
WARNING - An indication that something unexpected happened, or indicative of some problem in the near future
ERROR - Due to a more serious problem, the software has not been able to perform some function.
CRITICAL - A serious error, indicating that the program itself may be unable to continue running.
"""
import os
import logging
from logging.handlers import RotatingFileHandler
from operations_modules import file_locations

if not os.path.exists(os.path.dirname(file_locations.log_directory)):
    os.makedirs(os.path.dirname(file_locations.log_directory))


def check_debug_logging():
    """ Check to see if debug logging is enabled and apply if necessary. """
    if os.path.isfile(file_locations.debug_file_location):
        debug_file = open(file_locations.debug_file_location, "r")
        debug = debug_file.read().strip()
        debug_file.close()

        if int(debug):
            return 1
        else:
            return 0
    else:
        enable_debug = open(file_locations.debug_file_location, 'w')
        enable_debug.write("0")
        enable_debug.close()
        return 0


def get_number_of_log_entries(log_file):
    """ Opens provided log file location and returns the amount of log entries in it. """
    log_content = open(log_file, "r")
    log_lines = log_content.readlines()
    log_content.close()

    return len(log_lines)


def get_sensor_log(log_file, max_log_lines=0):
    """ Opens provided log file location and returns its content. """
    log_content = open(log_file, "r")
    log_lines = log_content.readlines()
    log_content.close()

    if max_log_lines:
        log_lines = log_lines[-max_log_lines:]

    log_lines.reverse()

    return_log = ""
    for log in log_lines:
        return_log += log

    return return_log


def clear_primary_log():
    """ Clears all Primary Sensor Log. """
    log_content = open(file_locations.primary_log, "w")
    log_content.write("")
    log_content.close()


def clear_network_log():
    """ Clears all Network Sensor Log. """
    log_content = open(file_locations.network_log, "w")
    log_content.write("")
    log_content.close()


def clear_sensor_log():
    """ Clears all Sensor(s) Log. """
    log_content = open(file_locations.sensors_log, "w")
    log_content.write("")
    log_content.close()


# Initialize 3 Logs, Primary, Network and Sensors
primary_logger = logging.getLogger("PrimaryLog")
network_logger = logging.getLogger("NetworkLog")
sensors_logger = logging.getLogger("SensorsLog")

debug_logging = check_debug_logging()

if debug_logging:
    primary_logger.setLevel(logging.DEBUG)
    network_logger.setLevel(logging.DEBUG)
    sensors_logger.setLevel(logging.DEBUG)

else:
    primary_logger.setLevel(logging.INFO)
    network_logger.setLevel(logging.INFO)
    sensors_logger.setLevel(logging.INFO)

formatter = logging.Formatter("%(asctime)s - %(levelname)s:  %(message)s", "%Y-%m-%d %H:%M:%S")

# Setup Primary Log
file_handler_main = RotatingFileHandler(file_locations.primary_log,
                                        maxBytes=256000,
                                        backupCount=5)
file_handler_main.setFormatter(formatter)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

primary_logger.addHandler(file_handler_main)
primary_logger.addHandler(stream_handler)

# Setup Network Log
file_handler_network = RotatingFileHandler(file_locations.network_log,
                                           maxBytes=256000,
                                           backupCount=5)
file_handler_network.setFormatter(formatter)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

network_logger.addHandler(file_handler_network)
network_logger.addHandler(stream_handler)

# Setup Sensors Log
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(funcName)s:  %(message)s", "%Y-%m-%d %H:%M:%S")

file_handler_sensor = RotatingFileHandler(file_locations.sensors_log,
                                          maxBytes=256000,
                                          backupCount=5)
file_handler_sensor.setFormatter(formatter)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

sensors_logger.addHandler(file_handler_sensor)
sensors_logger.addHandler(stream_handler)
