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
from operations_modules import sensors
from operations_modules import software_version
from operations_modules import configuration_main
from html_files import html_templates


def _get_page_title():
    """
     Returns the beginning of the Sensor's Quick HTML page.
     It contains up to and including the page title made up of the Local Name and IP.
    """
    logger.primary_logger.debug("Retrieved Quick Links HTML Page Start")
    sensor_hostname = sensors.get_hostname()
    sensor_ip = sensors.get_ip()

    page_start = html_templates.quick_page_title_start + \
                 sensor_hostname + " / " + sensor_ip + \
                 html_templates.quick_page_title_end
    return page_start


def _get_page_system():
    """ Returns a HTML formatted string of the Local Sensor's System Information. """
    logger.primary_logger.debug("Retrieved Quick Links HTML Page System")
    style_name_start = "<span style='color: #00ffff;'>"
    style_data_start = "<span style='background-color: #ccffcc;'>"
    style_end = "</span>"
    html_divider = "<span style='color: #ffffff;'> || </span>"
    html_colon = "<span style='color: #ffffff;'>: </span>"

    sensor_hostname = sensors.get_hostname()
    sensor_ip = sensors.get_ip()
    sensor_free_disk = str(sensors.get_disk_usage_percent())
    sensor_free_memory = str(sensors.get_memory_usage_percent())
    sensor_last_updated = sensors.get_last_updated()
    sensor_datetime = sensors.get_system_datetime()
    sensor_uptime_str = sensors.get_uptime_str()
    sensor_db_size = str(sensors.get_db_size())
    sensor_installed_sensors = configuration_main.installed_sensors.get_installed_names_str()

    try:
        sensor_temperature = str(round(sensors.get_cpu_temperature(), 2))
    except Exception as error:
        logger.primary_logger.error("CPU Temperature Error: " + str(error))
        sensor_temperature = "Error"

    page_start = """<p><strong><span style="text-decoration: underline; background-color: #00ffff;">""" + \
                 "System" + "</span></strong></p>"

    return_page_part1 = "<p>" + html_divider + \
                        style_name_start + "HostName" + style_end + html_colon + \
                        style_data_start + sensor_hostname + style_end + html_divider + \
                        style_name_start + "IP" + style_end + html_colon + \
                        style_data_start + sensor_ip + style_end + html_divider + \
                        style_name_start + "System Temperature" + style_end + html_colon + \
                        style_data_start + sensor_temperature + " °C" + style_end + \
                        html_divider + "</p>"

    return_page_part2 = "<p>" + html_divider + \
                        style_name_start + "SQL Database Size" + style_end + html_colon + \
                        style_data_start + sensor_db_size + " MB" + style_end + html_divider + \
                        style_name_start + "Drive Usage" + style_end + html_colon + \
                        style_data_start + sensor_free_disk + " %" + style_end + html_divider + \
                        style_name_start + "RAM Usage" + style_end + html_colon + \
                        style_data_start + sensor_free_memory + " %" + style_end + \
                        html_divider + "</p>"

    return_page_part3 = "<p>" + html_divider + \
                        style_name_start + "Sensor Date & Time" + style_end + html_colon + \
                        style_data_start + sensor_datetime + style_end + html_divider + \
                        style_name_start + "Sensor Uptime" + style_end + html_colon + \
                        style_data_start + sensor_uptime_str + style_end + \
                        html_divider + "</p>"

    return_page_part4 = "<p>" + html_divider + \
                        style_name_start + "Installed Sensors" + style_end + html_colon + \
                        style_data_start + sensor_installed_sensors + style_end + \
                        html_divider + "</p>"

    return_page_part5 = "<p>" + html_divider + \
                        style_name_start + "Version" + style_end + html_colon + \
                        style_data_start + software_version.version + style_end + html_divider + \
                        style_name_start + "Last Updated" + style_end + html_colon + \
                        style_data_start + sensor_last_updated + style_end + \
                        html_divider + "</p>"

    return_page = page_start + return_page_part1 + return_page_part2 + return_page_part3 + return_page_part4 + \
                  return_page_part5
    return return_page


def _get_page_configuration():
    """ Returns a HTML formatted string of the Local Sensor's Configuration. """
    logger.primary_logger.debug("Retrieved Quick Links HTML Page Config")
    style_name_start = "<span style='color: #00ffff;'>"
    style_data_start = "<span style='background-color: #ccffcc;'>"
    style_end = "</span>"
    html_divider = "<span style='color: #ffffff;'> || </span>"
    html_colon = "<span style='color: #ffffff;'>: </span>"

    if configuration_main.current_config.enable_debug_logging:
        debug_logging = "Enabled"
    else:
        debug_logging = "Disabled"

    if configuration_main.current_config.enable_interval_recording:
        interval_enabled = "Enabled"
    else:
        interval_enabled = "Disabled"

    interval_duration = str(configuration_main.current_config.sleep_duration_interval)

    if configuration_main.current_config.enable_trigger_recording:
        trigger_enabled = "Enabled"
    else:
        trigger_enabled = "Disabled"

    if configuration_main.current_config.enable_custom_temp:
        temperature_offset_custom = "Enabled"
    else:
        temperature_offset_custom = "Disabled"

    temperature_offset_value = str(configuration_main.current_config.temperature_offset)

    page_start = """<p><strong><span style="text-decoration: underline; background-color: #00ffff;">""" + \
                 "Configurations" + "</span></strong></p>"

    return_page_part1 = "<p>" + html_divider + \
                        style_name_start + "Debug Logging" + style_end + html_colon + \
                        style_data_start + debug_logging + style_end + html_divider + \
                        style_name_start + "Interval Recording" + style_end + html_colon + \
                        style_data_start + interval_enabled + style_end + html_divider + \
                        style_name_start + "Trigger Recording" + style_end + html_colon + \
                        style_data_start + trigger_enabled + style_end + html_divider + "</p>"

    return_page_part2 = "<p>" + html_divider + \
                        style_name_start + "Manual Temperature Offset" + style_end + html_colon + \
                        style_data_start + temperature_offset_custom + style_end + html_divider + \
                        style_name_start + "Current Temperature Offset" + style_end + html_colon + \
                        style_data_start + temperature_offset_value + style_end + html_divider + \
                        style_name_start + "Interval Delay in Seconds" + style_end + html_colon + \
                        style_data_start + interval_duration + style_end + html_divider + "</p>"

    return_page = page_start + return_page_part1 + return_page_part2
    return return_page


def get_quick_html_page():
    """ Combines all parts of the Sensor's Quick HTML Page and returns it. """
    return_page = _get_page_title() + \
                  _get_page_system() + \
                  _get_page_configuration() + \
                  html_templates.quick_page_links + \
                  html_templates.quick_page_final_end

    return return_page
