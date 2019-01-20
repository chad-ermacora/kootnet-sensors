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


class CreateTriggerVariances:
    def __init__(self):
        self.sensor_uptime_enabled = 1
        self.sensor_uptime_wait_seconds = 1209600.0  # Basically 4 weeks

        self.cpu_temperature_enabled = 1
        self.cpu_temperature_variance = 10.0
        self.cpu_temperature_wait_seconds = 600.0

        self.env_temperature_enabled = 1
        self.env_temperature_variance = 10.0
        self.env_temperature_wait_seconds = 600.0

        self.pressure_enabled = 1
        self.pressure_variance = 50
        self.pressure_wait_seconds = 300.0

        self.humidity_enabled = 1
        self.humidity_variance = 25.0
        self.humidity_wait_seconds = 600.0

        self.lumen_enabled = 0
        self.lumen_variance = 99999.99
        self.lumen_wait_seconds = 99999.99

        self.red_enabled = 0
        self.red_variance = 99999.99
        self.red_wait_seconds = 99999.99

        self.orange_enabled = 0
        self.orange_variance = 99999.99
        self.orange_wait_seconds = 99999.99

        self.yellow_enabled = 0
        self.yellow_variance = 99999.99
        self.yellow_wait_seconds = 99999.99

        self.green_enabled = 0
        self.green_variance = 99999.99
        self.green_wait_seconds = 99999.99

        self.blue_enabled = 0
        self.blue_variance = 99999.99
        self.blue_wait_seconds = 99999.99

        self.violet_enabled = 0
        self.violet_variance = 99999.99
        self.violet_wait_seconds = 99999.99

        self.accelerometer_enabled = 1
        self.accelerometer_variance = 99999.99
        self.accelerometer_wait_seconds = 0.15

        self.magnetometer_enabled = 1
        self.magnetometer_variance = 99999.99
        self.magnetometer_wait_seconds = 0.15

        self.gyroscope_enabled = 1
        self.gyroscope_variance = 99999.99
        self.gyroscope_wait_seconds = 0.15

    def init_trigger_variances(self, installed_sensors):
        """ Sets default values for all variances in the provided configuration object. """
        if installed_sensors.raspberry_pi_sense_hat:
            self.accelerometer_variance = 0.01
            self.magnetometer_variance = 2.0
            self.gyroscope_variance = 0.05
        if installed_sensors.pimoroni_enviro:
            self.accelerometer_variance = 0.05
            self.magnetometer_variance = 600.0
        if installed_sensors.pimoroni_lsm303d:
            self.accelerometer_variance = 0.1
            self.magnetometer_variance = 0.02


def convert_triggers_to_str(triggers):
    triggers_file_str = "Enable or Disable & set Variance settings.  0 = Disabled, 1 = Enabled.\n" + \
                        str(triggers.cpu_temperature_enabled) + \
                        " = Enable CPU Temperature\n" + \
                        str(triggers.cpu_temperature_variance) + \
                        " = CPU Temperature variance\n" + \
                        str(triggers.cpu_temperature_wait_seconds) + \
                        " = Seconds between 'CPU Temperature' readings\n" + \
                        str(triggers.env_temperature_enabled) + \
                        " = Enable Environmental Temperature\n" + \
                        str(triggers.env_temperature_variance) + \
                        " = Environmental Temperature variance\n" + \
                        str(triggers.env_temperature_wait_seconds) + \
                        " = Seconds between 'Environmental Temperature' readings\n" + \
                        str(triggers.pressure_enabled) + \
                        " = Enable Pressure\n" + \
                        str(triggers.pressure_variance) + \
                        " = Pressure variance\n" + \
                        str(triggers.pressure_wait_seconds) + \
                        " = Seconds between 'Pressure' readings\n" + \
                        str(triggers.humidity_enabled) + \
                        " = Enable Humidity\n" + \
                        str(triggers.humidity_variance) + \
                        " = Humidity variance\n" + \
                        str(triggers.humidity_wait_seconds) + \
                        " = Seconds between 'Humidity' readings\n" + \
                        str(triggers.lumen_enabled) + \
                        " = Enable Lumen\n" + \
                        str(triggers.lumen_variance) + \
                        " = Lumen variance\n" + \
                        str(triggers.lumen_wait_seconds) + \
                        " = Seconds between 'Lumen' readings\n" + \
                        str(triggers.red_enabled) + \
                        " = Enable Red\n" + \
                        str(triggers.red_variance) + \
                        " = Red variance\n" + \
                        str(triggers.red_wait_seconds) + \
                        " = Seconds between 'Red' readings\n" + \
                        str(triggers.orange_enabled) + \
                        " = Enable Orange\n" + \
                        str(triggers.orange_variance) + \
                        " = Orange variance\n" + \
                        str(triggers.orange_wait_seconds) + \
                        " = Seconds between 'Orange' readings\n" + \
                        str(triggers.yellow_enabled) + \
                        " = Enable Yellow\n" + \
                        str(triggers.yellow_variance) + \
                        " = Yellow variance\n" + \
                        str(triggers.yellow_wait_seconds) + \
                        " = Seconds between 'Yellow' readings\n" + \
                        str(triggers.green_enabled) + \
                        " = Enable Green\n" + \
                        str(triggers.green_variance) + \
                        " = Green variance\n" + \
                        str(triggers.green_wait_seconds) + \
                        " = Seconds between 'Green' readings\n" + \
                        str(triggers.blue_enabled) + \
                        " = Enable Blue\n" + \
                        str(triggers.blue_variance) + \
                        " = Blue variance\n" + \
                        str(triggers.blue_wait_seconds) + \
                        " = Seconds between 'Blue' readings\n" + \
                        str(triggers.violet_enabled) + \
                        " = Enable Violet\n" + \
                        str(triggers.violet_variance) + \
                        " = Violet variance\n" + \
                        str(triggers.violet_wait_seconds) + \
                        " = Seconds between 'Violet' readings\n" + \
                        str(triggers.accelerometer_enabled) + \
                        " = Enable Accelerometer\n" + \
                        str(triggers.accelerometer_variance) + \
                        " = Accelerometer variance\n" + \
                        str(triggers.accelerometer_wait_seconds) + \
                        " = Seconds between 'Accelerometer' readings\n" + \
                        str(triggers.magnetometer_enabled) + \
                        " = Enable Magnetometer\n" + \
                        str(triggers.magnetometer_variance) + \
                        " = Magnetometer variance\n" + \
                        str(triggers.magnetometer_wait_seconds) + \
                        " = Seconds between 'Magnetometer' readings\n" + \
                        str(triggers.gyroscope_enabled) + \
                        " = Enable Gyroscope\n" + \
                        str(triggers.gyroscope_variance) + \
                        " = Gyroscope variance\n" + \
                        str(triggers.gyroscope_wait_seconds) + \
                        " = Seconds between 'Gyroscope' readings\n"

    return triggers_file_str


