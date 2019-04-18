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


class CreateTriggerVariances:
    """ Create a Trigger Variance configuration object. """

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
        self.humidity_variance = 10.0
        self.humidity_wait_seconds = 600.0

        self.lumen_enabled = 1
        self.lumen_variance = 200.0
        self.lumen_wait_seconds = 600.0

        self.red_enabled = 1
        self.red_variance = 25.0
        self.red_wait_seconds = 300.0

        self.orange_enabled = 1
        self.orange_variance = 25.0
        self.orange_wait_seconds = 300.0

        self.yellow_enabled = 1
        self.yellow_variance = 25.0
        self.yellow_wait_seconds = 300.0

        self.green_enabled = 1
        self.green_variance = 25.0
        self.green_wait_seconds = 300.0

        self.blue_enabled = 1
        self.blue_variance = 25.0
        self.blue_wait_seconds = 300.0

        self.violet_enabled = 1
        self.violet_variance = 25.0
        self.violet_wait_seconds = 300.0

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


# Not used yet, considering high low variances
class CreateTriggerLowHighVariances:
    def __init__(self):
        self.delay_between_readings = 300.0
        self.delay_before_new_write = 0.0

        self.cpu_temperature_enabled = 0
        self.cpu_temperature_low = 0
        self.cpu_temperature_high = 100

        self.env_temperature_enabled = 0
        self.env_temperature_low = -20
        self.env_temperature_high = 60

        self.pressure_enabled = 0
        self.pressure_low = 300
        self.pressure_high = 1400

        self.humidity_enabled = 0
        self.humidity_low = 10
        self.humidity_high = 90

        self.lumen_enabled = 0
        self.lumen_low = 0
        self.lumen_high = 600

        self.red_enabled = 0
        self.red_low = 0
        self.red_high = 600

        self.orange_enabled = 0
        self.orange_low = 0
        self.orange_high = 600

        self.yellow_enabled = 0
        self.yellow_low = 0
        self.yellow_high = 600

        self.green_enabled = 0
        self.green_low = 0
        self.green_high = 600

        self.blue_enabled = 0
        self.blue_low = 0
        self.blue_high = 600

        self.violet_enabled = 0
        self.violet_low = 0
        self.violet_high = 600

        self.accelerometer_enabled = 0
        self.accelerometer_low = 0
        self.accelerometer_high = 600

        self.magnetometer_enabled = 0
        self.magnetometer_low = 0
        self.magnetometer_high = 600

        self.gyroscope_enabled = 0
        self.gyroscope_low = 0
        self.gyroscope_high = 600


