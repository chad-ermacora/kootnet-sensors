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

import operations_logger
import sensor_modules.RaspberryPi_System

# IP and Port for Flask to start up on
flask_http_ip = ""
flask_http_port = 10065

version = "Alpha.22.14"
sense_hat_show_led_message = False

sensor_database_location = '/home/kootnet_data/SensorRecordingDatabase.sqlite'
sensors_installed_file_location = "/etc/kootnet/installed_sensors.conf"
config_file_location = "/etc/kootnet/sql_recording.conf"
last_updated_file_location = "/etc/kootnet/last_updated.txt"
old_version_file_location = "/etc/kootnet/installed_version.txt"

important_files = [last_updated_file_location, old_version_file_location]


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
        self.pimoroni_bme680 = 0
        self.pimoroni_enviro = 0
        self.pimoroni_lsm303d = 0
        self.pimoroni_vl53l1x = 0

        self.has_acc = 0
        self.has_mag = 0
        self.has_gyro = 0

        self.linux_system_name = "Gnu/Linux"
        self.raspberry_pi_zero_w_name = "Raspberry Pi Zero W"
        self.raspberry_pi_3b_plus_name = "Raspberry Pi 3BPlus"

        self.raspberry_pi_sense_hat_name = "RP Sense HAT"
        self.pimoroni_bh1745_name = "Pimoroni BH1745"
        self.pimoroni_bme680_name = "Pimoroni BME680"
        self.pimoroni_enviro_name = "Pimoroni EnviroPHAT"
        self.pimoroni_lsm303d_name = "Pimoroni LSM303D"
        self.pimoroni_vl53l1x_name = "Pimoroni VL53L1X"


class CreateConfig:
    """ Creates object with default sensor configuration settings. """

    def __init__(self):
        self.write_to_db = 1
        self.enable_custom = 0
        self.sleep_duration_interval = 300
        self.sleep_duration_trigger = 0.15
        self.acc_variance = 99999.99
        self.mag_variance = 99999.99
        self.gyro_variance = 99999.99

        self.enable_custom_temp = 0
        self.custom_temperature_offset = 0.0


def set_default_variances_per_sensor(config):
    """ Sets default values for all variances in the provided configuration object. """
    installed_sensors = get_installed_sensors()

    if installed_sensors.raspberry_pi_sense_hat:
        config.acc_variance = 0.5
        config.mag_variance = 2.0
        config.gyro_variance = 0.05
    if installed_sensors.pimoroni_enviro:
        config.acc_variance = 0.05
        config.mag_variance = 600.0
    if installed_sensors.pimoroni_lsm303d:
        config.acc_variance = 0.1
        config.mag_variance = 0.02

    return config


def get_default_temp_offset():
    installed_sensors = get_installed_sensors()
    if installed_sensors.raspberry_pi_3b_plus:
        offset_access = sensor_modules.RaspberryPi_System.CreateRP3BPlusTemperatureOffsets()
    elif installed_sensors.raspberry_pi_zero_w:
        offset_access = sensor_modules.RaspberryPi_System.CreateRPZeroWTemperatureOffsets()
    else:
        # Should probably create a default one instead...
        offset_access = sensor_modules.RaspberryPi_System.CreateRPZeroWTemperatureOffsets()

    if installed_sensors.raspberry_pi_sense_hat:
        return offset_access.rp_sense_hat
    elif installed_sensors.pimoroni_enviro:
        return offset_access.pimoroni_enviro
    elif installed_sensors.pimoroni_bme680:
        return offset_access.pimoroni_bme680
    else:
        return 0


