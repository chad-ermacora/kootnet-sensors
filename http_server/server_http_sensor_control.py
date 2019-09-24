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
from operations_modules import app_config_access
from operations_modules import app_cached_variables
from operations_modules import network_wifi
from operations_modules.online_services import weather_underground
from operations_modules.online_services import luftdaten
from operations_modules.online_services import open_sense_map
from operations_modules.app_generic_functions import get_http_sensor_reading, get_file_content

sensor_bg_names_list = ["senor_ip_1", "senor_ip_2", "senor_ip_3", "senor_ip_4", "senor_ip_5", "senor_ip_6",
                        "senor_ip_7", "senor_ip_8", "senor_ip_9", "senor_ip_10", "senor_ip_11", "senor_ip_12",
                        "senor_ip_13", "senor_ip_14", "senor_ip_15", "senor_ip_16", "senor_ip_17",
                        "senor_ip_18", "senor_ip_19", "senor_ip_20"]
try:
    html_report_system_start = get_file_content(file_locations.html_report_system1_start).strip()
    html_report_system_end = get_file_content(file_locations.html_report_system3_end).strip()
    html_report_system_sensor = get_file_content(file_locations.html_report_system2_sensor).strip()

    html_report_config_start = get_file_content(file_locations.html_report_config1_start).strip()
    html_report_config_end = get_file_content(file_locations.html_report_config3_end).strip()
    html_report_config_sensor = get_file_content(file_locations.html_report_config2_sensor).strip()

    html_report_sensors_test_start = get_file_content(file_locations.html_report_sensors_test1_start).strip()
    html_report_sensors_test_end = get_file_content(file_locations.html_report_sensors_test3_end).strip()
    html_report_sensors_test_sensor = get_file_content(file_locations.html_report_sensors_test2_sensor).strip()
except Exception as init_error:
    logger.primary_logger.warning("Problem loading Report Templates: " + str(init_error))


class CreateNetworkGetCommands:
    """ Create a object instance holding available network "Get" commands (AKA expecting data back). """

    def __init__(self):
        self.sensor_sql_database = "DownloadSQLDatabase"
        self.sensor_configuration = "GetConfigurationReport"
        self.sensor_configuration_file = "GetConfiguration"
        self.installed_sensors_file = "GetInstalledSensors"
        self.wifi_config_file = "GetWifiConfiguration"
        self.variance_config = "GetVarianceConfiguration"
        self.weather_underground_config_file = "GetOnlineServicesWeatherUnderground"
        self.luftdaten_config_file = "GetOnlineServicesLuftdaten"
        self.open_sense_map_config_file = "GetOnlineServicesOpenSenseMap"
        self.system_data = "GetSystemData"
        self.primary_log = "GetPrimaryLog"
        self.network_log = "GetNetworkLog"
        self.sensors_log = "GetSensorsLog"
        self.download_zipped_logs = "DownloadZippedLogs"
        self.sensor_readings = "GetIntervalSensorReadings"
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