def get_triggers_from_file():
    """ Loads configuration from file and returns it as a configuration object. """
    operations_logger.primary_logger.debug("Loading Trigger Variances File")

    if os.path.isfile(file_locations.trigger_variances_file_location):
        try:
            trigger_file = open(file_locations.trigger_variances_file_location, "r")
            trigger_file_content = trigger_file.readlines()
            trigger_file.close()
            installed_trigger_variances = convert_triggers_lines_to_obj(trigger_file_content)
            if len(trigger_file_content) < 5:
                write_triggers_to_file(installed_trigger_variances)
        except Exception as error:
            installed_trigger_variances = CreateTriggerVariances()
            operations_logger.primary_logger.error("Unable to load config file, using defaults: " + str(error))

    else:
        operations_logger.primary_logger.error("Configuration file not found, using and saving default")
        installed_trigger_variances = CreateTriggerVariances()
        write_triggers_to_file(installed_trigger_variances)

    return installed_trigger_variances


def convert_triggers_lines_to_obj(trigger_text_file):
    new_trigger_variances = CreateTriggerVariances()

    try:
        new_trigger_variances.sensor_name = int(trigger_text_file[1].split('=')[0].strip())
    except Exception as error:
        operations_logger.primary_logger.warning("Invalid Trigger - Sensor Name Change: " + str(error))

    try:
        new_trigger_variances.ip = int(trigger_text_file[2].split('=')[0].strip())
    except Exception as error:
        operations_logger.primary_logger.warning("Invalid Trigger - IP Change " + str(error))

    try:
        new_trigger_variances.sensor_uptime = int(trigger_text_file[3].split('=')[0].strip())
    except Exception as error:
        operations_logger.primary_logger.warning("Invalid Trigger - Sensor Uptime after 'X': " + str(error))

    try:
        new_trigger_variances.cpu_temperature = float(trigger_text_file[4].split('=')[0].split(',')[0].strip())
        new_trigger_variances.cpu_temperature_wait_seconds = float(
            trigger_text_file[4].split('=')[0].split(',')[0].strip())
    except Exception as error:
        operations_logger.primary_logger.warning("Invalid Trigger - CPU Temperature/Time: " + str(error))

    try:
        new_trigger_variances.env_temperature = float(trigger_text_file[5].split('=')[0].split(',')[0].strip())
        new_trigger_variances.env_temperature_wait_seconds = float(
            trigger_text_file[5].split('=')[0].split(',')[0].strip())
    except Exception as error:
        operations_logger.primary_logger.warning("Invalid Trigger - Environmental Temperature/Time: " + str(error))

    try:
        new_trigger_variances.pressure = float(trigger_text_file[6].split('=')[0].split(',')[0].strip())
        new_trigger_variances.pressure_wait_seconds = float(trigger_text_file[6].split('=')[0].split(',')[0].strip())
    except Exception as error:
        operations_logger.primary_logger.warning("Invalid Trigger - Pressure/Time: " + str(error))

    try:
        new_trigger_variances.humidity = float(trigger_text_file[7].split('=')[0].split(',')[0].strip())
        new_trigger_variances.humidity_wait_seconds = float(trigger_text_file[7].split('=')[0].split(',')[0].strip())
    except Exception as error:
        operations_logger.primary_logger.warning("Invalid Trigger - Humidity/Time: " + str(error))

    try:
        new_trigger_variances.lumen = float(trigger_text_file[8].split('=')[0].split(',')[0].strip())
        new_trigger_variances.lumen_wait_seconds = float(trigger_text_file[8].split('=')[0].split(',')[0].strip())
    except Exception as error:
        operations_logger.primary_logger.warning("Invalid Trigger - Lumen/Time: " + str(error))

    try:
        new_trigger_variances.red = float(trigger_text_file[9].split('=')[0].split(',')[0].strip())
        new_trigger_variances.red_wait_seconds = float(trigger_text_file[9].split('=')[0].split(',')[0].strip())
    except Exception as error:
        operations_logger.primary_logger.warning("Invalid Trigger - Red/Time: " + str(error))

    try:
        new_trigger_variances.orange = float(trigger_text_file[10].split('=')[0].split(',')[0].strip())
        new_trigger_variances.orange_wait_seconds = float(trigger_text_file[10].split('=')[0].split(',')[0].strip())
    except Exception as error:
        operations_logger.primary_logger.warning("Invalid Trigger - Orange/Time: " + str(error))

    try:
        new_trigger_variances.yellow = float(trigger_text_file[11].split('=')[0].split(',')[0].strip())
        new_trigger_variances.yellow_wait_seconds = float(trigger_text_file[11].split('=')[0].split(',')[0].strip())
    except Exception as error:
        operations_logger.primary_logger.warning("Invalid Trigger - Yellow/Time: " + str(error))

    try:
        new_trigger_variances.green = float(trigger_text_file[12].split('=')[0].split(',')[0].strip())
        new_trigger_variances.green_wait_seconds = float(trigger_text_file[12].split('=')[0].split(',')[0].strip())
    except Exception as error:
        operations_logger.primary_logger.warning("Invalid Trigger - Green/Time: " + str(error))

    try:
        new_trigger_variances.blue = float(trigger_text_file[13].split('=')[0].split(',')[0].strip())
        new_trigger_variances.blue_wait_seconds = float(trigger_text_file[13].split('=')[0].split(',')[0].strip())
    except Exception as error:
        operations_logger.primary_logger.warning("Invalid Trigger - Blue/Time: " + str(error))

    try:
        new_trigger_variances.violet = float(trigger_text_file[14].split('=')[0].split(',')[0].strip())
        new_trigger_variances.violet_wait_seconds = float(trigger_text_file[14].split('=')[0].split(',')[0].strip())
    except Exception as error:
        operations_logger.primary_logger.warning("Invalid Trigger - Violet/Time: " + str(error))

    try:
        new_trigger_variances.accelerometer = float(trigger_text_file[15].split('=')[0].split(',')[0].strip())
        new_trigger_variances.accelerometer_wait_seconds = float(
            trigger_text_file[15].split('=')[0].split(',')[0].strip())
    except Exception as error:
        operations_logger.primary_logger.warning("Invalid Trigger - Accelerometer/Time: " + str(error))

    try:
        new_trigger_variances.magnetometer = float(trigger_text_file[16].split('=')[0].split(',')[0].strip())
        new_trigger_variances.magnetometer_wait_seconds = float(
            trigger_text_file[16].split('=')[0].split(',')[0].strip())
    except Exception as error:
        operations_logger.primary_logger.warning("Invalid Trigger - Magnetometer/Time: " + str(error))

    try:
        new_trigger_variances.gyroscope = float(trigger_text_file[17].split('=')[0].split(',')[0].strip())
        new_trigger_variances.gyroscope_wait_seconds = float(trigger_text_file[17].split('=')[0].split(',')[0].strip())
    except Exception as error:
        operations_logger.primary_logger.warning("Invalid Trigger - Gyroscope/Time: " + str(error))

    return new_trigger_variances


def write_triggers_to_file(triggers):
    """ Writes provided trigger variances object instance to local disk. """
    operations_logger.primary_logger.debug("Writing Trigger Variances to File")
    try:
        new_triggers = convert_triggers_to_str(triggers)
        sensor_list_file = open(file_locations.trigger_variances_file_location, 'w')
        sensor_list_file.write(new_triggers)
        sensor_list_file.close()
    except Exception as error:
        operations_logger.primary_logger.error("Unable to open trigger file: " + str(error))
