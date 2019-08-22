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


class CreateSQLColumnsReadable:
    """ Creates an object to hold all human readable SQL column names. """

    def __init__(self):
        self.no_sensor = " || No Sensor Detected || "
        self.date_time = "Date & Time"
        self.sensor_name = "Sensor Name"
        self.ip = "IP"
        self.system_uptime = "Sensor Uptime"
        self.cpu_temp = "CPU Temperature"
        self.environmental_temp = "Env Temperature"
        self.pressure = "Pressure"
        self.altitude = "Altitude"
        self.humidity = "Humidity"
        self.distance = "Distance"
        self.gas = "Gas"
        self.particulate_matter = "Particulate Matter"
        self.lumen = "Lumen"
        self.colours = "Colours"
        self.ultra_violet = "Ultra Violet"
        self.accelerometer_xyz = "Accelerometer XYZ"
        self.magnetometer_xyz = "Magnetometer XYZ"
        self.gyroscope_xyz = "Gyroscope XYZ"


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
        self.altitude = "Altitude"
        self.humidity = "Humidity"
        self.distance = "Distance"
        self.gas_resistance_index = "Gas_Resistance_Index"
        self.gas_oxidising = "Gas_Oxidising"
        self.gas_reducing = "Gas_Reducing"
        self.gas_nh3 = "Gas_NH3"
        self.particulate_matter_1 = "Particulate_Matter_1"
        self.particulate_matter_2_5 = "Particulate_Matter_2_5"
        self.particulate_matter_10 = "Particulate_Matter_10"

        self.lumen = "Lumen"
        self.red = "Red"
        self.orange = "Orange"
        self.yellow = "Yellow"
        self.green = "Green"
        self.blue = "Blue"
        self.violet = "Violet"
        self.ultra_violet_index = "Ultra_Violet_Index"
        self.ultra_violet_a = "Ultra_Violet_A"
        self.ultra_violet_b = "Ultra_Violet_B"

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
                              self.altitude,
                              self.humidity,
                              self.distance,
                              self.gas_resistance_index,
                              self.gas_oxidising,
                              self.gas_reducing,
                              self.gas_nh3,
                              self.particulate_matter_1,
                              self.particulate_matter_2_5,
                              self.particulate_matter_10,
                              self.lumen,
                              self.red,
                              self.orange,
                              self.yellow,
                              self.green,
                              self.blue,
                              self.violet,
                              self.ultra_violet_index,
                              self.ultra_violet_a,
                              self.ultra_violet_b,
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
        self.enable_display = 1
        self.enable_interval_recording = 1
        self.enable_trigger_recording = 0
        self.sleep_duration_interval = 300.0
        self.enable_custom_temp = 0
        self.temperature_offset = 0.0


# IP and Port for Flask to start up on
flask_http_ip = ""
flask_http_port = 10065

trigger_pairs = 3

text_message_may_take_minutes = "This may take a few minutes ..."

restart_sensor_services_command = "systemctl daemon-reload ; " + \
                                  "systemctl restart KootnetSensors"

bash_commands = {"inkupg": "bash /opt/kootnet-sensors/scripts/install_update_kootnet-sensors_e-ink.sh",
                 "UpgradeOnline": "bash /opt/kootnet-sensors/scripts/install_update_kootnet-sensors_http.sh",
                 "UpgradeOnlineDEV": "bash /opt/kootnet-sensors/scripts/dev_upgrade_http.sh",
                 "UpgradeSMB": "bash /opt/kootnet-sensors/scripts/install_update_kootnet-sensors_smb.sh",
                 "UpgradeSMBDEV": "bash /opt/kootnet-sensors/scripts/dev_upgrade_smb.sh",
                 "CleanOnline": "systemctl start SensorCleanUpgradeOnline",
                 "CleanSMB": "systemctl start SensorCleanUpgradeSMB",
                 "RebootSystem": "reboot",
                 "ShutdownSystem": "shutdown -h now",
                 "UpgradeSystemOS": "bash /opt/kootnet-sensors/scripts/linux_system_os_upgrade.sh",
                 "ReInstallRequirements": "bash /opt/kootnet-sensors/scripts/reinstall_requirements.sh",
                 "SetPermissions": "bash /opt/kootnet-sensors/scripts/set_permissions.sh"}
