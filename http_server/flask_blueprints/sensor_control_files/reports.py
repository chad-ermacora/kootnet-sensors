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
from threading import Thread
from queue import Queue
from operations_modules import logger
from operations_modules import app_cached_variables
from configuration_modules import app_config_access
from operations_modules import network_wifi
from operations_modules.app_generic_functions import get_response_bg_colour, get_http_sensor_reading, \
    check_for_port_in_address, get_ip_and_port_split
from configuration_modules.config_primary import CreatePrimaryConfiguration
from configuration_modules.config_installed_sensors import CreateInstalledSensorsConfiguration
from configuration_modules.config_interval_recording import CreateIntervalRecordingConfiguration
from configuration_modules.config_trigger_high_low import CreateTriggerHighLowConfiguration
from configuration_modules.config_trigger_variances import CreateTriggerVariancesConfiguration
from configuration_modules.config_display import CreateDisplayConfiguration
from configuration_modules.config_weather_underground import CreateWeatherUndergroundConfiguration
from configuration_modules.config_luftdaten import CreateLuftdatenConfiguration
from configuration_modules.config_open_sense_map import CreateOpenSenseMapConfiguration
from sensor_modules.sensor_access import get_system_datetime, get_reading_unit
from http_server.flask_blueprints.atpro.atpro_interface_functions.atpro_variables import html_report_start, \
    html_report_end, html_report_system, html_report_system_sensor_template, html_report_config, \
    html_report_config_sensor_template, html_report_sensors_readings, html_report_sensor_readings_template, \
    html_report_latency, html_report_latency_sensor_template

running_with_root = app_cached_variables.running_with_root
sensor_get_commands = app_cached_variables.CreateNetworkGetCommands()

html_address_list = ["senor_ip_1", "senor_ip_2", "senor_ip_3", "senor_ip_4", "senor_ip_5",
                     "senor_ip_6", "senor_ip_7", "senor_ip_8", "senor_ip_9", "senor_ip_10",
                     "senor_ip_11", "senor_ip_12", "senor_ip_13", "senor_ip_14", "senor_ip_15",
                     "senor_ip_16", "senor_ip_17", "senor_ip_18", "senor_ip_19", "senor_ip_20"]


