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
import operations_modules.operations_logger as operations_logger
import operations_modules.operations_file_locations as file_locations


class CreateConfig:
    """ Creates object with default sensor configuration settings. """

    def __init__(self):
        self.write_to_db = 1
        self.enable_interval_recording = 1
        self.enable_trigger_recording = 1
        self.enable_custom = 0
        self.sleep_duration_interval = 300
        self.sleep_duration_trigger = 0.15

        # Remove variances when all using TriggerVariance class
        self.acc_variance = 99999.99
        self.mag_variance = 99999.99
        self.gyro_variance = 99999.99

        self.enable_custom_temp = 0
        self.temperature_offset = 0.0

    def old_config_variance_set(self, installed_sensors):
        if installed_sensors.raspberry_pi_sense_hat:
            self.acc_variance = 0.01
            self.mag_variance = 2.0
            self.gyro_variance = 0.05
        if installed_sensors.pimoroni_enviro:
            self.acc_variance = 0.05
            self.mag_variance = 600.0
        if installed_sensors.pimoroni_lsm303d:
            self.acc_variance = 0.1
            self.mag_variance = 0.02


def convert_config_to_str(config):
    config_file_str = "Enable = 1 & Disable = 0 (Recommended: Do not change if you are unsure)\n" + \
                      str(config.write_to_db) + " = Record Sensors to SQL Database\n" + \
                      str(config.sleep_duration_interval) + \
                      " = Duration between Interval recordings in Seconds\n" + \
                      str(config.sleep_duration_trigger) + \
                      " = Duration between Trigger reading checks in Seconds\n" + \
                      str(config.enable_custom) + " = Enable Custom Variances\n" + \
                      str(config.acc_variance) + " = Current Accelerometer variance\n" + \
                      str(config.mag_variance) + " = Current Magnetometer variance\n" + \
                      str(config.gyro_variance) + " = Current Gyroscope variance\n" + \
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
            if len(config_file_content) < 5:
                write_config_to_file(installed_config)
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

    try:
        new_config.write_to_db = int(config_text_file[1].split('=')[0].strip())
    except Exception as error:
        operations_logger.primary_logger.warning("Invalid Config - Record Sensors to SQL Database: " + str(error))

    try:
        new_config.sleep_duration_interval = float(config_text_file[2].split('=')[0].strip())
    except Exception as error:
        operations_logger.primary_logger.warning(
            "Invalid Config - Interval reading delay in Seconds: " + str(error))

    try:
        new_config.sleep_duration_trigger = float(config_text_file[3].split('=')[0].strip())
        # Ensure trigger duration is not too low
        if new_config.sleep_duration_trigger < 0.05:
            new_config.sleep_duration_trigger = 0.05
    except Exception as error:
        operations_logger.primary_logger.warning("Invalid Config - Trigger reading delay in Seconds: " + str(error))

    try:
        new_config.enable_custom = int(config_text_file[4].split('=')[0].strip())
    except Exception as error:
        operations_logger.primary_logger.warning("Invalid Config - Enable Custom Settings: " + str(error))

    if new_config.enable_custom:
        try:
            new_config.acc_variance = float(config_text_file[5].split('=')[0].strip())
        except Exception as error:
            operations_logger.primary_logger.warning(
                "Invalid Config - Custom Accelerometer variance: " + str(error))

        try:
            new_config.mag_variance = float(config_text_file[6].split('=')[0].strip())
        except Exception as error:
            operations_logger.primary_logger.warning("Invalid Config - Custom Magnetometer variance: " + str(error))

        try:
            new_config.gyro_variance = float(config_text_file[7].split('=')[0].strip())
        except Exception as error:
            operations_logger.primary_logger.warning("Invalid Config - Custom Gyroscope variance: " + str(error))

    try:
        new_config.custom_temperature_offset = float(config_text_file[9].split('=')[0].strip())
        if int(config_text_file[8].split('=')[0].strip()):
            new_config.enable_custom_temp = 1
    except Exception as error:
        operations_logger.primary_logger.warning("Invalid Config - Temperature Offset: " + str(error))

    return new_config


def write_config_to_file(config):
    """ Writes provided configuration file to local disk. """
    operations_logger.primary_logger.debug("Writing Configuration to File")
    try:
        new_config = convert_config_to_str(config)
        sensor_list_file = open(file_locations.config_file_location, 'w')
        sensor_list_file.write(new_config)
        sensor_list_file.close()
    except Exception as error:
        operations_logger.primary_logger.error("Unable to open config file: " + str(error))
