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
from platform import system
from queue import Queue


class CreateNetworkSystemCommands:
    """ Create a object instance holding available network "System" commands (Mostly Upgrades). """

    def __init__(self):
        self.upgrade_system_os = "UpgradeSystemOS"
        self.upgrade_pip_modules = "UpdatePipModules"

        self.upgrade_http = "UpgradeOnline"
        self.upgrade_http_dev = "UpgradeOnlineDev"
        self.upgrade_http_clean = "UpgradeOnlineClean"
        self.upgrade_http_clean_dev = "UpgradeOnlineCleanDEV"

        self.upgrade_smb = "UpgradeSMB"
        self.upgrade_smb_dev = "UpgradeSMBDev"
        self.upgrade_smb_clean = "UpgradeSMBClean"
        self.upgrade_smb_clean_dev = "UpgradeSMBCleanDEV"

        self.restart_services = "RestartServices"
        self.restart_system = "RebootSystem"
        self.shutdown_system = "ShutdownSystem"


class CreateNetworkSetCommands:
    """ Create a object instance holding available network "Set" commands (AKA set configurations on remote sensor). """

    def __init__(self):
        self.set_host_name = "SetHostName"
        self.set_datetime = "SetDateTime"
        self.set_primary_configuration = "SetPrimaryConfiguration"
        self.set_installed_sensors = "SetInstalledSensors"
        self.set_variance_configuration = "SetVarianceConfiguration"
        self.set_sensor_control_configuration = "SetSensorControlConfiguration"
        self.set_weather_underground_configuration = "SetWeatherUndergroundConfiguration"
        self.set_luftdaten_configuration = "SetLuftdatenConfiguration"
        self.set_open_sense_map_configuration = "SetOpenSenseMapConfiguration"
        self.set_wifi_configuration = "SetWifiConfiguration"

        # self.put_sql_note = "PutDatabaseNote"
        # self.delete_sql_note = "DeleteDatabaseNote"
        # self.update_sql_note = "UpdateDatabaseNote"


class CreateNetworkGetCommands:
    """ Create a object instance holding available network "Get" commands (AKA get data from remote sensor). """

    def __init__(self):
        self.check_online_status = "CheckOnlineStatus"
        self.check_portal_login = "TestLogin"
        self.sensor_sql_database = "DownloadSQLDatabase"
        self.sensor_sql_database_raw = "DownloadSQLDatabaseRAW"
        self.sensor_sql_database_size = "GetSQLDBSize"
        self.sensor_zipped_sql_database_size = "GetZippedSQLDatabaseSize"
        self.sensor_configuration = "GetConfigurationReport"
        self.sensor_configuration_file = "GetConfiguration"
        self.installed_sensors_file = "GetInstalledSensors"
        self.sensor_control_configuration_file = "GetSensorControlConfiguration"
        self.wifi_config_file = "GetWifiConfiguration"
        self.variance_config = "GetVarianceConfiguration"
        self.weather_underground_config_file = "GetWeatherUndergroundConfiguration"
        self.luftdaten_config_file = "GetOnlineServicesLuftdaten"
        self.open_sense_map_config_file = "GetOnlineServicesOpenSenseMap"
        self.system_data = "GetSystemData"
        self.primary_log = "GetPrimaryLog"
        self.network_log = "GetNetworkLog"
        self.sensors_log = "GetSensorsLog"
        self.download_zipped_logs = "DownloadZippedLogs"
        self.download_zipped_logs_size = "GetZippedLogsSize"
        self.download_zipped_everything = "DownloadZippedEverything"
        self.sensor_readings = "GetIntervalSensorReadings"
        self.sensors_latency = "GetSensorsLatency"
        self.sensor_name = "GetHostName"
        self.system_uptime = "GetSystemUptime"
        self.system_date_time = "GetSystemDateTime"
        self.cpu_temp = "GetCPUTemperature"
        self.environmental_temp = "GetEnvTemperature"
        self.env_temp_offset = "GetTempOffsetEnv"
        self.pressure = "GetPressure"
        self.altitude = "GetAltitude"
        self.humidity = "GetHumidity"
        self.distance = "GetDistance"
        self.all_gas = "GetAllGas"
        self.gas_index = "GetGasResistanceIndex"
        self.gas_oxidised = "GetGasOxidised"
        self.gas_reduced = "GetGasReduced"
        self.gas_nh3 = "GetGasNH3"
        self.all_particulate_matter = "GetAllParticulateMatter"
        self.pm_1 = "GetParticulateMatter1"
        self.pm_2_5 = "GetParticulateMatter2_5"
        self.pm_10 = "GetParticulateMatter10"
        self.lumen = "GetLumen"
        self.electromagnetic_spectrum = "GetEMSColors"
        self.all_ultra_violet = "GetAllUltraViolet"
        self.ultra_violet_index = "GetUltraVioletA"
        self.ultra_violet_a = "GetUltraVioletA"
        self.ultra_violet_b = "GetUltraVioletB"
        self.accelerometer_xyz = "GetAccelerometerXYZ"
        self.magnetometer_xyz = "GetMagnetometerXYZ"
        self.gyroscope_xyz = "GetGyroscopeXYZ"
        self.database_notes = "GetDatabaseNotes"
        self.database_note_dates = "GetDatabaseNoteDates"
        self.database_user_note_dates = "GetDatabaseNoteUserDates"


class CreateDatabaseVariables:
    """ Creates a object instance holding SQLite3 database table and row names. """

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


