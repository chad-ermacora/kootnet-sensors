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

import sensor_modules.temperature_offsets
from operations_modules import operations_logger

# IP and Port for Flask to start up on
flask_http_ip = ""
flask_http_port = 10065

version = "Alpha.23.10"
sense_hat_show_led_message = False

sensor_database_location = "/home/kootnet_data/SensorRecordingDatabase.sqlite"
sensors_installed_file_location = "/etc/kootnet/installed_sensors.conf"
config_file_location = "/etc/kootnet/sql_recording.conf"
last_updated_file_location = "/etc/kootnet/last_updated.txt"
old_version_file_location = "/etc/kootnet/installed_version.txt"

trigger_pairs = 3

restart_sensor_services_command = "systemctl daemon-reload && " + \
                                  "systemctl restart SensorRecording && " + \
                                  "systemctl restart SensorCommands"

sensor_bash_commands = {"inkupg": "bash /opt/kootnet-sensors/scripts/update_programs_e-Ink.sh",
                        "UpgradeOnline": "bash /opt/kootnet-sensors/scripts/update_programs_online.sh",
                        "UpgradeSMB": "bash /opt/kootnet-sensors/scripts/update_programs_smb.sh",
                        "CleanOnline": "systemctl start SensorCleanUpgradeOnline",
                        "CleanSMB": "systemctl start SensorCleanUpgradeSMB",
                        "RebootSystem": "reboot",
                        "ShutdownSystem": "shutdown -h now",
                        "UpgradeSystemOS": "apt-get update && apt-get upgrade -y && reboot"}


class CreateDatabaseVariables:
    def __init__(self):
        self.table_interval = "IntervalData"
        self.table_trigger = "TriggerData"
        self.table_other = "OtherData"

        self.other_table_column_user_date_time = "UserDateTime"
        self.other_table_column_notes = "Notes"

        self.sensor_name = "SensorName"
        self.ip = "IP"
        self.sensor_uptime = "SensorUpTime"
        self.system_temperature = "SystemTemp"
        self.env_temperature = "EnvironmentTemp"
        self.env_temperature_offset = "EnvTempOffset"
        self.pressure = "Pressure"
        self.humidity = "Humidity"
        self.lumen = "Lumen"
        self.red = "Red"
        self.orange = "Orange"
        self.yellow = "Yellow"
        self.green = "Green"
        self.blue = "Blue"
        self.violet = "Violet"
        self.acc_x = "Acc_X"
        self.acc_y = "Acc_Y"
        self.acc_z = "Acc_Z"
        self.mag_x = "Mag_X"
        self.mag_y = "Mag_Y"
        self.mag_z = "Mag_Z"
        self.gyro_x = "Gyro_X"
        self.gyro_y = "Gyro_Y"
        self.gyro_z = "Gyro_Z"

    def get_acc_columns_str(self):
        acc_str = self.acc_x + "," + self.acc_y + "," + self.acc_z
        return acc_str

    def get_mag_columns_str(self):
        acc_str = self.mag_x + "," + self.mag_y + "," + self.mag_z
        return acc_str

    def get_gyro_columns_str(self):
        acc_str = self.gyro_x + "," + self.gyro_y + "," + self.gyro_z
        return acc_str

    def get_six_colours_columns_str(self):
        six_colours = self.red + "," + self.orange + "," + self.yellow + "," + \
                      self.green + "," + self.blue + "," + self.violet + ","
        return six_colours

    def get_rgb_columns_str(self):
        rgb = self.red + "," + self.green + "," + self.blue + ","
        return rgb

    def get_sensor_columns_list(self):
        sensor_sql_columns = [self.sensor_name,
                              self.ip,
                              self.sensor_uptime,
                              self.system_temperature,
                              self.env_temperature,
                              self.env_temperature_offset,
                              self.pressure,
                              self.humidity,
                              self.lumen,
                              self.red,
                              self.orange,
                              self.yellow,
                              self.green,
                              self.blue,
                              self.violet,
                              self.acc_x,
                              self.acc_y,
                              self.acc_z,
                              self.mag_x,
                              self.mag_y,
                              self.mag_z,
                              self.gyro_x,
                              self.gyro_y,
                              self.gyro_z]
        return sensor_sql_columns

    def get_other_columns_list(self):
        other_sql_columns = [self.other_table_column_user_date_time,
                             self.other_table_column_notes]
        return other_sql_columns


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
        config.acc_variance = 0.01
        config.mag_variance = 2.0
        config.gyro_variance = 0.05
    if installed_sensors.pimoroni_enviro:
        config.acc_variance = 0.05
        config.mag_variance = 600.0
    if installed_sensors.pimoroni_lsm303d:
        config.acc_variance = 0.1
        config.mag_variance = 0.02

    return config