class CreateReplacementVariables:

    @staticmethod
    def report_system(ip_address):
        sensor_id = sensor_get_commands.sensor_id
        os_version = sensor_get_commands.os_version
        program_version = sensor_get_commands.program_version
        program_last_updated = sensor_get_commands.program_last_updated
        system_date_time = sensor_get_commands.system_date_time
        system_uptime = sensor_get_commands.system_uptime
        sensor_sql_database_size = sensor_get_commands.sensor_sql_database_size
        cpu_temp = sensor_get_commands.cpu_temp
        system_ram_used = sensor_get_commands.system_ram_used
        system_ram_total = sensor_get_commands.system_ram_total
        system_ram_size_type = sensor_get_commands.system_ram_size_type
        system_disk_space_free = sensor_get_commands.system_disk_space_free

        return [[get_http_sensor_reading(ip_address, command=sensor_id), "{{ SensorID }}"],
                [get_http_sensor_reading(ip_address, command=os_version), "{{ OSVersion }}"],
                [get_http_sensor_reading(ip_address, command=program_version), "{{ ProgramVersion }}"],
                [get_http_sensor_reading(ip_address, command=program_last_updated), "{{ LastUpdated }}"],
                [get_http_sensor_reading(ip_address, command=system_date_time), "{{ SensorDateTime }}"],
                [get_http_sensor_reading(ip_address, command=system_uptime), "{{ SystemUpTime }}"],
                [get_http_sensor_reading(ip_address, command=sensor_sql_database_size), "{{ SQLDBSize }}"],
                [get_http_sensor_reading(ip_address, command=cpu_temp), "{{ CPUTemp }}"],
                [get_http_sensor_reading(ip_address, command=system_ram_used), "{{ RAMUsed }}"],
                [get_http_sensor_reading(ip_address, command=system_ram_total), "{{ TotalRAM }}"],
                [get_http_sensor_reading(ip_address, command=system_ram_size_type), "{{ TotalRAMSizeType }}"],
                [get_http_sensor_reading(ip_address, command=system_disk_space_free), "{{ FreeDiskSpace }}"]]

    def report_config(self, ip_address):
        try:
            get_config_command = sensor_get_commands.sensor_configuration_file
            get_interval_config_command = sensor_get_commands.interval_configuration_file
            get_high_low_config_command = sensor_get_commands.high_low_trigger_configuration_file
            get_variance_config_command = sensor_get_commands.variance_config_file
            get_display_config = sensor_get_commands.display_configuration_file
            command_installed_sensors = sensor_get_commands.installed_sensors_file
            command_config_os_wu = sensor_get_commands.weather_underground_config_file
            command_config_os_luftdaten = sensor_get_commands.luftdaten_config_file
            command_config_os_osm = sensor_get_commands.open_sense_map_config_file

            wifi_ssid = "N/A"
            weather_underground_enabled = "N/A"
            open_sense_map_enabled = "N/A"
            if get_http_sensor_reading(ip_address, command=sensor_get_commands.check_portal_login) == "OK":
                wifi_config_file = sensor_get_commands.wifi_config_file
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

            sensor_date_time = get_http_sensor_reading(ip_address, command=sensor_get_commands.system_date_time)

            sensor_config_raw = get_http_sensor_reading(ip_address, command=get_config_command)
            sensors_config = CreatePrimaryConfiguration(load_from_file=False)
            sensors_config.set_config_with_str(sensor_config_raw)

            display_config_raw = get_http_sensor_reading(ip_address, command=get_display_config)
            display_config = CreateDisplayConfiguration(load_from_file=False)
            display_config.set_config_with_str(display_config_raw)

            installed_sensors_raw = get_http_sensor_reading(ip_address, command=command_installed_sensors)
            installed_sensors_config = CreateInstalledSensorsConfiguration(load_from_file=False)
            installed_sensors_config.set_config_with_str(installed_sensors_raw)

            interval_config_raw = get_http_sensor_reading(ip_address, command=get_interval_config_command)
            interval_config = CreateIntervalRecordingConfiguration(load_from_file=False)
            interval_config.set_config_with_str(interval_config_raw)

            high_low_trigger_config_raw = get_http_sensor_reading(ip_address, command=get_high_low_config_command)
            high_low_trigger_config = CreateTriggerHighLowConfiguration(load_from_file=False)
            high_low_trigger_config.set_config_with_str(high_low_trigger_config_raw)

            variance_trigger_config_raw = get_http_sensor_reading(ip_address, command=get_variance_config_command)
            variance_trigger_config = CreateTriggerVariancesConfiguration(load_from_file=False)
            variance_trigger_config.set_config_with_str(variance_trigger_config_raw)

            luftdaten_config_raw = get_http_sensor_reading(ip_address, command=command_config_os_luftdaten)
            luftdaten_config = CreateLuftdatenConfiguration(load_from_file=False)
            luftdaten_config.set_config_with_str(luftdaten_config_raw)

            luftdaten_config.config_file_location = "Sensor Control's Luftdaten Config from " + ip_address
            luftdaten_enabled = self.get_enabled_disabled_text(luftdaten_config.luftdaten_enabled)

            try:
                installed_sensors_lines = installed_sensors_raw.strip().split("\n")
                rpi_model_name = installed_sensors_lines[3].split("=")[1].strip()
            except Exception as error:
                logger.network_logger.debug("Failed Getting Raspberry Pi Model: " + str(error))
                rpi_model_name = "Raspberry Pi"
            installed_sensors_config.config_settings_names[2] = rpi_model_name

            text_debug = self.get_enabled_disabled_text(sensors_config.enable_debug_logging)
            text_checkin = self.get_enabled_disabled_text(sensors_config.enable_checkin)
            text_display = self.get_enabled_disabled_text(display_config.enable_display)
            text_interval_recording = self.get_enabled_disabled_text(interval_config.enable_interval_recording)
            text_interval_seconds = str(interval_config.sleep_duration_interval)
            enable_high_low_recording = high_low_trigger_config.enable_high_low_trigger_recording
            text_trigger_high_low_recording = self.get_enabled_disabled_text(enable_high_low_recording)
            text_variance_recording = self.get_enabled_disabled_text(variance_trigger_config.enable_trigger_variance)
            text_custom_temperature = self.get_enabled_disabled_text(sensors_config.enable_custom_temp)
            text_rpi_tcf = self.get_enabled_disabled_text(sensors_config.enable_temperature_comp_factor)

            value_replace = [[str(sensor_date_time), "{{ SensorDateTime }}"],
                             [text_debug, "{{ DebugLogging }}"],
                             [text_checkin, "{{ SensorCheckin }}"],
                             [text_display, "{{ Display }}"],
                             [text_interval_recording, "{{ IntervalRecording }}"],
                             [text_interval_seconds, "{{ IntervalSeconds }}"],
                             [text_trigger_high_low_recording, "{{ HighLowRecording }}"],
                             [text_variance_recording, "{{ VarianceRecording }}"],
                             [text_custom_temperature, "{{ TemperatureOffset }}"],
                             [text_rpi_tcf, "{{ TemperatureCorrectionFactor }}"],
                             [wifi_ssid, "{{ WifiNetwork }}"],
                             [weather_underground_enabled, "{{ WeatherUnderground }}"],
                             [luftdaten_enabled, "{{ Luftdaten }}"],
                             [open_sense_map_enabled, "{{ OpenSenseMap }}"],
                             [installed_sensors_config.get_installed_names_str(skip_root_check=True),
                              "{{ InstalledSensors }}"]]
            return value_replace
        except Exception as error:
            log_msg = "Sensor Control - Get Remote Sensor " + ip_address + " Config Report Failed: " + str(error)
            logger.network_logger.warning(log_msg)
            return []

    @staticmethod
    def report_sensors_choice(ip_address, report_type="sensors_test"):
        try:
            if report_type == "sensors_test":
                get_sensors_readings_command = sensor_get_commands.sensor_readings
            else:
                get_sensors_readings_command = sensor_get_commands.sensors_latency
            sensor_readings_raw = get_http_sensor_reading(ip_address, command=get_sensors_readings_command, timeout=20)
            sensor_readings_raw = sensor_readings_raw.strip()
            sensor_types = sensor_readings_raw.split(app_cached_variables.command_data_separator)[0].split(",")
            sensor_readings = sensor_readings_raw.split(app_cached_variables.command_data_separator)[1].split(",")

            return_readings = ""
            for sensor_type, sensor_reading in zip(sensor_types, sensor_readings):
                if sensor_type != "SensorName" and sensor_type != "IP":
                    return_readings += '<div class="col-4 col-m-4 col-sm-4"><div class="counter bg-primary">' + \
                                       "<p><span class='sensor-info'>" + str(sensor_type).replace("_", " ") + \
                                       "</span><br>" + str(sensor_reading) + " " + get_reading_unit(sensor_type) + \
                                       "</p></div></div>\n"

            return [[return_readings, "{{ SensorInfoBoxes }}"]]
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


