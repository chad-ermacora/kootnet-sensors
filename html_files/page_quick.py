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


def get_page_start():
    logger.primary_logger.debug("Retrieved Quick Links HTML Page Start")
    sensor_hostname = sensors.get_hostname()
    sensor_ip = sensors.get_ip()

    page_start = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Local Sensor Management</title>
        <style>
            body {
                background-color: #000000;
                white-space: nowrap;
            }
        </style>
    </head>
    <body>
    <h1 style="color: red;"><strong><span style="text-decoration: underline;">
    """ + "Kootnet Sensor: " + sensor_hostname + " / " + sensor_ip + "</span></strong></h1>"
    return page_start


def get_system():
    logger.primary_logger.debug("Retrieved Quick Links HTML Page System")
    style_name_start = "<span style='color: #00ffff;'>"
    style_data_start = "<span style='background-color: #ccffcc;'>"
    style_end = "</span>"
    html_divider = "<span style='color: #ffffff;'> || </span>"
    html_colon = "<span style='color: #ffffff;'>: </span>"

    sensor_hostname = sensors.get_hostname()
    sensor_ip = sensors.get_ip()
    sensor_temperature = str(round(sensors.get_cpu_temperature(), 2))
    sensor_last_updated = sensors.get_last_updated()
    sensor_datetime = sensors.get_system_datetime()
    sensor_uptime_str = sensors.get_uptime_str()
    sensor_db_size = str(sensors.get_db_size())
    sensor_installed_sensors = configuration_main.installed_sensors.get_installed_names_str()

    page_start = """<p><strong><span style="text-decoration: underline; background-color: #00ffff;">""" + \
                 "System" + "</span></strong></p>"

    return_page_part1 = "<p>" + html_divider + \
                        style_name_start + "HostName" + style_end + html_colon + \
                        style_data_start + sensor_hostname + style_end + html_divider + \
                        style_name_start + "IP" + style_end + html_colon + \
                        style_data_start + sensor_ip + style_end + html_divider + \
                        style_name_start + "System Temperature" + style_end + html_colon + \
                        style_data_start + sensor_temperature + " °C" + style_end + html_divider + \
                        style_name_start + "SQL Database Size" + style_end + html_colon + \
                        style_data_start + sensor_db_size + " MB" + style_end + html_divider + "</p>"

    return_page_part2 = "<p>" + html_divider + \
                        style_name_start + "Sensor Date & Time" + style_end + html_colon + \
                        style_data_start + sensor_datetime + style_end + html_divider + \
                        style_name_start + "Sensor Uptime" + style_end + html_colon + \
                        style_data_start + sensor_uptime_str + style_end + html_divider + "</p>"

    return_page_part3 = "<p>" + html_divider + \
                        style_name_start + "Installed Sensors" + style_end + html_colon + \
                        style_data_start + sensor_installed_sensors + style_end + html_divider + "</p>"

    return_page_part4 = "<p>" + html_divider + \
                        style_name_start + "Version" + style_end + html_colon + \
                        style_data_start + software_version.version + style_end + html_divider + \
                        style_name_start + "Last Updated" + style_end + html_colon + \
                        style_data_start + sensor_last_updated + style_end + html_divider + "</p>"

    return_page = page_start + return_page_part1 + return_page_part2 + return_page_part3 + return_page_part4
    return return_page


def get_configuration():
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


def get_page_links():
    logger.primary_logger.debug("Retrieved Quick Links HTML Page Links")
    quick_links_html_links = """
    <H2 style="color: #00ffff;"><u>Live Sensor Readings</u></H2>
    <p><span style='background-color: #ccffcc;'><a href="/TestSensor" target="_blank">Sensor Readings</a></span></p>
    
    <H2 style="color: #00ffff;"><u>Logs</u></H2>
    <p><span style='background-color: #ccffcc;'><a href="/GetPrimaryLogHTML" target="_blank">Primary Log</a></span></p>
    <p><span style='background-color: #ccffcc;'><a href="/GetNetworkLogHTML" target="_blank">Network Log</a></span></p>
    <p><span style='background-color: #ccffcc;'><a href="/GetSensorsLogHTML" target="_blank">Sensors Log</a></span></p>

    <H2 style="color: #00ffff;"><u>Downloads</u></H2>
    <p><span style='background-color: #ccffcc;'><a href="/GetVarianceConfiguration" target="_blank">Download Trigger Variance Configuration</a></span></p>
    <p><span style='background-color: #ccffcc;'><a href="/DownloadSQLDatabase" target="_blank">Download Sensor SQL Database</a></span></p>
    
    <H2 style="color: #00ffff;"><u>Initiate Sensor Upgrade</u></H2>
    <p><span style='background-color: #ccffcc;'><a href="/UpgradeSMB" target="_blank">Upgrade Sensor over SMB</a></span></p>
    <p><span style='background-color: #ccffcc;'><a href="/UpgradeOnline-not" target="_blank">Upgrade Sensor over HTTP</a></span></p>
    """
    return quick_links_html_links


def get_html_page_end():
    logger.primary_logger.debug("Retrieved Quick Links HTML Page End")
    quick_links_html_end = "</body></html>"
    return quick_links_html_end