def get_installed_config():
    """ Loads configuration from file and returns it as a configuration object. """
    operations_logger.primary_logger.debug("Loading Configuration File")
    installed_config = CreateConfig()

    if os.path.isfile(config_file_location):
        config_list = []

        try:
            config_file = open(config_file_location, "r")
            config_list = config_file.readlines()
            config_file.close()
            if len(config_list) < 5:
                write_config_to_file(installed_config)
        except Exception as error:
            operations_logger.primary_logger.error("Unable to load config file, using defaults: " + str(error))

        try:
            installed_config.write_to_db = int(config_list[1].split('=')[0].strip())
        except Exception as error:
            operations_logger.primary_logger.warning("Invalid Config - Record Sensors to SQL Database: " + str(error))

        try:
            installed_config.sleep_duration_interval = float(config_list[2].split('=')[0].strip())
        except Exception as error:
            operations_logger.primary_logger.warning(
                "Invalid Config - Interval reading delay in Seconds: " + str(error))

        try:
            installed_config.sleep_duration_trigger = float(config_list[3].split('=')[0].strip())
            # Ensure trigger duration is not too low
            if installed_config.sleep_duration_trigger < 0.05:
                installed_config.sleep_duration_trigger = 0.05
        except Exception as error:
            operations_logger.primary_logger.warning("Invalid Config - Trigger reading delay in Seconds: " + str(error))

        try:
            installed_config.enable_custom = int(config_list[4].split('=')[0].strip())
        except Exception as error:
            operations_logger.primary_logger.warning("Invalid Config - Enable Custom Settings: " + str(error))

        if installed_config.enable_custom:
            try:
                installed_config.acc_variance = float(config_list[5].split('=')[0].strip())
            except Exception as error:
                operations_logger.primary_logger.warning(
                    "Invalid Config - Custom Accelerometer variance: " + str(error))

            try:
                installed_config.mag_variance = float(config_list[6].split('=')[0].strip())
            except Exception as error:
                operations_logger.primary_logger.warning("Invalid Config - Custom Magnetometer variance: " + str(error))

            try:
                installed_config.gyro_variance = float(config_list[7].split('=')[0].strip())
            except Exception as error:
                operations_logger.primary_logger.warning("Invalid Config - Custom Gyroscope variance: " + str(error))
        else:
            operations_logger.primary_logger.debug("Custom Settings Disabled in Config - Using Defaults")
            installed_config = set_default_variances_per_sensor(installed_config)

        try:
            installed_config.custom_temperature_offset = float(config_list[9].split('=')[0].strip())
            if int(config_list[8].split('=')[0].strip()):
                installed_config.enable_custom_temp = 1
        except Exception as error:
            operations_logger.primary_logger.warning("Invalid Config - Temperature Offset: " + str(error))
    else:
        operations_logger.primary_logger.error("Configuration file not found, using and saving default")
        write_config_to_file(installed_config)

    return installed_config


def write_config_to_file(config):
    """ Writes provided configuration file to local disk. """
    operations_logger.primary_logger.debug("Writing Configuration to File")
    try:
        sensor_list_file = open(config_file_location, 'w')

        new_config = "Enable = 1 & Disable = 0\n" + \
                     str(config.write_to_db) + " = Record Sensors to SQL Database\n" + \
                     str(config.sleep_duration_interval) + \
                     " = Duration between Interval readings in Seconds\n" + \
                     str(config.sleep_duration_trigger) + \
                     " = Duration between Trigger readings in Seconds\n" + \
                     str(config.enable_custom) + " = Enable Custom Settings\n" + \
                     str(config.acc_variance) + " = Current Accelerometer variance\n" + \
                     str(config.mag_variance) + " = Current Magnetometer variance\n" + \
                     str(config.gyro_variance) + " = Current Gyroscope variance\n" + \
                     str(config.enable_custom_temp) + " = Enable Custom Temperature Offset\n"
        if config.enable_custom_temp:
            new_config = new_config + str(config.custom_temperature_offset) + " = Current Temperature Offset"
        else:
            new_config = new_config + str(get_default_temp_offset()) + " = Current Temperature Offset"

        sensor_list_file.write(new_config)
        sensor_list_file.close()
    except Exception as error:
        operations_logger.primary_logger.error("Unable to open config file: " + str(error))


