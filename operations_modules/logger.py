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

max_log_lines_return = 150


def initialize_logger(logger, log_location, formatter):
    file_handler_main = RotatingFileHandler(log_location, maxBytes=256000, backupCount=5)
    file_handler_main.setFormatter(formatter)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler_main)
    logger.addHandler(stream_handler)


def _debug_enabled():
    if os.path.isfile(file_locations.primary_config):
        with open(file_locations.primary_config, "r") as loaded_file:
            file_lines_list = loaded_file.read().split("\n")
            if len(file_lines_list) > 1:
                debug_setting = file_lines_list[2].split("=")[0].strip()
                if int(debug_setting):
                    return True
    return False


def set_logging_level(debug_enabled=_debug_enabled()):
    if debug_enabled:
        primary_logger.setLevel(logging.DEBUG)
        network_logger.setLevel(logging.DEBUG)
        sensors_logger.setLevel(logging.DEBUG)
        mqtt_subscriber_logger.setLevel(logging.DEBUG)
    else:
        primary_logger.setLevel(logging.INFO)
        network_logger.setLevel(logging.INFO)
        sensors_logger.setLevel(logging.INFO)
        mqtt_subscriber_logger.setLevel(logging.INFO)


def get_number_of_log_entries(log_file):
    """ Opens provided log file location and returns the amount of log entries in it. """
    with open(log_file, "r") as log_content:
        log_lines = log_content.readlines()
        return len(log_lines)


def get_sensor_log(log_file, max_lines=max_log_lines_return):
    """ Opens provided log file location and returns its content. """
    try:
        with open(log_file, "r") as log_content:
            log_lines = log_content.readlines()
            if max_lines:
                log_lines = log_lines[-max_lines:]
            log_lines.reverse()

            return_log = ""
            for log in log_lines:
                return_log += log
            return return_log
    except FileNotFoundError:
        return "Log not found: " + log_file


def clear_primary_log():
    """ Clears Primary Log. """
    with open(file_locations.primary_log, "w") as log_content:
        log_content.write("")


def clear_network_log():
    """ Clears Network Log. """
    with open(file_locations.network_log, "w") as log_content:
        log_content.write("")


def clear_sensor_log():
    """ Clears Sensors Log. """
    with open(file_locations.sensors_log, "w") as log_content:
        log_content.write("")


def clear_mqtt_subscriber_log():
    """ Clears MQTT Subscriber Log. """
    with open(file_locations.mqtt_subscriber_log, "w") as log_content:
        log_content.write("")


# Initialize 3 Logs, Primary, Network and Sensors
primary_logger = logging.getLogger("PrimaryLog")
network_logger = logging.getLogger("NetworkLog")
sensors_logger = logging.getLogger("SensorsLog")
mqtt_subscriber_logger = logging.getLogger("MQTTSubscriber")

main_formatter = logging.Formatter("%(asctime)s - %(levelname)s:  %(message)s", "%Y-%m-%d %H:%M:%S")
sensor_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(funcName)s:  %(message)s", "%Y-%m-%d %H:%M:%S")
mqtt_formatter = logging.Formatter("%(asctime)s - %(message)s", "%Y-%m-%d %H:%M:%S")

initialize_logger(primary_logger, file_locations.primary_log, main_formatter)
initialize_logger(network_logger, file_locations.network_log, main_formatter)
initialize_logger(sensors_logger, file_locations.sensors_log, sensor_formatter)
initialize_logger(mqtt_subscriber_logger, file_locations.mqtt_subscriber_log, mqtt_formatter)

set_logging_level()
