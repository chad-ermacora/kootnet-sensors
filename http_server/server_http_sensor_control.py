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
from operations_modules.app_generic_functions import get_response_bg_colour, get_http_sensor_reading, \
    get_file_content, check_for_port_in_address, get_ip_and_port_split
from configuration_modules import app_config_access
from operations_modules import app_cached_variables
from operations_modules import network_wifi
from operations_modules import software_version
from configuration_modules.config_primary import CreatePrimaryConfiguration
from configuration_modules.config_installed_sensors import CreateInstalledSensorsConfiguration
from configuration_modules.config_weather_underground import CreateWeatherUndergroundConfiguration
from configuration_modules.config_luftdaten import CreateLuftdatenConfiguration
from configuration_modules.config_open_sense_map import CreateOpenSenseMapConfiguration

running_with_root = app_cached_variables.running_with_root
if software_version.old_version == software_version.version:
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

        html_report_sensors_latency_start = get_file_content(file_locations.html_report_sensors_latency1_start).strip()
        html_report_sensors_latency_sensor = get_file_content(file_locations.html_report_sensors_latency2_sensor).strip()
    except Exception as init_error:
        logger.primary_logger.warning("Problem loading Report Templates: " + str(init_error))

html_address_list = ["senor_ip_1", "senor_ip_2", "senor_ip_3", "senor_ip_4", "senor_ip_5",
                     "senor_ip_6", "senor_ip_7", "senor_ip_8", "senor_ip_9", "senor_ip_10",
                     "senor_ip_11", "senor_ip_12", "senor_ip_13", "senor_ip_14", "senor_ip_15",
                     "senor_ip_16", "senor_ip_17", "senor_ip_18", "senor_ip_19", "senor_ip_20"]


