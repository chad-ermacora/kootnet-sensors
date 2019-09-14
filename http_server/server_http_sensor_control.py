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
from operations_modules import logger
from operations_modules import app_cached_variables
from operations_modules.app_generic_functions import get_http_sensor_reading


class CreateNetworkGetCommands:
    """ Create a object instance holding available network "Get" commands (AKA expecting data back). """

    def __init__(self):
        self.sensor_sql_database = "DownloadSQLDatabase"
        self.sensor_configuration = "GetConfigurationReport"
        self.sensor_configuration_file = "GetConfiguration"
        self.installed_sensors_file = "GetInstalledSensors"
        self.wifi_config_file = "GetWifiConfiguration"
        self.variance_config = "GetVarianceConfiguration"
        self.system_data = "GetSystemData"
        self.primary_log = "GetPrimaryLog"
        self.network_log = "GetNetworkLog"
        self.sensors_log = "GetSensorsLog"
        self.download_zipped_logs = "DownloadZippedLogs"
        self.sensor_readings = "GetSensorReadings"
        self.sensor_name = ""
        self.system_uptime = "GetSystemUptime"
        self.cpu_temp = "GetCPUTemperature"
        self.environmental_temp = "GetEnvTemperature"
        self.env_temp_offset = "GetTempOffsetEnv"
        self.pressure = "GetPressure"
        self.altitude = "GetAltitude"
        self.humidity = "GetHumidity"
        self.distance = "GetDistance"
        self.gas_index = "GetGasResistanceIndex"
        self.gas_oxidised = "GetGasOxidised"
        self.gas_reduced = "GetGasReduced"
        self.gas_nh3 = "GetGasNH3"
        self.pm_1 = "GetParticulateMatter1"
        self.pm_2_5 = "GetParticulateMatter2_5"
        self.pm_10 = "GetParticulateMatter10"
        self.lumen = "GetLumen"
        self.rgb = "GetEMS"
        self.ultra_violet_index = "GetUltraVioletA"
        self.ultra_violet_a = "GetUltraVioletA"
        self.ultra_violet_b = "GetUltraVioletB"
        self.accelerometer_xyz = "GetAccelerometerXYZ"
        self.magnetometer_xyz = "GetMagnetometerXYZ"
        self.gyroscope_xyz = "GetGyroscopeXYZ"
        self.database_notes = "GetDatabaseNotes"
        self.database_note_dates = "GetDatabaseNoteDates"
        self.database_user_note_dates = "GetDatabaseNoteUserDates"

    @staticmethod
    def get_command_and_replacement_text_list():
        report_variables = [["GetHostName", "{{ SensorName }}"],
                            ["GetOSVersion", "{{ OSVersion }}"],
                            ["GetSensorVersion", "{{ ProgramVersion }}"],
                            ["GetProgramLastUpdated", "{{ LastUpdated }}"],
                            ["GetSystemDateTime", "{{ SensorDateTime }}"],
                            ["GetSystemUptime", "{{ SystemUpTime }}"],
                            ["GetSQLDBSize", "{{ SQLDBSize }}"],
                            ["GetCPUTemperature", "{{ CPUTemp }}"],
                            ["GetRAMUsed", "{{ RAMUsed }}"],
                            ["GetUsedDiskSpace", "{{ FreeDiskSpace }}"]]
        return report_variables


network_commands = CreateNetworkGetCommands()

sensor_bg_names_list = ["senor_ip_1", "senor_ip_2", "senor_ip_3", "senor_ip_4", "senor_ip_5", "senor_ip_6",
                        "senor_ip_7", "senor_ip_8", "senor_ip_9", "senor_ip_10", "senor_ip_11", "senor_ip_12",
                        "senor_ip_13", "senor_ip_14", "senor_ip_15", "senor_ip_16", "senor_ip_17",
                        "senor_ip_18", "senor_ip_19", "senor_ip_20"]