class CreateDisplaySensorsVariables:
    """ Create a object instance holding Sensor Display Variables (Such as sensor types to display). """

    def __init__(self):
        self.display_type_numerical = "numerical"
        self.display_type_graph = "graph"

        self.sensor_uptime = "SensorUpTime"
        self.system_temperature = "SystemTemp"
        self.env_temperature = "EnvironmentTemp"
        self.pressure = "Pressure"
        self.altitude = "Altitude"
        self.humidity = "Humidity"
        self.distance = "Distance"
        self.gas = "Gas"
        self.particulate_matter = "Particulate_Matter"
        self.lumen = "Lumen"
        self.color = "Color"
        self.ultra_violet = "Ultra_Violet"

        self.accelerometer = "Acc"
        self.magnetometer = "Mag"
        self.gyroscope = "Gyro"


# Dictionary of Terminal commands
bash_commands = {"inkupg": "bash /opt/kootnet-sensors/scripts/update_kootnet-sensors_e-ink.sh",
                 "RestartService": "systemctl daemon-reload ; systemctl restart KootnetSensors.service",
                 "EnableService": "systemctl enable KootnetSensors.service",
                 "StartService": "systemctl start KootnetSensors.service",
                 "DisableService": "systemctl disable KootnetSensors.service",
                 "StopService": "systemctl stop KootnetSensors.service",
                 "UpgradeOnline": "systemctl start SensorUpgradeOnline.service",
                 "UpgradeOnlineClean": "systemctl start SensorUpgradeOnlineClean.service",
                 "UpgradeOnlineCleanDEV": "systemctl start SensorUpgradeOnlineCleanDEV.service",
                 "UpgradeOnlineDEV": "systemctl start SensorUpgradeOnlineDEV.service",
                 "UpgradeSMB": "systemctl start SensorUpgradeSMB.service",
                 "UpgradeSMBClean": "systemctl start SensorUpgradeSMBClean.service",
                 "UpgradeSMBCleanDEV": "systemctl start SensorUpgradeSMBCleanDEV.service",
                 "UpgradeSMBDEV": "systemctl start SensorUpgradeSMBDEV.service",
                 "UpgradeSystemOS": "apt-get update && apt-get -y upgrade",
                 "RebootSystem": "reboot",
                 "ShutdownSystem": "shutdown -h now"}

# The following variables are populated at runtime (Up until the next blank line)
# This helps lessen disk reads by caching commonly used variables
current_platform = system()
operating_system_name = ""
database_variables = CreateDatabaseVariables()
program_last_updated = ""
reboot_count = ""
total_ram_memory = 0.0
total_ram_memory_size_type = " MB"

# Static variables
command_data_separator = "[new_data_section]"
no_sensor_present = "NoSensor"

# Plotly Configuration Variables
plotly_theme = "plotly_dark"

# Network Variables
hostname = ""
ip = ""
ip_subnet = ""
gateway = ""
dns1 = ""
dns2 = ""

# Wifi Variables
wifi_country_code = ""
wifi_ssid = ""
wifi_security_type = ""
wifi_psk = ""

# Flask App Login Variables (Web Portal Login)
http_flask_user = "Kootnet"
http_flask_password = "sensors"

# Running "Service" Threads
http_server_thread = None
interval_recording_thread = None
mini_display_thread = None
interactive_sensor_thread = None
weather_underground_thread = None
luftdaten_thread = None
open_sense_map_thread = None

# Running Trigger Recording Threads
trigger_thread_sensor_uptime = None
trigger_thread_cpu_temp = None
trigger_thread_env_temp = None
trigger_thread_pressure = None
trigger_thread_altitude = None
trigger_thread_humidity = None
trigger_thread_distance = None
trigger_thread_lumen = None
trigger_thread_visible_ems = None
trigger_thread_accelerometer = None
trigger_thread_magnetometer = None
trigger_thread_gyroscope = None

# Checked before running OS or pip3 upgrades
# Set to False when stating a upgrade, returns to True after program restarts
sensor_ready_for_upgrade = True

# Variables to make sure Sensor Control is only creating a single copy at any given time
creating_the_reports_zip = False
creating_the_big_zip = False
creating_databases_zip = False
creating_logs_zip = False

# Possible Trigger "High / Low" States
normal_state = "Normal"
low_state = "Low"
high_state = "High"

state_sensor_uptime = normal_state
state_cpu_temp = normal_state
state_env_temp = normal_state
state_pressure = normal_state
state_altitude = normal_state
state_humidity = normal_state
state_distance = normal_state
state_lumen = normal_state
state_visible_ems = normal_state
state_accelerometer = normal_state
state_magnetometer = normal_state
state_gyroscope = normal_state

# Login used for remote sensors (Used in Sensor Control)
http_login = ""
http_password = ""

# Used to get data from multiple remote sensors at the "same" time.
flask_return_data_queue = Queue()
data_queue = Queue()
data_queue2 = Queue()
data_queue3 = Queue()

# Download Sensor SQL Database in a zip placeholder
sensor_database_zipped = b''

# Sensor Control Download placeholders
sc_reports_zip_name = ""
sc_logs_zip_name = ""
sc_databases_zip_name = ""
sc_big_zip_name = ""
sc_databases_zip_in_memory = False
sc_big_zip_in_memory = False
sc_in_memory_zip = b''

# HTML Sensor Notes Variables
notes_total_count = 0
note_current = 1