class CreateReplacementVariables:
    def __init__(self):
        self.remote_sensor_commands = app_cached_variables.CreateNetworkGetCommands()

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
                ["GetRAMTotal", "{{ TotalRAM }}"],
                ["GetRAMTotalSizeType", "{{ TotalRAMSizeType }}"],
                ["GetUsedDiskSpace", "{{ FreeDiskSpace }}"]]

    def report_config(self, ip_address):
        try:
            get_config_command = self.remote_sensor_commands.sensor_configuration_file
            command_installed_sensors = self.remote_sensor_commands.installed_sensors_file
            command_config_os_wu = self.remote_sensor_commands.weather_underground_config_file
            command_config_os_luftdaten = self.remote_sensor_commands.luftdaten_config_file
            command_config_os_osm = self.remote_sensor_commands.open_sense_map_config_file

            wifi_ssid = ""
            weather_underground_enabled = ""
            open_sense_map_enabled = ""

            if get_http_sensor_reading(ip_address, command=self.remote_sensor_commands.check_portal_login) == "OK":
                wifi_config_file = self.remote_sensor_commands.wifi_config_file
                wifi_config_raw = get_http_sensor_reading(ip_address, command=wifi_config_file)
                weather_underground_config_raw = get_http_sensor_reading(ip_address, command=command_config_os_wu)
                open_sense_map_config_raw = get_http_sensor_reading(ip_address, command=command_config_os_osm)

                wifi_config_lines = wifi_config_raw.strip().split("\n")
                if len(wifi_config_lines) > 2 and wifi_config_lines[1][0] != "<":
                    wifi_ssid = network_wifi.get_wifi_ssid(wifi_config_lines)

                wu_config = CreateWeatherUndergroundConfiguration(load_from_file=False)
                wu_config.config_file_location = "Sensor Control's Weather Underground Config from " + ip_address
                wu_config.set_config_with_str(weather_underground_config_raw)
                weather_underground_enabled = self.get_enabled_disabled_text(wu_config.weather_underground_enabled)

                osm_config = CreateOpenSenseMapConfiguration(load_from_file=False)
                osm_config.config_file_location = "Sensor Control's Open Sense Map Config from " + ip_address
                osm_config.set_config_with_str(open_sense_map_config_raw)
                open_sense_map_enabled = self.get_enabled_disabled_text(osm_config.open_sense_map_enabled)

                weather_underground_colour = "#F4A460"
                if wu_config.weather_underground_enabled:
                    weather_underground_colour = "lightgreen"

                open_sense_map_colour = "#F4A460"
                if osm_config.open_sense_map_enabled:
                    open_sense_map_colour = "lightgreen"
            else:
                weather_underground_colour = "orangered"
                open_sense_map_colour = "orangered"

            sensor_date_time = get_http_sensor_reading(ip_address, command=self.remote_sensor_commands.system_date_time)
            sensor_config_raw = get_http_sensor_reading(ip_address, command=get_config_command)
            installed_sensors_raw = get_http_sensor_reading(ip_address, command=command_installed_sensors)
            luftdaten_config_raw = get_http_sensor_reading(ip_address, command=command_config_os_luftdaten)
            sensors_config = CreatePrimaryConfiguration(load_from_file=False)
            sensors_config.set_config_with_str(sensor_config_raw)

            luftdaten_config = CreateLuftdatenConfiguration(load_from_file=False)
            luftdaten_config.config_file_location = "Sensor Control's Luftdaten Config from " + ip_address
            luftdaten_config.set_config_with_str(luftdaten_config_raw)
            luftdaten_enabled = self.get_enabled_disabled_text(luftdaten_config.luftdaten_enabled)
            luftdaten_colour = "#F4A460"
            if luftdaten_config.luftdaten_enabled:
                luftdaten_colour = "lightgreen"

            installed_sensors_config = CreateInstalledSensorsConfiguration(load_from_file=False)
            installed_sensors_config.set_config_with_str(installed_sensors_raw)
            try:
                installed_sensors_lines = installed_sensors_raw.strip().split("\n")
                rpi_model_name = installed_sensors_lines[3].split("=")[1].strip()
            except Exception as error:
                logger.network_logger.debug("Failed Getting Raspberry Pi Model: " + str(error))
                rpi_model_name = "Raspberry Pi"
            installed_sensors_config.config_settings_names[2] = rpi_model_name

            text_debug = str(self.get_enabled_disabled_text(sensors_config.enable_debug_logging))
            text_display = str(self.get_enabled_disabled_text(app_config_access.display_config.enable_display))
            text_interval_recording = str(self.get_enabled_disabled_text(sensors_config.enable_interval_recording))
            text_interval_seconds = str(sensors_config.sleep_duration_interval)
            text_trigger_recording = str(self.get_enabled_disabled_text(sensors_config.enable_trigger_recording))
            text_custom_temperature = str(self.get_enabled_disabled_text(sensors_config.enable_custom_temp))

            wifi_network_colour = "orangered"
            if len(wifi_ssid) > 0:
                wifi_network_colour = "#0099ff"

            debug_colour = "#F4A460"
            if sensors_config.enable_debug_logging:
                debug_colour = "lightgreen"

            display_colour = "#F4A460"
            if app_config_access.display_config.enable_display:
                display_colour = "lightgreen"

            interval_recording_colour = "#F4A460"
            if sensors_config.enable_interval_recording:
                interval_recording_colour = "lightgreen"

            trigger_recording_colour = "#F4A460"
            if sensors_config.enable_trigger_recording:
                trigger_recording_colour = "lightgreen"

            temp_offset_colour = "#F4A460"
            if sensors_config.enable_custom_temp:
                temp_offset_colour = "lightgreen"

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
            log_msg = "Sensor Control - Get Remote Sensor " + ip_address + " Config Report Failed: " + str(error)
            logger.network_logger.warning(log_msg)
            return []

    def report_sensors_choice(self, ip_address, report_type="sensors_test"):
        try:
            if report_type == "sensors_test":
                get_sensors_readings_command = self.remote_sensor_commands.sensor_readings
            else:
                get_sensors_readings_command = self.remote_sensor_commands.sensors_latency
            sensor_readings_raw = get_http_sensor_reading(ip_address, command=get_sensors_readings_command, timeout=20)
            sensor_readings_raw = sensor_readings_raw.strip()
            sensor_types = sensor_readings_raw.split(app_cached_variables.command_data_separator)[0].split(",")
            sensor_readings = sensor_readings_raw.split(app_cached_variables.command_data_separator)[1].split(",")

            return_types = ""
            return_readings = ""
            for sensor_type, sensor_reading in zip(sensor_types, sensor_readings):
                return_types += '<th><span style="color: #00ffff;">' + \
                                str(sensor_type) + \
                                "</span></th>\n"
                return_readings += '<th><span style="color: #ccffcc;">' + \
                                   str(sensor_reading) + \
                                   "</span></th>\n"

            return [[return_types, "{{ SensorTypes }}"],
                    [return_readings, "{{ SensorReadings }}"]]
        except Exception as error:
            log_msg = "Sensor Control - Get Remote Sensor " + ip_address + " Sensors Test Report Failed: " + str(error)
            logger.network_logger.warning(log_msg)
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