html_sensor_entry_start = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Sensors System Report</title>
    <style>
        table {
            border: 3px solid white;
            border-collapse: collapse;
        }
        th {
            padding: 5px;
            text-align: center;
        }
        body {
            background-color: #000000;
            white-space: nowrap;
        }
    </style>
</head>
<body>
<h2><strong><a style="text-decoration: underline; color: red" href="/SensorControlManage">
Back to Sensor Control
</a></strong></h2>
<table>
<tr>
    <th><span style="background-color: #00ffff;">Sensor Name</span></th>
    <th><span style="background-color: #00ffff;">IP Address</span></th>
    <th><span style="background-color: #00ffff;">Sensor Date & Time</span></th>
    <th><span style="background-color: #00ffff;">System UpTime</span></th>
    <th><span style="background-color: #00ffff;">Operating System</span></th>
    <th><span style="background-color: #00ffff;">Program Version</span></th>
    <th><span style="background-color: #00ffff;">CPU Temp</span></th>
    <th><span style="background-color: #00ffff;">RAM % Used</span></th>
    <th><span style="background-color: #00ffff;">SQL DB Size / Free Disk Space</span></th>
    <th><span style="background-color: #00ffff;">Last Updated</span></th>
</tr>
<tr>
    <th style="color: grey;">-----</th>
    <th style="color: grey;">-----</th>
    <th style="color: grey;">-----</th>
    <th style="color: grey;">-----</th>
    <th style="color: grey;">-----</th>
    <th style="color: grey;">-----</th>
    <th style="color: grey;">-----</th>
    <th style="color: grey;">-----</th>
    <th style="color: grey;">-----</th>
    <th style="color: grey;">-----</th>
</tr>
"""

html_sensor_entry_end = """
</table>
<span style="color: red">
    <br>* Last Updated
    <br>  * SMB = Windows Share
    <br>  * HTTP = Online HTTP Web Server
</span>
</body>
</html>
"""

html_sensor = """
<tr>
    <th><span style="background-color: #f2f2f2;">_{{ SensorName }}_</span></th>
    <th><span style="background-color: #f2f2f2;">
        <a href='https://{{ IPAddress }}:10065/SensorInformation' target='_blank'>
            _{{ IPAddress }}_
        </a>
    </span></th>
    <th><span style="background-color: #ccffcc;">_{{ SensorDateTime }}_</span></th>
    <th><span style="background-color: #ccffcc;">_{{ SystemUpTime }}_</span></th>
    <th><span style="background-color: #f2f2f2;">_{{ OSVersion }}_</span></th>
    <th><span style="background-color: #ff66b3;">_{{ ProgramVersion }}_</span></th>
    <th><span style="background-color: #F4A460;">_{{ CPUTemp }}°C_</span></th>
    <th><span style="background-color: #F4A460;">_{{ RAMUsed }} %_</span></th>
    <th><span style="background-color: #0099ff;">_{{ SQLDBSize }} MB / {{ FreeDiskSpace }} GB_</span></th>
    <th><span style="background-color: #b3b3b3;">_{{ LastUpdated }}_</span></th>
</tr>
"""


def check_online_status(ip_address):
    sensor_return = get_http_sensor_reading(ip_address)
    if sensor_return == "OK":
        app_cached_variables.data_queue.put([ip_address, "green"])
    else:
        app_cached_variables.data_queue.put([ip_address, "red"])


def get_online_system_report(ip_address):
    sensor_report = html_sensor
    try:
        sensor_report = sensor_report.replace("{{ IPAddress }}", ip_address)
        sensor_check = get_http_sensor_reading(ip_address)
        if sensor_check == "OK":
            for command_and_replacement in network_commands.get_command_and_replacement_text_list():
                replacement_value = str(get_http_sensor_reading(ip_address, command=command_and_replacement[0]))
                sensor_report = sensor_report.replace(command_and_replacement[1], replacement_value)
            app_cached_variables.data_queue.put(sensor_report)
    except Exception as error:
        logger.network_logger.warning("Remote Sensor Report Generation Failed: " + str(error))
