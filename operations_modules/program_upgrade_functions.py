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
from operations_modules import config_primary
from operations_modules import config_installed_sensors
from operations_modules import config_trigger_variances


def get_installed_sensors_raw():
    """ Loads the installed sensors from file and returns it as a list of lines. """
    logger.primary_logger.debug("Loading Installed Sensors Configuration File")

    if os.path.isfile(file_locations.installed_sensors_config):
        try:
            with open(file_locations.installed_sensors_config, 'r') as sensor_list_file:
                raw_installed_sensor_file = sensor_list_file.readlines()
        except Exception as error:
            logger.primary_logger.error("Unable to open installed_sensors.conf: " + str(error))
            raw_installed_sensor_file = []
    else:
        logger.primary_logger.error("Installed Sensors file not found, using and saving default")
        raw_installed_sensor_file = []
    return raw_installed_sensor_file


def get_main_config_raw():
    """ Loads the main configuration from file and returns it as a list of lines. """
    logger.primary_logger.debug("Loading Main Configuration File")

    if os.path.isfile(file_locations.main_config):
        try:
            with open(file_locations.main_config, "r") as config_file:
                config_file_content = config_file.readlines()
        except Exception as error:
            logger.primary_logger.error("Unable to load config file, using defaults: " + str(error))
            config_file_content = []
    else:
        logger.primary_logger.error("Configuration file not found, using and saving default")
        config_file_content = []
    return config_file_content


def reset_installed_sensors():
    """ Writes a default installed sensor configuration file. """
    logger.primary_logger.warning(" **** Installed Sensors Configuration Reset ****")
    config_installed_sensors.write_to_file(config_installed_sensors.CreateInstalledSensors())


def reset_main_config():
    """ Writes a default main configuration file. """
    logger.primary_logger.warning(" **** Main Configuration Reset ****")
    default_primary_config = config_primary.CreatePrimaryConfiguration(load_from_file=False)
    default_primary_config.save_config_to_file()


def reset_variance_config():
    """ Writes a default Trigger Variance configuration file. """
    logger.primary_logger.warning(" **** Trigger Variances Configuration Reset ****")
    config_trigger_variances.write_triggers_to_file(config_trigger_variances.CreateTriggerVariances())