def get_online_report(ip_address, report_type="systems_report"):
    report_type_config = app_config_access.sensor_control_config.radio_report_config
    report_type_test_sensors = app_config_access.sensor_control_config.radio_report_test_sensors
    report_type_latency_sensors = app_config_access.sensor_control_config.radio_report_sensors_latency

    sensor_report = html_report_system_sensor
    command_and_replacements = CreateReplacementVariables().report_system()
    if report_type == report_type_config:
        sensor_report = html_report_config_sensor
        command_and_replacements = CreateReplacementVariables().report_config(ip_address)
    elif report_type == report_type_test_sensors:
        sensor_report = html_report_sensors_test_sensor
        command_and_replacements = CreateReplacementVariables().report_sensors_choice(ip_address)
    elif report_type == report_type_latency_sensors:
        sensor_report = html_report_sensors_latency_sensor
        command_and_replacements = CreateReplacementVariables().report_sensors_choice(ip_address, report_type="Latency")

    try:
        if check_for_port_in_address(ip_address):
            address_split = get_ip_and_port_split(ip_address)
            address_and_port = address_split[0].strip() + ":" + address_split[1].strip()
        else:
            address_and_port = ip_address.strip() + ":10065"
        sensor_report = sensor_report.replace("{{ IPAddress }}", address_and_port)
        task_start_time = time.time()
        sensor_check = get_http_sensor_reading(ip_address)
        task_end_time = str(round(time.time() - task_start_time, 3))
        if sensor_check == "OK":
            sensor_name = get_http_sensor_reading(ip_address, command="GetHostName")
            sensor_report = sensor_report.replace("{{ SensorName }}", sensor_name)
            sensor_report = sensor_report.replace("{{ ResponseBackground }}", get_response_bg_colour(task_end_time))
            for command_and_replacement in command_and_replacements:
                if report_type == "systems_report":
                    replacement_value = str(get_http_sensor_reading(ip_address, command=command_and_replacement[0]))
                    sensor_report = sensor_report.replace(command_and_replacement[1], replacement_value)
                else:
                    sensor_report = sensor_report.replace(command_and_replacement[1], command_and_replacement[0])
            sensor_report = sensor_report.replace("{{ SensorResponseTime }}", task_end_time)
            if report_type == report_type_config:
                app_cached_variables.data_queue2.put([sensor_name, sensor_report])
            elif report_type == report_type_latency_sensors or report_type == report_type_test_sensors:
                app_cached_variables.data_queue3.put([sensor_name, sensor_report])
            else:
                app_cached_variables.data_queue.put([sensor_name, sensor_report])
    except Exception as error:
        log_msg = "Remote Sensor " + ip_address + " Failed providing " + str(report_type) + " Data: " + str(error)
        logger.network_logger.warning(log_msg)
