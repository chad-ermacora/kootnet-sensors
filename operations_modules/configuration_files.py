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
from operations_modules import app_variables
from sensor_modules import sensor_variables


def convert_config_to_str(config):
    """ Takes configuration Object and returns it as a string. """
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
    logger.primary_logger.debug("Loading Configuration File")

    if os.path.isfile(file_locations.config_file_location):
        try:
            config_file = open(file_locations.config_file_location, "r")
            config_file_content = config_file.readlines()
            config_file.close()
            installed_config = convert_config_lines_to_obj(config_file_content)
        except Exception as error:
            installed_config = app_variables.CreateConfig()
            logger.primary_logger.error("Unable to load config file, using defaults: " + str(error))

    else:
        logger.primary_logger.error("Configuration file not found, using and saving default")
        installed_config = app_variables.CreateConfig()
        write_config_to_file(installed_config)

    return installed_config


def convert_config_lines_to_obj(config_text_file):
    """ Converts provided configuration text as a list of lines into a object and returns it. """
    new_config = app_variables.CreateConfig()
    bad_load = False

    try:
        new_config.enable_debug_logging = int(config_text_file[1].split('=')[0].strip())
    except Exception as error:
        logger.primary_logger.warning("Invalid Config - Enable Debug Logging: " + str(error))
        bad_load = True

    try:
        new_config.enable_interval_recording = int(config_text_file[2].split('=')[0].strip())
    except Exception as error:
        logger.primary_logger.warning("Invalid Config - Record Interval Sensors: " + str(error))
        bad_load = True

    try:
        new_config.enable_trigger_recording = int(config_text_file[3].split('=')[0].strip())
    except Exception as error:
        logger.primary_logger.warning("Invalid Config - Record Trigger Sensors: " + str(error))
        bad_load = True

    try:
        new_config.sleep_duration_interval = float(config_text_file[4].split('=')[0].strip())
    except Exception as error:
        logger.primary_logger.warning("Invalid Config - Seconds between Interval recordings: " + str(error))
        bad_load = True

    try:
        new_config.enable_custom_temp = int(config_text_file[5].split('=')[0].strip())
    except Exception as error:
        logger.primary_logger.warning("Invalid Config - Enable Custom Temperature Offset: " + str(error))
        bad_load = True

    try:
        new_config.temperature_offset = float(config_text_file[6].split('=')[0].strip())
    except Exception as error:
        logger.primary_logger.warning("Invalid Config - Temperature Offset: " + str(error))
        bad_load = True

    if bad_load:
        logger.primary_logger.warning("One or more bad options in main configuration file.  " +
                                      "Using defaults for bad entries and saving.")
        write_config_to_file(new_config)

    return new_config


def write_config_to_file(config):
    """ Writes provided configuration file to local disk. The provided configuration can be string or object. """
    logger.primary_logger.debug("Writing Configuration to File")
    try:
        if type(config) is str:
            new_config = config
            config = convert_config_lines_to_obj(config)
        else:
            new_config = convert_config_to_str(config)

        sensor_list_file = open(file_locations.config_file_location, 'w')
        sensor_list_file.write(new_config)
        sensor_list_file.close()

        # Save Log level with each config file save
        enable_debug = open(file_locations.debug_file_location, 'w')
        enable_debug.write(str(config.enable_debug_logging))
        enable_debug.close()

    except Exception as error:
        logger.primary_logger.error("Unable to open config file: " + str(error))


def get_installed_sensors_from_file():
    """ Loads installed sensors from file and returns it as an object. """
    logger.primary_logger.debug("Loading Installed Sensors and Returning")

    if os.path.isfile(file_locations.sensors_installed_file_location):
        try:
            sensor_list_file = open(file_locations.sensors_installed_file_location, 'r')
            installed_sensor_lines = sensor_list_file.readlines()
            sensor_list_file.close()
            installed_sensors = convert_installed_sensors_lines_to_obj(installed_sensor_lines)
        except Exception as error:
            logger.primary_logger.error("Unable to open installed_sensors.conf: " + str(error))
            installed_sensors = sensor_variables.CreateInstalledSensors()
    else:
        logger.primary_logger.error("Installed Sensors file not found, using and saving default")
        installed_sensors = sensor_variables.CreateInstalledSensors()
        write_installed_sensors_to_file(installed_sensors)

    return installed_sensors