def get_online_report(ip_address, data_queue, report_type="systems_report"):
    report_type_config = app_config_access.sensor_control_config.radio_report_config
    report_type_test_sensors = app_config_access.sensor_control_config.radio_report_test_sensors
    report_type_latency_sensors = app_config_access.sensor_control_config.radio_report_sensors_latency

    if report_type == report_type_config:
        sensor_report = html_report_config_sensor_template
        command_and_replacements = CreateReplacementVariables().report_config(ip_address)
    elif report_type == report_type_test_sensors:
        sensor_report = html_report_sensor_readings_template
        command_and_replacements = CreateReplacementVariables().report_sensors_choice(ip_address)
    elif report_type == report_type_latency_sensors:
        sensor_report = html_report_latency_sensor_template
        command_and_replacements = CreateReplacementVariables().report_sensors_choice(ip_address, report_type="Latency")
    else:
        sensor_report = html_report_system_sensor_template
        command_and_replacements = CreateReplacementVariables().report_system(ip_address)

    try:
        if check_for_port_in_address(ip_address):
            address_split = get_ip_and_port_split(ip_address)
            address_and_port = address_split[0].strip() + ":" + address_split[1].strip()
        else:
            address_and_port = ip_address.strip() + ":10065"
        address_and_port = "<a style='color: #7f3299;' href='https://" + address_and_port + "' target='_blank'>" + \
                           address_and_port + "</a>"
        sensor_report = sensor_report.replace("{{ IPAddress }}", address_and_port)
        task_start_time = time.time()
        sensor_check = get_http_sensor_reading(ip_address)
        task_end_time = str(round(time.time() - task_start_time, 3))
        if sensor_check == "OK":
            sensor_login_check = get_http_sensor_reading(ip_address, command=sensor_get_commands.check_portal_login)
            if sensor_login_check != "OK":
                sensor_login_check = "Login Failed"
            sensor_name = get_http_sensor_reading(ip_address, command=sensor_get_commands.sensor_name)
            sensor_report = sensor_report.replace("{{ SensorName }}", sensor_name)
            sensor_report = sensor_report.replace("{{ ResponseBackground }}", get_response_bg_colour(task_end_time))
            sensor_report = sensor_report.replace("{{ LoginCheck }}", sensor_login_check)
            for command_and_replacement in command_and_replacements:
                sensor_report = sensor_report.replace(command_and_replacement[1], command_and_replacement[0])
            sensor_report = sensor_report.replace("{{ SensorResponseTime }}", task_end_time)
            data_queue.put([sensor_name, sensor_report])
    except Exception as error:
        log_msg = "Remote Sensor " + ip_address + " Failed providing " + str(report_type) + " Data: " + str(error)
        logger.network_logger.warning(log_msg)
        data_queue.put([ip_address, "Failed"])