def convert_triggers_to_str(triggers):
    """ Returns trigger variances as text to write to the local disk trigger variances file. """
    triggers_file_str = "Enable or Disable & set Variance settings.  0 = Disabled, 1 = Enabled.\n" + \
                        str(triggers.sensor_uptime_enabled) + \
                        " = Enable Sensor Uptime\n" + \
                        str(triggers.sensor_uptime_wait_seconds) + \
                        " = Seconds between SQL Writes of Sensor Uptime\n\n" + \
                        str(triggers.cpu_temperature_enabled) + \
                        " = Enable CPU Temperature\n" + \
                        str(triggers.cpu_temperature_variance) + \
                        " = CPU Temperature variance\n" + \
                        str(triggers.cpu_temperature_wait_seconds) + \
                        " = Seconds between 'CPU Temperature' readings\n\n" + \
                        str(triggers.env_temperature_enabled) + \
                        " = Enable Environmental Temperature\n" + \
                        str(triggers.env_temperature_variance) + \
                        " = Environmental Temperature variance\n" + \
                        str(triggers.env_temperature_wait_seconds) + \
                        " = Seconds between 'Environmental Temperature' readings\n\n" + \
                        str(triggers.pressure_enabled) + \
                        " = Enable Pressure\n" + \
                        str(triggers.pressure_variance) + \
                        " = Pressure variance\n" + \
                        str(triggers.pressure_wait_seconds) + \
                        " = Seconds between 'Pressure' readings\n\n" + \
                        str(triggers.humidity_enabled) + \
                        " = Enable Humidity\n" + \
                        str(triggers.humidity_variance) + \
                        " = Humidity variance\n" + \
                        str(triggers.humidity_wait_seconds) + \
                        " = Seconds between 'Humidity' readings\n\n" + \
                        str(triggers.lumen_enabled) + \
                        " = Enable Lumen\n" + \
                        str(triggers.lumen_variance) + \
                        " = Lumen variance\n" + \
                        str(triggers.lumen_wait_seconds) + \
                        " = Seconds between 'Lumen' readings\n\n" + \
                        str(triggers.red_enabled) + \
                        " = Enable Red\n" + \
                        str(triggers.red_variance) + \
                        " = Red variance\n" + \
                        str(triggers.red_wait_seconds) + \
                        " = Seconds between 'Red' readings\n\n" + \
                        str(triggers.orange_enabled) + \
                        " = Enable Orange\n" + \
                        str(triggers.orange_variance) + \
                        " = Orange variance\n" + \
                        str(triggers.orange_wait_seconds) + \
                        " = Seconds between 'Orange' readings\n\n" + \
                        str(triggers.yellow_enabled) + \
                        " = Enable Yellow\n" + \
                        str(triggers.yellow_variance) + \
                        " = Yellow variance\n" + \
                        str(triggers.yellow_wait_seconds) + \
                        " = Seconds between 'Yellow' readings\n\n" + \
                        str(triggers.green_enabled) + \
                        " = Enable Green\n" + \
                        str(triggers.green_variance) + \
                        " = Green variance\n" + \
                        str(triggers.green_wait_seconds) + \
                        " = Seconds between 'Green' readings\n\n" + \
                        str(triggers.blue_enabled) + \
                        " = Enable Blue\n" + \
                        str(triggers.blue_variance) + \
                        " = Blue variance\n" + \
                        str(triggers.blue_wait_seconds) + \
                        " = Seconds between 'Blue' readings\n\n" + \
                        str(triggers.violet_enabled) + \
                        " = Enable Violet\n" + \
                        str(triggers.violet_variance) + \
                        " = Violet variance\n" + \
                        str(triggers.violet_wait_seconds) + \
                        " = Seconds between 'Violet' readings\n\n" + \
                        str(triggers.accelerometer_enabled) + \
                        " = Enable Accelerometer\n" + \
                        str(triggers.accelerometer_variance) + \
                        " = Accelerometer variance\n" + \
                        str(triggers.accelerometer_wait_seconds) + \
                        " = Seconds between 'Accelerometer' readings\n\n" + \
                        str(triggers.magnetometer_enabled) + \
                        " = Enable Magnetometer\n" + \
                        str(triggers.magnetometer_variance) + \
                        " = Magnetometer variance\n" + \
                        str(triggers.magnetometer_wait_seconds) + \
                        " = Seconds between 'Magnetometer' readings\n\n" + \
                        str(triggers.gyroscope_enabled) + \
                        " = Enable Gyroscope\n" + \
                        str(triggers.gyroscope_variance) + \
                        " = Gyroscope variance\n" + \
                        str(triggers.gyroscope_wait_seconds) + \
                        " = Seconds between 'Gyroscope' readings\n"

    return triggers_file_str


def get_triggers_variances_from_file():
    """ Loads configuration from file and returns it as a configuration object. """
    logger.primary_logger.debug("Loading Trigger Variances File")

    if os.path.isfile(file_locations.trigger_variances_file_location):
        try:
            trigger_file = open(file_locations.trigger_variances_file_location, "r")
            trigger_file_content = trigger_file.readlines()
            trigger_file.close()
            installed_trigger_variances = convert_triggers_lines_to_obj(trigger_file_content)
        except Exception as error:
            installed_trigger_variances = CreateTriggerVariances()
            logger.primary_logger.error("Unable to load config file, using defaults: " + str(error))

    else:
        logger.primary_logger.error("Configuration file not found, using and saving default")
        installed_trigger_variances = CreateTriggerVariances()
        # write_triggers_to_file(installed_trigger_variances)
        pass

    return installed_trigger_variances


