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
from os import geteuid


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

        self.set_interval_configuration = "SetIntervalConfiguration"
        self.set_high_low_trigger_config = "SetHighLowTriggerConfiguration"
        self.set_variance_configuration = "SetVarianceConfiguration"

        self.set_display_config = "SetDisplayConfiguration"
        self.set_email_configuration = "SetEmailConfiguration"
        self.set_sensor_control_configuration = "SetSensorControlConfiguration"
        self.set_wifi_configuration = "SetWifiConfiguration"

        self.set_mqtt_publisher_configuration = "SetMQTTPublisherConfiguration"
        self.set_mqtt_subscriber_configuration = "SetMQTTSubscriberConfiguration"

        self.set_weather_underground_configuration = "SetWeatherUndergroundConfiguration"
        self.set_luftdaten_configuration = "SetLuftdatenConfiguration"
        self.set_open_sense_map_configuration = "SetOpenSenseMapConfiguration"


class CreateNetworkGetCommands:
    """ Create a object instance holding available network "Get" commands (AKA get data from remote sensor). """

    def __init__(self):
        self.check_online_status = "CheckOnlineStatus"
        self.check_portal_login = "TestLogin"

        self.sensor_sql_database = "DownloadSQLDatabase"
        self.sensor_sql_database_raw = "DownloadSQLDatabaseRAW"
        self.sensor_sql_database_size = "GetSQLDBSize"
        self.sensor_zipped_sql_database_size = "GetZippedSQLDatabaseSize"

        self.sensor_configuration_file = "GetConfiguration"
        self.installed_sensors_file = "GetInstalledSensors"
        self.interval_configuration_file = "GetIntervalConfiguration"
        self.high_low_trigger_configuration_file = "GetHighLowTriggerConfiguration"
        self.variance_config_file = "GetVarianceConfiguration"
        self.display_configuration_file = "GetDisplayConfiguration"
        self.email_configuration_file = "GetEmailConfiguration"
        self.mqtt_publisher_configuration_file = "GetMQTTPublisherConfiguration"
        self.mqtt_subscriber_configuration_file = "GetMQTTSubscriberConfiguration"
        self.sensor_control_configuration_file = "GetSensorControlConfiguration"
        self.wifi_config_file = "GetWifiConfiguration"
        self.weather_underground_config_file = "GetWeatherUndergroundConfiguration"
        self.luftdaten_config_file = "GetOnlineServicesLuftdaten"
        self.open_sense_map_config_file = "GetOnlineServicesOpenSenseMap"

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
        self.all_particulate_matter = "GetAllParticulateMatter"
        self.lumen = "GetLumen"
        self.electromagnetic_spectrum = "GetEMSColors"
        self.all_ultra_violet = "GetAllUltraViolet"
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

        self.sensor_check_in_version = "KootnetVersion"
        self.sensor_check_in_installed_sensors = "InstalledSensors"
        self.sensor_check_in_primary_log = "PrimaryLog"
        self.sensor_check_in_sensors_log = "SensorsLog"

        self.trigger_state = "TriggerState"

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

        self.gas_all_dic = "All_Gas_As_Dictionary"
        self.gas_resistance_index = "Gas_Resistance_Index"
        self.gas_oxidising = "Gas_Oxidising"
        self.gas_reducing = "Gas_Reducing"
        self.gas_nh3 = "Gas_NH3"

        self.particulate_matter_all_dic = "All_Particulate_Matter_As_Dictionary"
        self.particulate_matter_1 = "Particulate_Matter_1"
        self.particulate_matter_2_5 = "Particulate_Matter_2_5"
        self.particulate_matter_4 = "Particulate_Matter_4"
        self.particulate_matter_10 = "Particulate_Matter_10"

        self.lumen = "Lumen"

        self.colour_all_dic = "All_Colours_As_Dictionary"
        self.red = "Red"
        self.orange = "Orange"
        self.yellow = "Yellow"
        self.green = "Green"
        self.blue = "Blue"
        self.violet = "Violet"

        self.ultra_violet_all_dic = "All_Ultra_Violet_As_Dictionary"
        self.ultra_violet_index = "Ultra_Violet_Index"
        self.ultra_violet_a = "Ultra_Violet_A"
        self.ultra_violet_b = "Ultra_Violet_B"

        self.acc_all_dic = "All_Acceleration_As_Dictionary"
        self.acc_x = "Acc_X"
        self.acc_y = "Acc_Y"
        self.acc_z = "Acc_Z"

        self.mag_all_dic = "All_Magnetometer_As_Dictionary"
        self.mag_x = "Mag_X"
        self.mag_y = "Mag_Y"
        self.mag_z = "Mag_Z"

        self.gyro_all_dic = "All_Gyroscope_As_Dictionary"
        self.gyro_x = "Gyro_X"
        self.gyro_y = "Gyro_Y"
        self.gyro_z = "Gyro_Z"

    def get_sensor_columns_list(self):
        """ Returns SQL Table columns used for Interval recording as a list. """
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
                              self.particulate_matter_4,
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


class CreateEmptyThreadClass:
    def __init__(self):
        self.current_state = "Disabled"


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
running_with_root = True
if geteuid() != 0:
    running_with_root = False
operating_system_name = ""
program_last_updated = ""
reboot_count = ""
total_ram_memory = 0.0
total_ram_memory_size_type = " MB"
tmp_sensor_id = ""
database_variables = CreateDatabaseVariables()

# Names of all the uploaded databases for graphing (Only names, no directory path)
uploaded_databases_list = []