def convert_installed_sensors_lines_to_obj(installed_sensor_lines):
    """ Converts provided installed sensors text as a list of lines into a object and returns it. """
    new_installed_sensors = sensor_variables.CreateInstalledSensors()
    bad_load = False

    try:
        if int(installed_sensor_lines[1][:1]):
            new_installed_sensors.linux_system = 1
        else:
            new_installed_sensors.linux_system = 0
    except IndexError:
        logger.primary_logger.error("Invalid Sensor: " + new_installed_sensors.linux_system_name)
        bad_load = True

    try:
        if int(installed_sensor_lines[2][:1]):
            new_installed_sensors.no_sensors = False
            new_installed_sensors.raspberry_pi_zero_w = 1
    except IndexError:
        logger.primary_logger.error("Invalid Sensor: " + new_installed_sensors.raspberry_pi_zero_w_name)
        bad_load = True

    try:
        if int(installed_sensor_lines[3][:1]):
            new_installed_sensors.no_sensors = False
            new_installed_sensors.raspberry_pi_3b_plus = 1
    except IndexError:
        logger.primary_logger.error("Invalid Sensor: " + new_installed_sensors.raspberry_pi_3b_plus_name)
        bad_load = True

    try:
        if int(installed_sensor_lines[4][:1]):
            new_installed_sensors.no_sensors = False
            new_installed_sensors.raspberry_pi_sense_hat = 1
            new_installed_sensors.has_env_temperature = 1
            new_installed_sensors.has_pressure = 1
            new_installed_sensors.has_humidity = 1
            new_installed_sensors.has_acc = 1
            new_installed_sensors.has_mag = 1
            new_installed_sensors.has_gyro = 1
    except IndexError:
        logger.primary_logger.error("Invalid Sensor: " + new_installed_sensors.raspberry_pi_sense_hat_name)
        bad_load = True

    try:
        if int(installed_sensor_lines[5][:1]):
            new_installed_sensors.no_sensors = False
            new_installed_sensors.pimoroni_bh1745 = 1
            new_installed_sensors.has_lumen = 1
            new_installed_sensors.has_red = 1
            new_installed_sensors.has_green = 1
            new_installed_sensors.has_blue = 1
    except IndexError:
        logger.primary_logger.error("Invalid Sensor: " + new_installed_sensors.pimoroni_bh1745_name)
        bad_load = True

    try:
        if int(installed_sensor_lines[6][:1]):
            new_installed_sensors.no_sensors = False
            new_installed_sensors.pimoroni_as7262 = 1
            new_installed_sensors.has_red = 1
            new_installed_sensors.has_orange = 1
            new_installed_sensors.has_yellow = 1
            new_installed_sensors.has_green = 1
            new_installed_sensors.has_blue = 1
            new_installed_sensors.has_violet = 1
    except IndexError:
        logger.primary_logger.error("Invalid Sensor: " + new_installed_sensors.pimoroni_as7262_name)
        bad_load = True

    try:
        if int(installed_sensor_lines[7][:1]):
            new_installed_sensors.no_sensors = False
            new_installed_sensors.pimoroni_bme680 = 1
            new_installed_sensors.has_env_temperature = 1
            new_installed_sensors.has_pressure = 1
            new_installed_sensors.has_humidity = 1

    except IndexError:
        logger.primary_logger.error("Invalid Sensor: " + new_installed_sensors.pimoroni_bme680_name)
        bad_load = True

    try:
        if int(installed_sensor_lines[8][:1]):
            new_installed_sensors.no_sensors = False
            new_installed_sensors.pimoroni_enviro = 1
            new_installed_sensors.has_lumen = 1
            new_installed_sensors.has_red = 1
            new_installed_sensors.has_green = 1
            new_installed_sensors.has_blue = 1
            new_installed_sensors.has_acc = 1
            new_installed_sensors.has_mag = 1
    except IndexError:
        logger.primary_logger.error("Invalid Sensor: " + new_installed_sensors.pimoroni_enviro_name)
        bad_load = True

    try:
        if int(installed_sensor_lines[9][:1]):
            new_installed_sensors.no_sensors = False
            new_installed_sensors.pimoroni_lsm303d = 1
            new_installed_sensors.has_acc = 1
            new_installed_sensors.has_mag = 1
    except IndexError:
        logger.primary_logger.error("Invalid Sensor: " + new_installed_sensors.pimoroni_lsm303d_name)
        bad_load = True

    try:
        if int(installed_sensor_lines[10][:1]):
            new_installed_sensors.no_sensors = False
            new_installed_sensors.pimoroni_vl53l1x = 1
    except IndexError:
        logger.primary_logger.error("Invalid Sensor: " + new_installed_sensors.pimoroni_vl53l1x_name)
        bad_load = True

    try:
        if int(installed_sensor_lines[11][:1]):
            new_installed_sensors.no_sensors = False
            new_installed_sensors.pimoroni_ltr_559 = 1
            new_installed_sensors.has_lumen = 1
    except IndexError:
        logger.primary_logger.error("Invalid Sensor: " + new_installed_sensors.pimoroni_ltr_559_name)
        bad_load = True

    if bad_load:
        logger.primary_logger.warning("One or more bad options in Installed Sensors configuration file.  " +
                                      "Using defaults for bad entries and saving.")
        write_installed_sensors_to_file(new_installed_sensors)

    return new_installed_sensors


def write_installed_sensors_to_file(installed_sensors):
    """ Writes provided 'installed sensors' to local disk. The provided sensors can be string or object. """
    try:
        if type(installed_sensors) is str:
            new_installed_sensors = installed_sensors
        else:
            new_installed_sensors = installed_sensors.get_installed_sensors_config_as_str()

        installed_sensors_config_file = open(file_locations.sensors_installed_file_location, 'w')
        installed_sensors_config_file.write(new_installed_sensors)
        installed_sensors_config_file.close()

    except Exception as error:
        logger.primary_logger.error("Unable to open config file: " + str(error))