class CreateReplacementVariables:

    def __init__(self):
        self.remote_sensor_commands = CreateNetworkGetCommands()

    @staticmethod
    def report_system():
        return [["GetOSVersion", "{{ OSVersion }}"],
                ["GetSensorVersion", "{{ ProgramVersion }}"],
                ["GetProgramLastUpdated", "{{ LastUpdated }}"],
                ["GetSystemDateTime", "{{ SensorDateTime }}"],
                ["GetSystemUptime", "{{ SystemUpTime }}"],
                ["GetSQLDBSize", "{{ SQLDBSize }}"],
                ["GetCPUTemperature", "{{ CPUTemp }}"],
                ["GetRAMUsed", "{{ RAMUsed }}"],
                ["GetUsedDiskSpace", "{{ FreeDiskSpace }}"]]

    def report_config(self, ip_address):
        try:
            get_config_command = self.remote_sensor_commands.sensor_configuration_file
            command_installed_sensors = self.remote_sensor_commands.installed_sensors_file
            command_config_os_wu = self.remote_sensor_commands.weather_underground_config_file
            command_config_os_luftdaten = self.remote_sensor_commands.luftdaten_config_file
            command_config_os_osm = self.remote_sensor_commands.open_sense_map_config_file

            sensor_date_time = get_http_sensor_reading(ip_address, command=self.remote_sensor_commands.system_date_time)
            sensor_config_raw = get_http_sensor_reading(ip_address, command=get_config_command)
            installed_sensors_raw = get_http_sensor_reading(ip_address, command=command_installed_sensors)
            wifi_config_raw = get_http_sensor_reading(ip_address, command=self.remote_sensor_commands.wifi_config_file)
            weather_underground_config_raw = get_http_sensor_reading(ip_address, command=command_config_os_wu)
            luftdaten_config_raw = get_http_sensor_reading(ip_address, command=command_config_os_luftdaten)
            open_sense_map_config_raw = get_http_sensor_reading(ip_address, command=command_config_os_osm)

            sensor_config_lines = sensor_config_raw.strip().split("\n")
            installed_sensors_lines = installed_sensors_raw.strip().split("\n")
            try:
                rpi_model_name = installed_sensors_lines[2].split("=")[1].strip()
            except Exception as error:
                logger.network_logger.debug("Failed Getting Raspberry Pi Model: " + str(error))
                rpi_model_name = "Raspberry Pi"
            wifi_config_lines = wifi_config_raw.strip().split("\n")

            wu_config = weather_underground.CreateWeatherUndergroundConfig()
            wu_config.update_settings_from_file(file_content=weather_underground_config_raw, skip_write=True)

            luftdaten_config = luftdaten.CreateLuftdatenConfig()
            luftdaten_config.update_settings_from_file(file_content=luftdaten_config_raw.strip(), skip_write=True)

            osm_config = open_sense_map.CreateOpenSenseMapConfig()
            osm_config.update_settings_from_file(file_content=open_sense_map_config_raw.strip(), skip_write=True)

            sensors_config = app_config_access.config_primary.convert_config_lines_to_obj(sensor_config_lines,
                                                                                          skip_write=True)
            installed_sensors_config = app_config_access.config_installed_sensors.convert_lines_to_obj(
                installed_sensors_lines, skip_write=True)

            installed_sensors_config.raspberry_pi_name = rpi_model_name

            weather_underground_enabled = self.get_enabled_disabled_text(wu_config.weather_underground_enabled)
            luftdaten_enabled = self.get_enabled_disabled_text(luftdaten_config.luftdaten_enabled)
            open_sense_map_enabled = self.get_enabled_disabled_text(osm_config.open_sense_map_enabled)

            if wu_config.bad_config_load:
                weather_underground_enabled = ""
            if luftdaten_config.bad_load:
                luftdaten_enabled = ""
            if osm_config.bad_load:
                open_sense_map_enabled = ""

            wifi_ssid = ""
            if len(wifi_config_lines) > 2 and wifi_config_lines[1][0] != "<":
                wifi_ssid = network_wifi.get_wifi_ssid(wifi_config_lines)

            text_debug = str(self.get_enabled_disabled_text(sensors_config.enable_debug_logging))
            text_display = str(self.get_enabled_disabled_text(sensors_config.enable_display))
            text_interval_recording = str(self.get_enabled_disabled_text(sensors_config.enable_interval_recording))
            text_interval_seconds = str(sensors_config.sleep_duration_interval)
            text_trigger_recording = str(self.get_enabled_disabled_text(sensors_config.enable_trigger_recording))
            text_custom_temperature = str(self.get_enabled_disabled_text(sensors_config.enable_custom_temp))

            wifi_network_colour = "#F4A460"
            debug_colour = "#F4A460"
            display_colour = "#F4A460"
            interval_recording_colour = "#F4A460"
            trigger_recording_colour = "#F4A460"
            temp_offset_colour = "#F4A460"
            weather_underground_colour = "#F4A460"
            luftdaten_colour = "#F4A460"
            open_sense_map_colour = "#F4A460"
            if len(wifi_ssid) > 0:
                wifi_network_colour = "#0099ff"
            if sensors_config.enable_debug_logging:
                debug_colour = "lightgreen"
            if sensors_config.enable_display:
                display_colour = "lightgreen"
            if sensors_config.enable_interval_recording:
                interval_recording_colour = "lightgreen"
            if sensors_config.enable_trigger_recording:
                trigger_recording_colour = "lightgreen"
            if sensors_config.enable_custom_temp:
                temp_offset_colour = "lightgreen"
            if wu_config.weather_underground_enabled:
                weather_underground_colour = "lightgreen"
            if luftdaten_config.luftdaten_enabled:
                luftdaten_colour = "lightgreen"
            if osm_config.open_sense_map_enabled:
                open_sense_map_colour = "lightgreen"

            value_replace = [[str(sensor_date_time), "{{ SensorDateTime }}"],
                             [text_debug, "{{ DebugLogging }}"],
                             [text_display, "{{ Display }}"],
                             [text_interval_recording, "{{ IntervalRecording }}"],
                             [text_interval_seconds, "{{ IntervalSeconds }}"],
                             [text_trigger_recording, "{{ TriggerRecording }}"],
                             [text_custom_temperature, "{{ EnableTemperatureOffset }}"],
                             [str(sensors_config.temperature_offset), "{{ TemperatureOffset }}"],
                             [wifi_ssid, "{{ WifiNetwork }}"],
                             [weather_underground_enabled, "{{ WeatherUnderground }}"],
                             [luftdaten_enabled, "{{ Luftdaten }}"],
                             [open_sense_map_enabled, "{{ OpenSenseMap }}"],
                             [wifi_network_colour, "{{ WifiNetworkColour }}"],
                             [debug_colour, "{{ DebugLoggingColour }}"],
                             [display_colour, "{{ DisplayColour }}"],
                             [interval_recording_colour, "{{ IntervalRecordingColour }}"],
                             [trigger_recording_colour, "{{ TriggerRecordingColour }}"],
                             [temp_offset_colour, "{{ EnableTemperatureOffsetColour }}"],
                             [weather_underground_colour, "{{ WeatherUndergroundColour }}"],
                             [luftdaten_colour, "{{ LuftdatenColour }}"],
                             [open_sense_map_colour, "{{ OpenSenseMapColour }}"],
                             [installed_sensors_config.get_installed_names_str(), "{{ InstalledSensors }}"]]
            return value_replace
        except Exception as error:
            logger.network_logger.warning("Sensor Control - Get Remote Sensor " + ip_address +
                                          " Config Report Failed: " + str(error))
            return []

    def report_test_sensors(self, ip_address):
        try:
            get_sensors_readings_command = self.remote_sensor_commands.sensor_readings
            sensor_readings_raw = get_http_sensor_reading(ip_address, command=get_sensors_readings_command).strip()
            sensor_types = sensor_readings_raw.split(app_config_access.command_data_separator)[0].split(",")
            sensor_readings = sensor_readings_raw.split(app_config_access.command_data_separator)[1].split(",")

            return_types = ""
            return_readings = ""
            for sensor_type, sensor_reading in zip(sensor_types, sensor_readings):
                return_types += '<th><span style="background-color: #00ffff;">' + \
                                str(sensor_type) + \
                                "</span></th>\n"
                return_readings += '<th><span style="background-color: #0BB10D;">' + \
                                   str(sensor_reading) + \
                                   "</span></th>\n"

            return [[return_types, "{{ SensorTypes }}"],
                    [return_readings, "{{ SensorReadings }}"]]
        except Exception as error:
            logger.network_logger.warning("Sensor Control - Get Remote Sensor " + ip_address +
                                          " Sensors Test Report Failed: " + str(error))
            return []

    @staticmethod
    def get_enabled_disabled_text(setting):
        try:
            if int(setting):
                return "Enabled"
            return "Disabled"
        except Exception as error:
            logger.network_logger.debug("Unable to translate setting for Report: " + str(setting) + " - " + str(error))
            return ""


