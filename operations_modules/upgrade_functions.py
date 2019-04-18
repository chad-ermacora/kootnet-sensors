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
import os
from operations_modules import logger
from operations_modules import file_locations
from operations_modules import variables
from operations_modules import configuration_files


def get_installed_sensors_raw():
    """ Loads RAW sensors from file and returns it. """
    logger.primary_logger.debug("Loading Installed Sensors and Returning")

    if os.path.isfile(file_locations.sensors_installed_file_location):
        try:
            sensor_list_file = open(file_locations.sensors_installed_file_location, 'r')
            raw_installed_sensor_file = sensor_list_file.readlines()
            sensor_list_file.close()
        except Exception as error:
            logger.primary_logger.error("Unable to open installed_sensors.conf: " + str(error))
            raw_installed_sensor_file = []
    else:
        logger.primary_logger.error("Installed Sensors file not found, using and saving default")
        raw_installed_sensor_file = []

    return raw_installed_sensor_file


def get_installed_config_raw():
    """ Loads configuration from file and returns it as a configuration object. """
    logger.primary_logger.debug("Loading Configuration File")

    if os.path.isfile(file_locations.config_file_location):
        try:
            config_file = open(file_locations.config_file_location, "r")
            config_file_content = config_file.readlines()
            config_file.close()
        except Exception as error:
            logger.primary_logger.error("Unable to load config file, using defaults: " + str(error))
            config_file_content = []

    else:
        logger.primary_logger.error("Configuration file not found, using and saving default")
        config_file_content = []

    return config_file_content


def reset_installed_sensors():
    logger.primary_logger.warning("Installed Sensors Reset")
    configuration_files.write_installed_sensors_to_file(variables.CreateInstalledSensors())


def reset_config():
    logger.primary_logger.warning("Configuration Reset")
    configuration_files.write_config_to_file(variables.CreateConfig())
