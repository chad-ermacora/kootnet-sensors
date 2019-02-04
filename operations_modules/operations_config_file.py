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

import operations_modules.operations_file_locations as file_locations
import operations_modules.operations_logger as operations_logger


class CreateConfig:
    """ Creates object with default sensor configuration settings. """

    def __init__(self):
        self.enable_debug_logging = 0
        self.enable_interval_recording = 1
        self.enable_trigger_recording = 1
        self.sleep_duration_interval = 300.0
        self.enable_custom_temp = 0
        self.temperature_offset = 0.0


def convert_config_to_str(config):
    config_file_str = "Enable = 1 & Disable = 0 (Recommended: Do not change if you are unsure)\n" + \
                      str(config.enable_debug_logging) + " = Enable Debug Logging\n" + \
                      str(config.enable_interval_recording) + " = Record Interval Sensors to SQL Database\n" + \
                      str(config.enable_trigger_recording) + " = Record Trigger Sensors to SQL Database\n" + \
                      str(config.sleep_duration_interval) + " = Seconds between Interval recordings\n" + \
                      str(config.enable_custom_temp) + " = Enable Custom Temperature Offset\n" + \
                      str(config.temperature_offset) + " = Current Temperature Offset"

    return config_file_str


def get_config_from_file():
    """ Loads configuration from file and returns it as a configuration object. """
    operations_logger.primary_logger.debug("Loading Configuration File")

    if os.path.isfile(file_locations.config_file_location):
        try:
            config_file = open(file_locations.config_file_location, "r")
            config_file_content = config_file.readlines()
            config_file.close()
            installed_config = convert_config_lines_to_obj(config_file_content)
        except Exception as error:
            installed_config = CreateConfig()
            operations_logger.primary_logger.error("Unable to load config file, using defaults: " + str(error))

    else:
        operations_logger.primary_logger.error("Configuration file not found, using and saving default")
        installed_config = CreateConfig()
        write_config_to_file(installed_config)

    return installed_config


def convert_config_lines_to_obj(config_text_file):
    new_config = CreateConfig()
    bad_load = False

    try:
        new_config.enable_debug_logging = int(config_text_file[1].split('=')[0].strip())
    except Exception as error:
        operations_logger.primary_logger.warning("Invalid Config - Enable Debug Logging: " + str(error))
        bad_load = True

    try:
        new_config.enable_interval_recording = int(config_text_file[2].split('=')[0].strip())
    except Exception as error:
        operations_logger.primary_logger.warning("Invalid Config - Record Interval Sensors: " + str(error))
        bad_load = True

    try:
        new_config.enable_trigger_recording = int(config_text_file[3].split('=')[0].strip())
    except Exception as error:
        operations_logger.primary_logger.warning("Invalid Config - Record Trigger Sensors: " + str(error))
        bad_load = True

    try:
        new_config.sleep_duration_interval = float(config_text_file[4].split('=')[0].strip())
    except Exception as error:
        operations_logger.primary_logger.warning("Invalid Config - Seconds between Interval recordings: " + str(error))
        bad_load = True

    try:
        new_config.enable_custom_temp = int(config_text_file[5].split('=')[0].strip())
    except Exception as error:
        operations_logger.primary_logger.warning("Invalid Config - Enable Custom Temperature Offset: " + str(error))
        bad_load = True

    try:
        new_config.temperature_offset = float(config_text_file[6].split('=')[0].strip())
    except Exception as error:
        operations_logger.primary_logger.warning("Invalid Config - Temperature Offset: " + str(error))
        bad_load = True

    if bad_load:
        operations_logger.primary_logger.warning("One or more bad options in main configuration file.  " +
                                                 "Using defaults for bad entries and saving.")
        write_config_to_file(new_config)

    return new_config


def write_config_to_file(config):
    """ Writes provided configuration file to local disk. """
    operations_logger.primary_logger.debug("Writing Configuration to File")
    try:
        if type(config) is str:
            new_config = config
        else:
            new_config = convert_config_to_str(config)

        sensor_list_file = open(file_locations.config_file_location, 'w')
        sensor_list_file.write(new_config)
        sensor_list_file.close()

        # Save Log level with each config file save
        operations_logger.save_log_level(str(config.enable_debug_logging))

    except Exception as error:
        operations_logger.primary_logger.error("Unable to open config file: " + str(error))
