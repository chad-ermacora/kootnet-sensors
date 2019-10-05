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
from operations_modules import app_generic_functions


class CreateConfig:
    """ Creates object with default sensor configuration settings. """

    def __init__(self):
        self.enable_debug_logging = 0
        self.enable_display = 1
        self.enable_interval_recording = 1
        self.enable_trigger_recording = 0
        self.sleep_duration_interval = 300.0
        self.enable_custom_temp = 0
        self.temperature_offset = 0.0

    def get_config_as_csv(self):
        return str(self.enable_interval_recording) + "," + \
               str(self.enable_trigger_recording) + "," + \
               str(self.sleep_duration_interval) + "," + \
               str(self.enable_custom_temp) + "," + \
               str(self.temperature_offset)


def get_config_from_file():
    """ Loads configuration from file and returns it as a configuration object. """
    if os.path.isfile(file_locations.main_config):
        config_file_content = app_generic_functions.get_file_content(
            file_locations.main_config).strip().split("\n")
        installed_config = convert_config_lines_to_obj(config_file_content)
    else:
        logger.primary_logger.info("Primary Configuration file not found - Saving Default")
        installed_config = CreateConfig()
        write_config_to_file(installed_config)

    return installed_config


def convert_config_to_str(config):
    """ Takes configuration Object and returns it as a string. """
    config_file_str = "Enable = 1 & Disable = 0\n" + \
                      str(config.enable_debug_logging) + " = Enable Debug Logging\n" + \
                      str(config.enable_display) + " = Enable Mini Display\n" + \
                      str(config.enable_interval_recording) + " = Interval Recording to SQL Database\n" + \
                      str(config.enable_trigger_recording) + " = Trigger Recording to SQL Database\n" + \
                      str(config.sleep_duration_interval) + " = Recording Interval in Seconds ** Caution **\n" + \
                      str(config.enable_custom_temp) + " = Enable Custom Temperature Offset\n" + \
                      str(config.temperature_offset) + " = Current Temperature Offset"

    return config_file_str


def convert_config_lines_to_obj(config_lines, skip_write=False):
    """ Converts provided configuration text as a list of lines into a object and returns it. """
    new_config = CreateConfig()
    bad_load = False

    primary_config = []
    count = 0
    for config_line in config_lines:
        if count > 0:
            try:
                if count == 5 or count == 7:
                    primary_config.append(float(config_line.split("=")[0].strip()))
                else:
                    if config_line.strip()[0] == "1":
                        primary_config.append(1)
                    else:
                        primary_config.append(0)
            except Exception as error:
                logger.primary_logger.error("Primary Config Error on line #" + str(count) + ": " + str(error))
                bad_load = True
                if count == 5 or count == 7:
                    primary_config.append(35505.0)
                else:
                    primary_config.append(0)
        count += 1

    # 2 following values are defaulted at 1, so defaulting to 0 for loading from file
    new_config.enable_display = 0
    new_config.enable_interval_recording = 0
    count = 0
    for value in primary_config:
        if value:
            if count == 0:
                new_config.enable_debug_logging = 1
            elif count == 1:
                new_config.enable_display = 1
            elif count == 2:
                new_config.enable_interval_recording = 1
            elif count == 3:
                new_config.enable_trigger_recording = 1
            elif count == 4:
                new_config.sleep_duration_interval = value
            elif count == 5:
                new_config.enable_custom_temp = 1
            elif count == 6:
                new_config.temperature_offset = value
        count += 1

    if not skip_write:
        if bad_load:
            message = "Primary Configuration Load Error: Using one or more defaults.  Please review the Configuration."
            logger.primary_logger.warning(message)
            write_config_to_file(new_config)

    return new_config


def write_config_to_file(config):
    """ Writes provided configuration file to local disk. The provided configuration can be string or object. """
    if type(config) is str:
        new_config = config
        config = convert_config_lines_to_obj(config)
    else:
        new_config = convert_config_to_str(config)

    app_generic_functions.write_file_to_disk(file_locations.main_config, new_config)

    # Save Log level with each config file save
    app_generic_functions.write_file_to_disk(file_locations.debug_logging_config, str(config.enable_debug_logging))
