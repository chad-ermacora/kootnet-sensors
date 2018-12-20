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

from operations_modules import operations_logger
from operations_modules.operations_config import CreateInstalledSensors, write_installed_sensors_to_file, sensors_installed_file_location


def get_installed_sensors():
    """ Loads RAW sensors from file and returns it. """
    operations_logger.primary_logger.debug("Loading Installed Sensors and Returning")

    if os.path.isfile(sensors_installed_file_location):
        try:
            sensor_list_file = open(sensors_installed_file_location, 'r')
            raw_installed_sensor_file = sensor_list_file.readlines()
            sensor_list_file.close()
        except Exception as error:
            operations_logger.primary_logger.error("Unable to open installed_sensors.conf: " + str(error))
            raw_installed_sensor_file = []
    else:
        operations_logger.primary_logger.error("Installed Sensors file not found, using and saving default")
        raw_installed_sensor_file = []
        installed_sensors = CreateInstalledSensors()
        write_installed_sensors_to_file(installed_sensors)

    return raw_installed_sensor_file


def update_ver_a_22_8():
    operations_logger.primary_logger.warning("Upgrade: Unable to convert installed sensors file, " +
                                             "loading default installed sensors")
    new_installed_sensors = CreateInstalledSensors()
    write_installed_sensors_to_file(new_installed_sensors)
    os.system("rm -f /etc/systemd/system/SensorHTTP.service 2>/dev/null")
    os.system("rm -f /opt/kootnet-sensors/auto_start/SensorHTTP.service 2>/dev/null")


def update_ver_a_22_20():
    new_installed_sensors = CreateInstalledSensors()
    installed_sensors_file = get_installed_sensors()

    try:
        if int(installed_sensors_file[1][:1]):
            new_installed_sensors.no_sensors = False
            new_installed_sensors.linux_system = 1
    except IndexError:
        operations_logger.primary_logger.error("Invalid Sensor: " + new_installed_sensors.linux_system_name)

    try:
        if int(installed_sensors_file[2][:1]):
            new_installed_sensors.no_sensors = False
            new_installed_sensors.raspberry_pi_zero_w = 1
    except IndexError:
        operations_logger.primary_logger.error("Invalid Sensor: " + new_installed_sensors.raspberry_pi_zero_w_name)

    try:
        if int(installed_sensors_file[3][:1]):
            new_installed_sensors.no_sensors = False
            new_installed_sensors.raspberry_pi_3b_plus = 1
    except IndexError:
        operations_logger.primary_logger.error("Invalid Sensor: " + new_installed_sensors.raspberry_pi_3b_plus_name)

    try:
        if int(installed_sensors_file[4][:1]):
            new_installed_sensors.no_sensors = False
            new_installed_sensors.raspberry_pi_sense_hat = 1
            new_installed_sensors.has_acc = 1
            new_installed_sensors.has_mag = 1
            new_installed_sensors.has_gyro = 1
    except IndexError:
        operations_logger.primary_logger.error(
            "Invalid Sensor: " + new_installed_sensors.raspberry_pi_sense_hat_name)

    try:
        if int(installed_sensors_file[5][:1]):
            new_installed_sensors.no_sensors = False
            new_installed_sensors.pimoroni_bh1745 = 1
    except IndexError:
        operations_logger.primary_logger.error("Invalid Sensor: " + new_installed_sensors.pimoroni_bh1745_name)

    try:
        if int(installed_sensors_file[6][:1]):
            new_installed_sensors.no_sensors = False
            new_installed_sensors.pimoroni_bme680 = 1
    except IndexError:
        operations_logger.primary_logger.error("Invalid Sensor: " + new_installed_sensors.pimoroni_bme680_name)

    try:
        if int(installed_sensors_file[7][:1]):
            new_installed_sensors.no_sensors = False
            new_installed_sensors.pimoroni_enviro = 1
            new_installed_sensors.has_acc = 1
            new_installed_sensors.has_mag = 1
    except IndexError:
        operations_logger.primary_logger.error("Invalid Sensor: " + new_installed_sensors.pimoroni_enviro_name)

    try:
        if int(installed_sensors_file[8][:1]):
            new_installed_sensors.no_sensors = False
            new_installed_sensors.pimoroni_lsm303d = 1
            new_installed_sensors.has_acc = 1
            new_installed_sensors.has_mag = 1
    except IndexError:
        operations_logger.primary_logger.error("Invalid Sensor: " + new_installed_sensors.pimoroni_lsm303d_name)

    try:
        if int(installed_sensors_file[9][:1]):
            new_installed_sensors.no_sensors = False
            new_installed_sensors.pimoroni_vl53l1x = 1
    except IndexError:
        operations_logger.primary_logger.error("Invalid Sensor: " + new_installed_sensors.pimoroni_vl53l1x_name)

    write_installed_sensors_to_file(new_installed_sensors)
