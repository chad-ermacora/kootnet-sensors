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


class CreateDatabaseVariables:
    """ Creates SQLite3 database variables object. """
    def __init__(self):
        self.table_interval = "IntervalData"
        self.table_trigger = "TriggerData"
        self.table_other = "OtherData"

        self.other_table_column_user_date_time = "UserDateTime"
        self.other_table_column_notes = "Notes"

        self.all_tables_datetime = "DateTime"
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

    def get_sensor_columns_list(self):
        """ Returns SQL Table columns used for Interval & Trigger recording as a list. """
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
        """ Returns "Other" SQL Table columns as a list. """
        other_sql_columns = [self.other_table_column_user_date_time,
                             self.other_table_column_notes]
        return other_sql_columns


class CreateConfig:
    """ Creates object with default sensor configuration settings. """

    def __init__(self):
        self.enable_debug_logging = 0
        self.enable_interval_recording = 1
        self.enable_trigger_recording = 1
        self.sleep_duration_interval = 300.0
        self.enable_custom_temp = 0
        self.temperature_offset = 0.0


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

    def get_installed_sensors_config_as_str(self):
        new_installed_sensors_str = "Change the number in front of each line. Enable = 1 & Disable = 0\n" + \
                                    str(self.linux_system) + " = " + \
                                    self.linux_system_name + "\n" + \
                                    str(self.raspberry_pi_zero_w) + " = " + \
                                    self.raspberry_pi_zero_w_name + "\n" + \
                                    str(self.raspberry_pi_3b_plus) + " = " + \
                                    self.raspberry_pi_3b_plus_name + "\n" + \
                                    str(self.raspberry_pi_sense_hat) + " = " + \
                                    self.raspberry_pi_sense_hat_name + "\n" + \
                                    str(self.pimoroni_bh1745) + " = " + \
                                    self.pimoroni_bh1745_name + "\n" + \
                                    str(self.pimoroni_as7262) + " = " + \
                                    self.pimoroni_as7262_name + "\n" + \
                                    str(self.pimoroni_bme680) + " = " + \
                                    self.pimoroni_bme680_name + "\n" + \
                                    str(self.pimoroni_enviro) + " = " + \
                                    self.pimoroni_enviro_name + "\n" + \
                                    str(self.pimoroni_lsm303d) + " = " + \
                                    self.pimoroni_lsm303d_name + "\n" + \
                                    str(self.pimoroni_vl53l1x) + " = " + \
                                    self.pimoroni_vl53l1x_name + "\n" + \
                                    str(self.pimoroni_ltr_559) + " = " + \
                                    self.pimoroni_ltr_559_name + "\n"
        return new_installed_sensors_str

    def auto_detect_and_set_sensors(self):
        pi_version = os.system("cat /proc/device-tree/model")
        if str(pi_version)[25] == "Raspberry Pi 3 Model B Plus":
            self.linux_system = 1
            self.raspberry_pi_3b_plus = 1
        elif str(pi_version)[16] == "Raspberry Pi Zero":
            self.linux_system = 1
            self.raspberry_pi_zero_w = 1


class CreateRPZeroWTemperatureOffsets:
    def __init__(self):
        # Additional testing may be required for accuracy
        self.pimoroni_bme680 = -0.0  # Preliminary Testing
        self.pimoroni_enviro = -4.5  # Tested
        self.rp_sense_hat = -5.5  # Untested, guessing


class CreateRP3BPlusTemperatureOffsets:
    def __init__(self):
        # Additional testing may be required for accuracy
        self.pimoroni_bme680 = -2.5  # Tested when Raspberry Pi is on its side
        self.pimoroni_enviro = -6.5  # Untested, guessing
        self.rp_sense_hat = -7.0  # Preliminary testing done


class CreateUnknownTemperatureOffsets:
    def __init__(self):
        # No Offset if unknown or unselected
        self.pimoroni_bme680 = 0.0
        self.pimoroni_enviro = 0.0
        self.rp_sense_hat = 0.0


# IP and Port for Flask to start up on
flask_http_ip = ""
flask_http_port = 10065

sense_hat_show_led_message = False

trigger_pairs = 3

restart_sensor_services_command = "systemctl daemon-reload && " + \
                                  "systemctl restart SensorRecording && " + \
                                  "systemctl restart SensorCommands"

bash_commands = {"inkupg": "bash /opt/kootnet-sensors/scripts/update_programs_e-Ink.sh",
                 "UpgradeOnline": "bash /opt/kootnet-sensors/scripts/update_programs_online.sh",
                 "UpgradeSMB": "bash /opt/kootnet-sensors/scripts/update_programs_smb.sh",
                 "CleanOnline": "systemctl start SensorCleanUpgradeOnline",
                 "CleanSMB": "systemctl start SensorCleanUpgradeSMB",
                 "RebootSystem": "reboot",
                 "ShutdownSystem": "shutdown -h now",
                 "UpgradeSystemOS": "apt-get update && apt-get upgrade -y && reboot",
                 "SetPermissions": "bash /opt/kootnet-sensors/scripts/set_permissions.sh"}