def get_old_version():
    old_version_file = open(old_version_file_location, 'r')
    old_version = old_version_file.read()
    old_version_file.close()

    old_version.strip()

    return old_version


def get_installed_config():
    """ Loads configuration from file and returns it as a configuration object. """
    operations_logger.primary_logger.debug("Loading Configuration File")

    if os.path.isfile(config_file_location):
        try:
            config_file = open(config_file_location, "r")
            config_file_content = config_file.readlines()
            config_file.close()
            installed_config = config_convert_from_file(config_file_content)
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


def get_sensor_temperature_offset():
    """
     Returns sensors Environmental temperature offset based on system board and sensor.
     You can set an override in the main sensor configuration file.
    """
    installed_sensors = get_installed_sensors()
    current_config = get_installed_config()

    if installed_sensors.raspberry_pi_3b_plus:
        sensor_temp_offset = sensor_modules.temperature_offsets.CreateRP3BPlusTemperatureOffsets()
    elif installed_sensors.raspberry_pi_zero_w:
        sensor_temp_offset = sensor_modules.temperature_offsets.CreateRPZeroWTemperatureOffsets()
    else:
        # All offsets are 0.0 for unselected or unsupported system boards
        sensor_temp_offset = sensor_modules.temperature_offsets.CreateUnknownTemperatureOffsets()

    if current_config.enable_custom_temp:
        return current_config.custom_temperature_offset
    elif installed_sensors.pimoroni_enviro:
        return sensor_temp_offset.pimoroni_enviro
    elif installed_sensors.pimoroni_bme680:
        return sensor_temp_offset.pimoroni_bme680
    elif installed_sensors.raspberry_pi_sense_hat:
        return sensor_temp_offset.rp_sense_hat
    else:
        return 0.0


def config_convert_from_file(config_text_file):
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
    else:
        operations_logger.primary_logger.debug("Custom Settings Disabled in Config - Using Defaults")
        new_config = set_default_variances_per_sensor(new_config)

    try:
        new_config.custom_temperature_offset = float(config_text_file[9].split('=')[0].strip())
        if int(config_text_file[8].split('=')[0].strip()):
            new_config.enable_custom_temp = 1
    except Exception as error:
        operations_logger.primary_logger.warning("Invalid Config - Temperature Offset: " + str(error))

    return new_config


def config_convert_to_file(config):
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
                      str(config.enable_custom_temp) + " = Enable Custom Temperature Offset\n"
    if config.enable_custom_temp:
        config_file_str = config_file_str + str(config.custom_temperature_offset) + " = Current Temperature Offset"
    else:
        config_file_str = config_file_str + str(get_sensor_temperature_offset()) + " = Current Temperature Offset"

    return config_file_str


def write_config_to_file(config):
    """ Writes provided configuration file to local disk. """
    operations_logger.primary_logger.debug("Writing Configuration to File")
    try:
        new_config = config_convert_to_file(config)
        sensor_list_file = open(config_file_location, 'w')
        sensor_list_file.write(new_config)
        sensor_list_file.close()
    except Exception as error:
        operations_logger.primary_logger.error("Unable to open config file: " + str(error))