# Is filled with Currently available online Stable / Developmental versions
standard_version_available = "Retrieving ..."
developmental_version_available = "Retrieving ..."

# Static variables
command_data_separator = "[new_data_section]"
no_sensor_present = "NoSensor"

# Plotly Configuration Variables
plotly_theme = "plotly_dark"

# Network Variables
hostname = "Still Loading"
ip = "Refresh Page"
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

# Sensor Check-in View Variables
checkin_search_sensor_id = ""
checkin_search_sensor_installed_sensors = ""
checkin_sensor_info = ""
checkin_search_primary_log = ""
checkin_search_sensors_log = ""

# Running "Service" Threads
http_server_thread = CreateEmptyThreadClass()
interval_recording_thread = CreateEmptyThreadClass()
report_email_thread = CreateEmptyThreadClass()
graph_email_thread = CreateEmptyThreadClass()
mini_display_thread = CreateEmptyThreadClass()
interactive_sensor_thread = CreateEmptyThreadClass()
mqtt_publisher_thread = CreateEmptyThreadClass()
weather_underground_thread = CreateEmptyThreadClass()
luftdaten_thread = CreateEmptyThreadClass()
open_sense_map_thread = CreateEmptyThreadClass()

# Running High/Low Trigger Recording Threads
trigger_high_low_cpu_temp = CreateEmptyThreadClass()
trigger_high_low_env_temp = CreateEmptyThreadClass()
trigger_high_low_pressure = CreateEmptyThreadClass()
trigger_high_low_altitude = CreateEmptyThreadClass()
trigger_high_low_humidity = CreateEmptyThreadClass()
trigger_high_low_distance = CreateEmptyThreadClass()
trigger_high_low_lumen = CreateEmptyThreadClass()
trigger_high_low_visible_colours = CreateEmptyThreadClass()
trigger_high_low_ultra_violet = CreateEmptyThreadClass()
trigger_high_low_gas = CreateEmptyThreadClass()
trigger_high_low_particulate_matter = CreateEmptyThreadClass()
trigger_high_low_accelerometer = CreateEmptyThreadClass()
trigger_high_low_magnetometer = CreateEmptyThreadClass()
trigger_high_low_gyroscope = CreateEmptyThreadClass()

# Trigger Variance threads. Re-Work? at least re-name.
trigger_variance_thread_cpu_temp = CreateEmptyThreadClass()
trigger_variance_thread_env_temp = CreateEmptyThreadClass()
trigger_variance_thread_pressure = CreateEmptyThreadClass()
trigger_variance_thread_altitude = CreateEmptyThreadClass()
trigger_variance_thread_humidity = CreateEmptyThreadClass()
trigger_variance_thread_distance = CreateEmptyThreadClass()
trigger_variance_thread_lumen = CreateEmptyThreadClass()
trigger_variance_thread_visible_ems = CreateEmptyThreadClass()
trigger_variance_thread_ultra_violet = CreateEmptyThreadClass()
trigger_variance_thread_gas = CreateEmptyThreadClass()
trigger_variance_thread_particulate_matter = CreateEmptyThreadClass()
trigger_variance_thread_accelerometer = CreateEmptyThreadClass()
trigger_variance_thread_magnetometer = CreateEmptyThreadClass()
trigger_variance_thread_gyroscope = CreateEmptyThreadClass()

# If these variables are set to True, it will restart the corresponding thread
# After the thread restarts, it sets this back to False
restart_interval_recording_thread = False
restart_all_trigger_threads = False
restart_report_email_thread = False
restart_graph_email_thread = False
restart_mini_display_thread = False
restart_mqtt_publisher_thread = False
restart_weather_underground_thread = False
restart_luftdaten_thread = False
restart_open_sense_map_thread = False

# If set to True, it will prompt to restart service or reboot system in the HTTPS Web Portal
html_service_restart = False
html_sensor_reboot = False

# Checked before running OS or pip3 upgrades
# Set to False when stating a upgrade, returns to True after program restarts
sensor_ready_for_upgrade = True

# Variables to make sure Sensor Control is only creating a single copy at any given time
creating_the_reports_zip = False
creating_the_big_zip = False
creating_databases_zip = False
creating_logs_zip = False

creating_combo_report = False
creating_system_report = False
creating_config_report = False
creating_readings_report = False
creating_latency_report = False

# Cached Reports
default_report = """
<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="robots" content="noindex">
        <title>Kootnet Sensor</title>
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
    </head>
    <body style='background-color: black;'>
        <h2><a style='text-decoration: underline; color: red;' href='/SensorControlManage';>Back to Sensor Control</a></h3>
        <p style='color: white;'>No report found, please generated the report first</p>
    </body>
</html>
"""
html_combo_report = default_report
html_system_report = default_report
html_config_report = default_report
html_readings_report = default_report
html_latency_report = default_report

# Login used for remote sensors (Used in Sensor Control)
http_login = ""
http_password = ""

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

# Quick Graph's Variables
quick_graph_max_sql_entries = 1000
quick_graph_skip_sql_entries = 0
quick_graph_hours = 48
quick_graph_uptime = 1
quick_graph_cpu_temp = 0
quick_graph_env_temp = 1
quick_graph_pressure = 0
quick_graph_altitude = 0
quick_graph_humidity = 1
quick_graph_distance = 0
quick_graph_gas = 0
quick_graph_particulate_matter = 0
quick_graph_lumen = 0
quick_graph_colours = 0
quick_graph_ultra_violet = 0
quick_graph_acc = 0
quick_graph_mag = 0
quick_graph_gyro = 0
