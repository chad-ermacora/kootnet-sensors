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
import time
from operations_modules import logger
from operations_modules import file_locations
from operations_modules import app_generic_functions
from operations_modules import app_cached_variables
from operations_modules.app_generic_functions import get_http_sensor_reading

sensor_bg_names_list = ["senor_ip_1", "senor_ip_2", "senor_ip_3", "senor_ip_4", "senor_ip_5", "senor_ip_6",
                        "senor_ip_7", "senor_ip_8", "senor_ip_9", "senor_ip_10", "senor_ip_11", "senor_ip_12",
                        "senor_ip_13", "senor_ip_14", "senor_ip_15", "senor_ip_16", "senor_ip_17",
                        "senor_ip_18", "senor_ip_19", "senor_ip_20"]

html_sensor_entry_start = app_generic_functions.get_file_content(file_locations.html_report_system1_start).strip()
html_sensor_entry_end = app_generic_functions.get_file_content(file_locations.html_report_system3_end).strip()
html_sensor = app_generic_functions.get_file_content(file_locations.html_report_system2_sensor).strip()


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


def check_online_status(ip_address):
    sensor_return = get_http_sensor_reading(ip_address)
    if sensor_return == "OK":
        app_cached_variables.data_queue.put([ip_address, "green"])
    else:
        app_cached_variables.data_queue.put([ip_address, "red"])


def get_online_system_report(ip_address):
    network_commands = CreateNetworkGetCommands()
    sensor_report = html_sensor
    try:
        sensor_report = sensor_report.replace("{{ IPAddress }}", ip_address)
        task_start_time = time.time()
        sensor_check = get_http_sensor_reading(ip_address)
        task_end_time = str(round(time.time() - task_start_time, 3))
        if sensor_check == "OK":
            for command_and_replacement in network_commands.get_command_and_replacement_text_list():
                replacement_value = str(get_http_sensor_reading(ip_address, command=command_and_replacement[0]))
                sensor_report = sensor_report.replace(command_and_replacement[1], replacement_value)
            sensor_report = sensor_report.replace("{{ SensorResponseTime }}", task_end_time)
            app_cached_variables.data_queue.put(sensor_report)
    except Exception as error:
        logger.network_logger.warning("Remote Sensor Report Generation Failed: " + str(error))
