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


class CreateInstalledSensors:
    """
    Creates object with default installed sensors (Default = Gnu/Linux / RP only).
    Also contains human readable sensor names as text.
    """

    def __init__(self):
        self.no_sensors = True
        self.linux_system = 1
        self.raspberry_pi_zero_w = 0
        self.raspberry_pi_3b_plus = 0

        self.raspberry_pi_sense_hat = 0
        self.pimoroni_bh1745 = 0
        self.pimoroni_as7262 = 0
        self.pimoroni_bme680 = 0
        self.pimoroni_enviro = 0
        self.pimoroni_lsm303d = 0
        self.pimoroni_vl53l1x = 0
        self.pimoroni_ltr_559 = 0

        self.has_cpu_temperature = 0
        self.has_env_temperature = 0
        self.has_pressure = 0
        self.has_humidity = 0
        self.has_lumen = 0
        self.has_red = 0
        self.has_orange = 0
        self.has_yellow = 0
        self.has_green = 0
        self.has_blue = 0
        self.has_violet = 0
        self.has_acc = 0
        self.has_mag = 0
        self.has_gyro = 0

        self.linux_system_name = "Gnu/Linux - Raspbian"
        self.raspberry_pi_zero_w_name = "Raspberry Pi Zero W"
        self.raspberry_pi_3b_plus_name = "Raspberry Pi 3BPlus"

        self.raspberry_pi_sense_hat_name = "Raspberry Pi Sense HAT"
        self.pimoroni_bh1745_name = "Pimoroni BH1745"
        self.pimoroni_as7262_name = "Pimoroni AS7262"
        self.pimoroni_bme680_name = "Pimoroni BME680"
        self.pimoroni_enviro_name = "Pimoroni EnviroPHAT"
        self.pimoroni_lsm303d_name = "Pimoroni LSM303D"
        self.pimoroni_vl53l1x_name = "Pimoroni VL53L1X"
        self.pimoroni_ltr_559_name = "Pimoroni LTR-559"

    def get_installed_names_str(self):
        str_installed_sensors = ""
        if self.linux_system:
            str_installed_sensors += self.linux_system_name + " || "
        if self.raspberry_pi_zero_w:
            str_installed_sensors += self.raspberry_pi_zero_w_name + " || "
        if self.raspberry_pi_3b_plus:
            str_installed_sensors += self.raspberry_pi_3b_plus_name + " || "
        if self.raspberry_pi_sense_hat:
            str_installed_sensors += self.raspberry_pi_sense_hat_name + " || "
        if self.pimoroni_bh1745:
            str_installed_sensors += self.pimoroni_bh1745_name + " || "
        if self.pimoroni_as7262:
            str_installed_sensors += self.pimoroni_as7262_name + " || "
        if self.pimoroni_bme680:
            str_installed_sensors += self.pimoroni_bme680_name + " || "
        if self.pimoroni_enviro:
            str_installed_sensors += self.pimoroni_enviro_name + " || "
        if self.pimoroni_lsm303d:
            str_installed_sensors += self.pimoroni_lsm303d_name + " || "
        if self.pimoroni_vl53l1x:
            str_installed_sensors += self.pimoroni_vl53l1x_name + " || "
        if self.pimoroni_ltr_559:
            str_installed_sensors += self.pimoroni_ltr_559_name + " || "

        return str_installed_sensors[:-4]

    def auto_detect_and_set_sensors(self):
        pi_version = os.system("cat /proc/device-tree/model")
        if str(pi_version)[25] == "Raspberry Pi 3 Model B Plus":
            self.linux_system = 1
            self.raspberry_pi_3b_plus = 1
        elif str(pi_version)[16] == "Raspberry Pi Zero":
            self.linux_system = 1
            self.raspberry_pi_zero_w = 1


def convert_installed_sensors_to_str(installed_sensors):
    new_installed_sensors_str = "Change the number in front of each line. Enable = 1 & Disable = 0\n" + \
                                str(installed_sensors.linux_system) + " = " + \
                                installed_sensors.linux_system_name + "\n" + \
                                str(installed_sensors.raspberry_pi_zero_w) + " = " + \
                                installed_sensors.raspberry_pi_zero_w_name + "\n" + \
                                str(installed_sensors.raspberry_pi_3b_plus) + " = " + \
                                installed_sensors.raspberry_pi_3b_plus_name + "\n" + \
                                str(installed_sensors.raspberry_pi_sense_hat) + " = " + \
                                installed_sensors.raspberry_pi_sense_hat_name + "\n" + \
                                str(installed_sensors.pimoroni_bh1745) + " = " + \
                                installed_sensors.pimoroni_bh1745_name + "\n" + \
                                str(installed_sensors.pimoroni_as7262) + " = " + \
                                installed_sensors.pimoroni_as7262_name + "\n" + \
                                str(installed_sensors.pimoroni_bme680) + " = " + \
                                installed_sensors.pimoroni_bme680_name + "\n" + \
                                str(installed_sensors.pimoroni_enviro) + " = " + \
                                installed_sensors.pimoroni_enviro_name + "\n" + \
                                str(installed_sensors.pimoroni_lsm303d) + " = " + \
                                installed_sensors.pimoroni_lsm303d_name + "\n" + \
                                str(installed_sensors.pimoroni_vl53l1x) + " = " + \
                                installed_sensors.pimoroni_vl53l1x_name + "\n" + \
                                str(installed_sensors.pimoroni_ltr_559) + " = " + \
                                installed_sensors.pimoroni_ltr_559_name + "\n"
    return new_installed_sensors_str


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
            installed_sensors = CreateInstalledSensors()
    else:
        logger.primary_logger.error("Installed Sensors file not found, using and saving default")
        installed_sensors = CreateInstalledSensors()
        write_installed_sensors_to_file(installed_sensors)

    return installed_sensors


def convert_installed_sensors_lines_to_obj(installed_sensor_lines):
    new_installed_sensors = CreateInstalledSensors()
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
    """ Writes provided 'installed sensors' object to local disk. """
    try:
        if type(installed_sensors) is str:
            new_installed_sensors = installed_sensors
        else:
            new_installed_sensors = convert_installed_sensors_to_str(installed_sensors)

        installed_sensors_config_file = open(file_locations.sensors_installed_file_location, 'w')
        installed_sensors_config_file.write(new_installed_sensors)
        installed_sensors_config_file.close()

    except Exception as error:
        logger.primary_logger.error("Unable to open config file: " + str(error))