def convert_triggers_lines_to_obj(trigger_text_file):
    """ Creates a Trigger Variance object with provided text from the variance configuration file. """
    new_trigger_variances = CreateTriggerVariances()
    bad_load = False

    try:
        new_trigger_variances.sensor_uptime_enabled = int(trigger_text_file[1].split('=')[0].strip())
        new_trigger_variances.sensor_uptime_wait_seconds = float(trigger_text_file[2].split('=')[0].strip())
    except Exception as error:
        logger.primary_logger.warning("Invalid Trigger - Sensor Uptime after 'X': " + str(error))
        bad_load = True

    try:
        new_trigger_variances.cpu_temperature_enabled = int(trigger_text_file[4].split('=')[0].strip())
        new_trigger_variances.cpu_temperature_variance = float(trigger_text_file[5].split('=')[0].strip())
        new_trigger_variances.cpu_temperature_wait_seconds = float(trigger_text_file[6].split('=')[0].strip())
    except Exception as error:
        logger.primary_logger.warning("Invalid Trigger - CPU Temperature/Time: " + str(error))
        bad_load = True

    try:
        new_trigger_variances.env_temperature_enabled = int(trigger_text_file[8].split('=')[0].strip())
        new_trigger_variances.env_temperature_variance = float(trigger_text_file[9].split('=')[0].strip())
        new_trigger_variances.env_temperature_wait_seconds = float(trigger_text_file[10].split('=')[0].strip())
    except Exception as error:
        logger.primary_logger.warning("Invalid Trigger - Environmental Temperature/Time: " + str(error))
        bad_load = True

    try:
        new_trigger_variances.pressure_enabled = int(trigger_text_file[12].split('=')[0].strip())
        new_trigger_variances.pressure_variance = float(trigger_text_file[13].split('=')[0].strip())
        new_trigger_variances.pressure_wait_seconds = float(trigger_text_file[14].split('=')[0].strip())
    except Exception as error:
        logger.primary_logger.warning("Invalid Trigger - Pressure/Time: " + str(error))
        bad_load = True

    try:
        new_trigger_variances.humidity_enabled = int(trigger_text_file[16].split('=')[0].strip())
        new_trigger_variances.humidity_variance = float(trigger_text_file[17].split('=')[0].strip())
        new_trigger_variances.humidity_wait_seconds = float(trigger_text_file[18].split('=')[0].strip())
    except Exception as error:
        logger.primary_logger.warning("Invalid Trigger - Humidity/Time: " + str(error))
        bad_load = True

    try:
        new_trigger_variances.lumen_enabled = int(trigger_text_file[20].split('=')[0].strip())
        new_trigger_variances.lumen_variance = float(trigger_text_file[21].split('=')[0].strip())
        new_trigger_variances.lumen_wait_seconds = float(trigger_text_file[22].split('=')[0].strip())
    except Exception as error:
        logger.primary_logger.warning("Invalid Trigger - Lumen/Time: " + str(error))
        bad_load = True

    try:
        new_trigger_variances.red_enabled = int(trigger_text_file[24].split('=')[0].strip())
        new_trigger_variances.red_variance = float(trigger_text_file[25].split('=')[0].strip())
        new_trigger_variances.red_wait_seconds = float(trigger_text_file[26].split('=')[0].strip())
    except Exception as error:
        logger.primary_logger.warning("Invalid Trigger - Red/Time: " + str(error))
        bad_load = True

    try:
        new_trigger_variances.orange_enabled = int(trigger_text_file[28].split('=')[0].strip())
        new_trigger_variances.orange_variance = float(trigger_text_file[29].split('=')[0].strip())
        new_trigger_variances.orange_wait_seconds = float(trigger_text_file[30].split('=')[0].strip())
    except Exception as error:
        logger.primary_logger.warning("Invalid Trigger - Orange/Time: " + str(error))
        bad_load = True

    try:
        new_trigger_variances.yellow_enabled = int(trigger_text_file[32].split('=')[0].strip())
        new_trigger_variances.yellow_variance = float(trigger_text_file[33].split('=')[0].strip())
        new_trigger_variances.yellow_wait_seconds = float(trigger_text_file[34].split('=')[0].strip())
    except Exception as error:
        logger.primary_logger.warning("Invalid Trigger - Yellow/Time: " + str(error))
        bad_load = True

    try:
        new_trigger_variances.green_enabled = int(trigger_text_file[36].split('=')[0].strip())
        new_trigger_variances.green_variance = float(trigger_text_file[37].split('=')[0].strip())
        new_trigger_variances.green_wait_seconds = float(trigger_text_file[38].split('=')[0].strip())
    except Exception as error:
        logger.primary_logger.warning("Invalid Trigger - Green/Time: " + str(error))
        bad_load = True

    try:
        new_trigger_variances.blue_enabled = int(trigger_text_file[40].split('=')[0].strip())
        new_trigger_variances.blue_variance = float(trigger_text_file[41].split('=')[0].strip())
        new_trigger_variances.blue_wait_seconds = float(trigger_text_file[42].split('=')[0].strip())
    except Exception as error:
        logger.primary_logger.warning("Invalid Trigger - Blue/Time: " + str(error))
        bad_load = True

    try:
        new_trigger_variances.violet_enabled = int(trigger_text_file[44].split('=')[0].strip())
        new_trigger_variances.violet_variance = float(trigger_text_file[45].split('=')[0].strip())
        new_trigger_variances.violet_wait_seconds = float(trigger_text_file[46].split('=')[0].strip())
    except Exception as error:
        logger.primary_logger.warning("Invalid Trigger - Violet/Time: " + str(error))
        bad_load = True

    try:
        new_trigger_variances.accelerometer_enabled = int(trigger_text_file[48].split('=')[0].strip())
        new_trigger_variances.accelerometer_variance = float(trigger_text_file[49].split('=')[0].strip())
        new_trigger_variances.accelerometer_wait_seconds = float(trigger_text_file[50].split('=')[0].strip())
    except Exception as error:
        logger.primary_logger.warning("Invalid Trigger - Accelerometer/Time: " + str(error))
        bad_load = True

    try:
        new_trigger_variances.magnetometer_enabled = int(trigger_text_file[52].split('=')[0].strip())
        new_trigger_variances.magnetometer_variance = float(trigger_text_file[53].split('=')[0].strip())
        new_trigger_variances.magnetometer_wait_seconds = float(trigger_text_file[54].split('=')[0].strip())
    except Exception as error:
        logger.primary_logger.warning("Invalid Trigger - Magnetometer/Time: " + str(error))
        bad_load = True

    try:
        new_trigger_variances.gyroscope_enabled = int(trigger_text_file[56].split('=')[0].strip())
        new_trigger_variances.gyroscope_variance = float(trigger_text_file[57].split('=')[0].strip())
        new_trigger_variances.gyroscope_wait_seconds = float(trigger_text_file[58].split('=')[0].strip())
    except Exception as error:
        logger.primary_logger.warning("Invalid Trigger - Gyroscope/Time: " + str(error))
        bad_load = True

    if bad_load:
        logger.primary_logger.warning("One or more bad options in Trigger Variance configuration file.  " +
                                      "Using defaults for bad entries and saving.")
        write_triggers_to_file(new_trigger_variances)

    return new_trigger_variances


def write_triggers_to_file(triggers):
    """ Writes provided trigger variances object instance or string to local disk. """
    logger.primary_logger.debug("Writing Trigger Variances to File")
    try:
        if type(triggers) is str:
            new_triggers = triggers
        else:
            new_triggers = convert_triggers_to_str(triggers)

        sensor_list_file = open(file_locations.trigger_variances_file_location, 'w')
        sensor_list_file.write(new_triggers)
        sensor_list_file.close()
    except Exception as error:
        logger.primary_logger.error("Unable to open trigger file: " + str(error))
