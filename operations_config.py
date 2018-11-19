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
import operations_logger

version = "Alpha.22.4"

sensors_installed_file_location = "/etc/kootnet/installed_sensors.conf"
config_file_location = "/etc/kootnet/sql_recording.conf"
last_updated_file_location = "/etc/kootnet/last_updated.txt"
sense_hat_show_led_message = False


class CreateInstalledSensors:
    """
    Creates object with default installed sensors (Default = Gnu/Linux / RP only).
    Also contains human readable sensor names as text.
    """

    def __init__(self):
        self.linux_system = 1
        self.raspberry_pi = 1
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
        self.raspberry_pi_name = "Raspberry Pi"
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
        self.acc_variance = 99999.0
        self.mag_variance = 99999.0
        self.gyro_variance = 99999.0


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
                     str(config.gyro_variance) + " = Current Gyroscope variance"

        sensor_list_file.write(new_config)
        sensor_list_file.close()

    except Exception as error:
        operations_logger.primary_logger.error("Unable to open config file - " +
                                               str(error))


def get_installed_config():
    """ Loads configuration from file and returns it as a configuration object. """
    operations_logger.primary_logger.debug("Loading Configuration File")
    installed_config = CreateConfig()

    try:
        config_file = open(config_file_location, 'r')
        config_list = config_file.readlines()
        config_file.close()
    except Exception as error:
        operations_logger.primary_logger.error("Unable to Load Config File, Creating Default: " +
                                               str(error))
        config_list = []

    try:
        installed_config.write_to_db = int(config_list[1].split('=')[0].strip())
    except Exception as error:
        operations_logger.primary_logger.error("Invalid Option in Config - " +
                                               "Record Sensors to SQL Database - " +
                                               str(error))

    try:
        installed_config.sleep_duration_interval = float(config_list[2].split('=')[0].strip())
    except Exception as error:
        operations_logger.primary_logger.error("Invalid Option in Config - " +
                                               "Duration between Interval readings in Seconds" +
                                               str(error))

    try:
        installed_config.sleep_duration_trigger = float(config_list[3].split('=')[0].strip())
        # Ensure trigger duration is not too low
        if installed_config.sleep_duration_trigger < 0.05:
            installed_config.sleep_duration_trigger = 0.05
    except Exception as error:
        operations_logger.primary_logger.error("Invalid Option in Config - " +
                                               "Duration between Trigger readings in Seconds" +
                                               str(error))

    try:
        installed_config.enable_custom = int(config_list[4].split('=')[0].strip())
    except Exception as error:
        operations_logger.primary_logger.error("Invalid Option in Config - " +
                                               "Enable Custom Settings" +
                                               str(error))

    if installed_config.enable_custom:
        try:
            installed_config.acc_variance = float(config_list[5].split('=')[0].strip())
        except Exception as error:
            operations_logger.primary_logger.error("Invalid Option in Config - " +
                                                   "Custom Accelerometer variance" +
                                                   str(error))

        try:
            installed_config.mag_variance = float(config_list[6].split('=')[0].strip())
        except Exception as error:
            operations_logger.primary_logger.error("Invalid Option in Config - " +
                                                   "Custom Magnetometer variance" +
                                                   str(error))

        try:
            installed_config.gyro_variance = float(config_list[7].split('=')[0].strip())
        except Exception as error:
            operations_logger.primary_logger.error("Invalid Option in Config - " +
                                                   "Custom Gyroscope variance" +
                                                   str(error))
    else:
        operations_logger.primary_logger.debug("Custom Settings Disabled in Config - " +
                                               "Loading Sensor Defaults based on Installed Sensors")
        installed_config = set_default_variances_per_sensor(installed_config)

    return installed_config


def write_installed_sensors_to_file(installed_sensors):
    """ Writes provided 'installed sensors' object to local disk. """
    try:
        sensor_list_file = open(sensors_installed_file_location, 'w')

        new_config = "Change the number in front of each line. Enable = 1 & Disable = 0\n" + \
                     str(installed_sensors.linux_system) + " = " + \
                     installed_sensors.linux_system_name + "\n" + \
                     str(installed_sensors.raspberry_pi) + " = " + \
                     installed_sensors.raspberry_pi_name + "\n" + \
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

        sensor_list_file.write(new_config)

    except Exception as error:
        operations_logger.primary_logger.error("Unable to open config file - " +
                                               str(error))


def get_installed_sensors():
    """ Loads installed sensors from file and returns it as an object. """
    operations_logger.primary_logger.debug("Loading Installed Sensors and Returning")
    installed_sensors = CreateInstalledSensors()

    sensor_list_file = open(sensors_installed_file_location, 'r')
    sensor_list = sensor_list_file.readlines()
    sensor_list_file.close()

    try:
        if int(sensor_list[1][:1]):
            installed_sensors.linux_system = 1
        else:
            installed_sensors.linux_system = 0
    except IndexError:
        operations_logger.primary_logger.error("Invalid Installed Sensor: " +
                                               installed_sensors.linux_system_name)

    try:
        if int(sensor_list[2][:1]):
            installed_sensors.raspberry_pi = 1
        else:
            installed_sensors.raspberry_pi = 0
    except IndexError:
        operations_logger.primary_logger.error("Invalid Installed Sensor: " +
                                               installed_sensors.raspberry_pi_name)

    try:
        if int(sensor_list[3][:1]):
            installed_sensors.raspberry_pi_sense_hat = 1
            installed_sensors.has_acc = 1
            installed_sensors.has_mag = 1
            installed_sensors.has_gyro = 1
        else:
            installed_sensors.raspberry_pi_sense_hat = 0
    except IndexError:
        operations_logger.primary_logger.error("Invalid Installed Sensor: " +
                                               installed_sensors.raspberry_pi_sense_hat_name)

    try:
        if int(sensor_list[4][:1]):
            installed_sensors.pimoroni_bh1745 = 1
        else:
            installed_sensors.pimoroni_bh1745 = 0
    except IndexError:
        operations_logger.primary_logger.error("Invalid Installed Sensor: " +
                                               installed_sensors.pimoroni_bh1745_name)

    try:
        if int(sensor_list[5][:1]):
            installed_sensors.pimoroni_bme680 = 1
        else:
            installed_sensors.pimoroni_bme680 = 0
    except IndexError:
        operations_logger.primary_logger.error("Invalid Installed Sensor: " +
                                               installed_sensors.pimoroni_bme680_name)

    try:
        if int(sensor_list[6][:1]):
            installed_sensors.pimoroni_enviro = 1
            installed_sensors.has_acc = 1
            installed_sensors.has_mag = 1
        else:
            installed_sensors.pimoroni_enviro = 0
    except IndexError:
        operations_logger.primary_logger.error("Invalid Installed Sensor: " +
                                               installed_sensors.pimoroni_enviro_name)

    try:
        if int(sensor_list[7][:1]):
            installed_sensors.pimoroni_lsm303d = 1
            installed_sensors.has_acc = 1
            installed_sensors.has_mag = 1
        else:
            installed_sensors.pimoroni_lsm303d = 0
    except IndexError:
        operations_logger.primary_logger.error("Invalid Installed Sensor: " +
                                               installed_sensors.pimoroni_lsm303d_name)

    try:
        if int(sensor_list[8][:1]):
            installed_sensors.pimoroni_vl53l1x = 1
        else:
            installed_sensors.pimoroni_vl53l1x = 0
    except IndexError:
        operations_logger.primary_logger.error("Invalid Installed Sensor: " +
                                               installed_sensors.pimoroni_vl53l1x_name)

    return installed_sensors