def get_installed_sensors():
    """ Loads installed sensors from file and returns it as an object. """
    operations_logger.primary_logger.debug("Loading Installed Sensors and Returning")

    if os.path.isfile(sensors_installed_file_location):
        try:
            sensor_list_file = open(sensors_installed_file_location, 'r')
            raw_installed_sensor_file = sensor_list_file.readlines()
            sensor_list_file.close()
            installed_sensors = installed_sensors_convert_from_file(raw_installed_sensor_file)
        except Exception as error:
            operations_logger.primary_logger.error("Unable to open installed_sensors.conf: " + str(error))
            installed_sensors = CreateInstalledSensors()
    else:
        operations_logger.primary_logger.error("Installed Sensors file not found, using and saving default")
        installed_sensors = CreateInstalledSensors()
        write_installed_sensors_to_file(installed_sensors)

    return installed_sensors


def installed_sensors_convert_from_file(installed_sensors_file):
    new_installed_sensors = CreateInstalledSensors()

    try:
        if int(installed_sensors_file[1][:1]):
            new_installed_sensors.linux_system = 1
        else:
            new_installed_sensors.linux_system = 0
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
        operations_logger.primary_logger.error("Invalid Sensor: " + new_installed_sensors.raspberry_pi_sense_hat_name)

    try:
        if int(installed_sensors_file[5][:1]):
            new_installed_sensors.no_sensors = False
            new_installed_sensors.pimoroni_bh1745 = 1
    except IndexError:
        operations_logger.primary_logger.error("Invalid Sensor: " + new_installed_sensors.pimoroni_bh1745_name)

    try:
        if int(installed_sensors_file[6][:1]):
            new_installed_sensors.no_sensors = False
            new_installed_sensors.pimoroni_as7262 = 1
    except IndexError:
        operations_logger.primary_logger.error("Invalid Sensor: " + new_installed_sensors.pimoroni_as7262_name)

    try:
        if int(installed_sensors_file[7][:1]):
            new_installed_sensors.no_sensors = False
            new_installed_sensors.pimoroni_bme680 = 1
    except IndexError:
        operations_logger.primary_logger.error("Invalid Sensor: " + new_installed_sensors.pimoroni_bme680_name)

    try:
        if int(installed_sensors_file[8][:1]):
            new_installed_sensors.no_sensors = False
            new_installed_sensors.pimoroni_enviro = 1
            new_installed_sensors.has_acc = 1
            new_installed_sensors.has_mag = 1
    except IndexError:
        operations_logger.primary_logger.error("Invalid Sensor: " + new_installed_sensors.pimoroni_enviro_name)

    try:
        if int(installed_sensors_file[9][:1]):
            new_installed_sensors.no_sensors = False
            new_installed_sensors.pimoroni_lsm303d = 1
            new_installed_sensors.has_acc = 1
            new_installed_sensors.has_mag = 1
    except IndexError:
        operations_logger.primary_logger.error("Invalid Sensor: " + new_installed_sensors.pimoroni_lsm303d_name)

    try:
        if int(installed_sensors_file[10][:1]):
            new_installed_sensors.no_sensors = False
            new_installed_sensors.pimoroni_vl53l1x = 1
    except IndexError:
        operations_logger.primary_logger.error("Invalid Sensor: " + new_installed_sensors.pimoroni_vl53l1x_name)

    try:
        if int(installed_sensors_file[11][:1]):
            new_installed_sensors.no_sensors = False
            new_installed_sensors.pimoroni_ltr_559 = 1
    except IndexError:
        operations_logger.primary_logger.error("Invalid Sensor: " + new_installed_sensors.pimoroni_ltr_559_name)

    return new_installed_sensors


def installed_sensors_convert_to_file(installed_sensors):
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


def write_installed_sensors_to_file(installed_sensors):
    """ Writes provided 'installed sensors' object to local disk. """
    try:
        new_config = installed_sensors_convert_to_file(installed_sensors)
        installed_sensors_config_file = open(sensors_installed_file_location, 'w')
        installed_sensors_config_file.write(new_config)
        installed_sensors_config_file.close()

    except Exception as error:
        operations_logger.primary_logger.error("Unable to open config file: " + str(error))