def get_installed_sensors():
    """ Loads installed sensors from file and returns it as an object. """
    operations_logger.primary_logger.debug("Loading Installed Sensors and Returning")
    installed_sensors = CreateInstalledSensors()

    if os.path.isfile(sensors_installed_file_location):
        try:
            sensor_list_file = open(sensors_installed_file_location, 'r')
            sensor_list = sensor_list_file.readlines()
            sensor_list_file.close()
            if len(sensor_list) < 5:
                write_installed_sensors_to_file(installed_sensors)
        except Exception as error:
            sensor_list = []
            operations_logger.primary_logger.error("Unable to open installed_sensors.conf: " + str(error))

        try:
            if int(sensor_list[1][:1]):
                installed_sensors.no_sensors = False
                installed_sensors.linux_system = 1
        except IndexError:
            operations_logger.primary_logger.error("Invalid Sensor: " + installed_sensors.linux_system_name)

        try:
            if int(sensor_list[2][:1]):
                installed_sensors.no_sensors = False
                installed_sensors.raspberry_pi_zero_w = 1
        except IndexError:
            operations_logger.primary_logger.error("Invalid Sensor: " + installed_sensors.raspberry_pi_zero_w_name)

        try:
            if int(sensor_list[3][:1]):
                installed_sensors.no_sensors = False
                installed_sensors.raspberry_pi_3b_plus = 1
        except IndexError:
            operations_logger.primary_logger.error("Invalid Sensor: " + installed_sensors.raspberry_pi_3b_plus_name)

        try:
            if int(sensor_list[4][:1]):
                installed_sensors.no_sensors = False
                installed_sensors.raspberry_pi_sense_hat = 1
                installed_sensors.has_acc = 1
                installed_sensors.has_mag = 1
                installed_sensors.has_gyro = 1
        except IndexError:
            operations_logger.primary_logger.error("Invalid Sensor: " + installed_sensors.raspberry_pi_sense_hat_name)

        try:
            if int(sensor_list[5][:1]):
                installed_sensors.no_sensors = False
                installed_sensors.pimoroni_bh1745 = 1
        except IndexError:
            operations_logger.primary_logger.error("Invalid Sensor: " + installed_sensors.pimoroni_bh1745_name)

        try:
            if int(sensor_list[6][:1]):
                installed_sensors.no_sensors = False
                installed_sensors.pimoroni_bme680 = 1
        except IndexError:
            operations_logger.primary_logger.error("Invalid Sensor: " + installed_sensors.pimoroni_bme680_name)

        try:
            if int(sensor_list[7][:1]):
                installed_sensors.no_sensors = False
                installed_sensors.pimoroni_enviro = 1
                installed_sensors.has_acc = 1
                installed_sensors.has_mag = 1
        except IndexError:
            operations_logger.primary_logger.error("Invalid Sensor: " + installed_sensors.pimoroni_enviro_name)

        try:
            if int(sensor_list[8][:1]):
                installed_sensors.no_sensors = False
                installed_sensors.pimoroni_lsm303d = 1
                installed_sensors.has_acc = 1
                installed_sensors.has_mag = 1
        except IndexError:
            operations_logger.primary_logger.error("Invalid Sensor: " + installed_sensors.pimoroni_lsm303d_name)

        try:
            if int(sensor_list[9][:1]):
                installed_sensors.no_sensors = False
                installed_sensors.pimoroni_vl53l1x = 1
        except IndexError:
            operations_logger.primary_logger.error("Invalid Sensor: " + installed_sensors.pimoroni_vl53l1x_name)
    else:
        operations_logger.primary_logger.error("Installed Sensors file not found, using and saving default")
        write_installed_sensors_to_file(installed_sensors)

    return installed_sensors


def write_installed_sensors_to_file(installed_sensors):
    """ Writes provided 'installed sensors' object to local disk. """
    try:
        installed_sensors_config_file = open(sensors_installed_file_location, 'w')

        new_config = "Change the number in front of each line. Enable = 1 & Disable = 0\n" + \
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
                     str(installed_sensors.pimoroni_bme680) + " = " + \
                     installed_sensors.pimoroni_bme680_name + "\n" + \
                     str(installed_sensors.pimoroni_enviro) + " = " + \
                     installed_sensors.pimoroni_enviro_name + "\n" + \
                     str(installed_sensors.pimoroni_lsm303d) + " = " + \
                     installed_sensors.pimoroni_lsm303d_name + "\n" + \
                     str(installed_sensors.pimoroni_vl53l1x) + " = " + \
                     installed_sensors.pimoroni_vl53l1x_name + "\n"

        installed_sensors_config_file.write(new_config)
        installed_sensors_config_file.close()

    except Exception as error:
        operations_logger.primary_logger.error("Unable to open config file: " + str(error))
