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


class CreateSensorCommands:
    """ Create a object instance holding available network "Get" commands (AKA expecting data back). """
    def __init__(self):
        self.sensor_name = "GetHostName"
        self.system_uptime = "GetSystemUptime"
        self.cpu_temp = "GetCPUTemperature"
        self.environmental_temp = "GetEnvTemperature"
        self.env_temp_offset = "GetTempOffsetEnv"
        self.pressure = "GetPressure"
        self.humidity = "GetHumidity"
        self.lumen = "GetLumen"
        self.electromagnetic_spectrum = "GetEMS"
        self.accelerometer_xyz = "GetAccelerometerXYZ"
        self.magnetometer_xyz = "GetMagnetometerXYZ"
        self.gyroscope_xyz = "GetGyroscopeXYZ"
        self.display_text = "DisplayText"


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


# IP and Port for Flask to start up on
flask_http_ip = ""
flask_http_port = 10065

sense_hat_show_led_message = True

trigger_pairs = 3

restart_sensor_services_command = "systemctl daemon-reload ; " + \
                                  "systemctl restart SensorRecording & " + \
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