def generate_sensor_control_report(address_list, report_type="systems_report"):
    """
    Returns a HTML report based on report_type and sensor addresses provided (IP or DNS addresses as a list).
    Default: systems_report
    """
    new_report = html_report_system
    if report_type == app_config_access.sensor_control_config.radio_report_system:
        app_cached_variables.creating_system_report = True
    if report_type == app_config_access.sensor_control_config.radio_report_config:
        app_cached_variables.creating_config_report = True
        new_report = html_report_config
    elif report_type == app_config_access.sensor_control_config.radio_report_test_sensors:
        app_cached_variables.creating_readings_report = True
        new_report = html_report_sensors_readings
    elif report_type == app_config_access.sensor_control_config.radio_report_sensors_latency:
        app_cached_variables.creating_latency_report = True
        new_report = html_report_latency
    new_report = new_report.replace("{{ DateTime }}", get_system_datetime())

    new_report = html_report_start + "\n" + new_report

    data_queue = Queue()
    sensor_reports = []
    threads = []
    for address in address_list:
        threads.append(Thread(target=get_online_report, args=[address, data_queue, report_type]))
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    while not data_queue.empty():
        sensor_reports.append(data_queue.get())
        data_queue.task_done()

    sensor_reports.sort()

    final_report_replacement = ""
    for report in sensor_reports:
        final_report_replacement += str(report[1]) + "\n"
    new_report = new_report.replace("{{ SensorInfoBoxes }}", final_report_replacement)
    new_report = new_report + "\n" + html_report_end

    if report_type == app_config_access.sensor_control_config.radio_report_config:
        app_cached_variables.html_config_report = new_report
        app_cached_variables.creating_config_report = False
    elif report_type == app_config_access.sensor_control_config.radio_report_test_sensors:
        app_cached_variables.html_readings_report = new_report
        app_cached_variables.creating_readings_report = False
    elif report_type == app_config_access.sensor_control_config.radio_report_sensors_latency:
        app_cached_variables.html_latency_report = new_report
        app_cached_variables.creating_latency_report = False
    else:
        app_cached_variables.html_system_report = new_report
        app_cached_variables.creating_system_report = False