def check_online_status(ip_address):
    sensor_return = get_http_sensor_reading(ip_address)
    if sensor_return == "OK":
        app_cached_variables.data_queue.put([ip_address, "green"])
    else:
        app_cached_variables.data_queue.put([ip_address, "red"])


def get_online_report(ip_address, report_type="systems_report"):
    report_type_config = app_config_access.sensor_control_config.radio_report_config
    report_type_test_sensors = app_config_access.sensor_control_config.radio_report_test_sensors

    sensor_report = html_report_system_sensor
    command_and_replacements = CreateReplacementVariables().report_system()
    if report_type == report_type_config:
        sensor_report = html_report_config_sensor
        command_and_replacements = CreateReplacementVariables().report_config(ip_address)
    elif report_type == report_type_test_sensors:
        sensor_report = html_report_sensors_test_sensor
        command_and_replacements = CreateReplacementVariables().report_test_sensors(ip_address)

    try:
        sensor_report = sensor_report.replace("{{ IPAddress }}", ip_address)
        task_start_time = time.time()
        sensor_check = get_http_sensor_reading(ip_address)
        task_end_time = str(round(time.time() - task_start_time, 3))
        if sensor_check == "OK":
            sensor_name = get_http_sensor_reading(ip_address, command="GetHostName")
            sensor_report = sensor_report.replace("{{ SensorName }}", sensor_name)
            for command_and_replacement in command_and_replacements:
                if report_type == "systems_report":
                    replacement_value = str(get_http_sensor_reading(ip_address, command=command_and_replacement[0]))
                    sensor_report = sensor_report.replace(command_and_replacement[1], replacement_value)
                else:
                    sensor_report = sensor_report.replace(command_and_replacement[1], command_and_replacement[0])
            sensor_report = sensor_report.replace("{{ SensorResponseTime }}", task_end_time)
            if report_type == report_type_config:
                app_cached_variables.data_queue2.put([sensor_name, sensor_report])
            elif report_type == report_type_test_sensors:
                app_cached_variables.data_queue3.put([sensor_name, sensor_report])
            else:
                app_cached_variables.data_queue.put([sensor_name, sensor_report])
    except Exception as error:
        logger.network_logger.warning("Remote Sensor " + ip_address +
                                      " Failed providing " + str(report_type) +
                                      " Data: " + str(error))