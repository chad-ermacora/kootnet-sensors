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
import logging
import os
import psutil
import time
import requests
from io import BytesIO
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED
from threading import Thread
from operations_modules import logger
from operations_modules import app_cached_variables
from operations_modules import network_ip
from operations_modules import network_wifi

logging.captureWarnings(True)


def get_file_content(load_file, open_type="r"):
    """ Loads provided file and returns it's content. """
    logger.primary_logger.debug("Loading File: " + str(load_file))

    if os.path.isfile(load_file):
        try:
            loaded_file = open(load_file, open_type)
            file_content = loaded_file.read()
            loaded_file.close()
        except Exception as error:
            file_content = ""
            logger.primary_logger.error("Unable to load " + load_file + " - " + str(error))
        return file_content
    else:
        logger.primary_logger.error(load_file + " not found")


def write_file_to_disk(file_location, file_content, open_type="w"):
    """ Writes provided file and content to local disk. """
    logger.primary_logger.debug("Writing content to " + str(file_location))
    try:
        write_file = open(file_location, open_type)
        write_file.write(file_content)
        write_file.close()
    except Exception as error:
        logger.primary_logger.error("Unable to open or write file: " + str(file_location) + " - " + str(error))


def thread_function(function, args=None):
    if args:
        system_thread = Thread(target=function, args=[args])
    else:
        system_thread = Thread(target=function)

    system_thread.daemon = True
    system_thread.start()


def update_cached_variables(sensor_access):
    app_cached_variables.ip = sensor_access.get_ip()
    app_cached_variables.total_ram_memory = psutil.virtual_memory().total / 1000000
    if app_cached_variables.total_ram_memory > 1000:
        app_cached_variables.total_ram_memory = app_cached_variables.total_ram_memory / 1000
        app_cached_variables.total_ram_memory_size_type = " GB"
        if app_cached_variables.total_ram_memory > 1000:
            app_cached_variables.total_ram_memory = app_cached_variables.total_ram_memory / 1000
            app_cached_variables.total_ram_memory_size_type = " TB"
    app_cached_variables.total_ram_memory = round(app_cached_variables.total_ram_memory, 2)

    if sensor_access.get_operating_system_name()[:8] == "Raspbian":
        try:
            wifi_config_lines = network_wifi.get_wifi_config_from_file().split("\n")
        except Exception as error:
            logger.primary_logger.error("Error checking WiFi configuration: " + str(error))
            wifi_config_lines = []

        app_cached_variables.wifi_country_code = network_wifi.get_wifi_country_code(wifi_config_lines)
        app_cached_variables.wifi_ssid = network_wifi.get_wifi_ssid(wifi_config_lines)
        app_cached_variables.wifi_security_type = network_wifi.get_wifi_security_type(wifi_config_lines)
        app_cached_variables.wifi_psk = network_wifi.get_wifi_psk(wifi_config_lines)

        try:
            dhcpcd_config_lines = network_ip.get_dhcpcd_config_from_file().split("\n")
        except Exception as error:
            logger.primary_logger.error("Error checking dhcpcd.conf: " + str(error))
            dhcpcd_config_lines = []

        if not network_ip.check_for_dhcp(dhcpcd_config_lines):
            app_cached_variables.ip = network_ip.get_dhcpcd_ip(dhcpcd_config_lines)
            app_cached_variables.ip_subnet = network_ip.get_subnet(dhcpcd_config_lines)
            app_cached_variables.gateway = network_ip.get_gateway(dhcpcd_config_lines)
            app_cached_variables.dns1 = network_ip.get_dns(dhcpcd_config_lines)
            app_cached_variables.dns2 = network_ip.get_dns(dhcpcd_config_lines, dns_server=1)

    app_cached_variables.program_last_updated = sensor_access.get_last_updated()
    app_cached_variables.reboot_count = str(sensor_access.get_system_reboot_count())
    app_cached_variables.operating_system_name = sensor_access.get_operating_system_name()
    app_cached_variables.hostname = sensor_access.get_hostname()


def get_http_sensor_reading(http_ip, http_port="10065", command="CheckOnlineStatus"):
    """ Returns requested sensor data (based on the provided command data). """
    try:
        url = "https://" + http_ip + ":" + http_port + "/" + command
        tmp_return_data = requests.get(url=url,
                                       timeout=2,
                                       auth=(app_cached_variables.http_login, app_cached_variables.http_password),
                                       verify=False)
        return tmp_return_data.text
    except Exception as error:
        logger.network_logger.debug("Remote Sensor Data Request - HTTPS GET Error for " + http_ip + ": " + str(error))
        return "Error"


def get_http_sensor_file(http_ip, command, http_port="10065"):
    """ Returns requested sensor file (based on the provided command data). """
    try:
        url = "https://" + http_ip + ":" + http_port + "/" + command
        tmp_return_data = requests.get(url=url,
                                       timeout=(2, 120),
                                       auth=(app_cached_variables.http_login, app_cached_variables.http_password),
                                       verify=False)
        return tmp_return_data.content
    except Exception as error:
        logger.network_logger.debug("Remote Sensor File Request - HTTPS GET Error for " + http_ip + ": " + str(error))
        return "Error"


def http_display_text_on_sensor(text_message, http_ip, http_port="10065"):
    """ Returns requested sensor data (based on the provided command data). """
    try:
        url = "https://" + http_ip + ":" + http_port + "/DisplayText"
        requests.put(url=url,
                     timeout=2,
                     auth=(app_cached_variables.http_login, app_cached_variables.http_password),
                     data={'command_data': text_message},
                     verify=False)
    except Exception as error:
        logger.network_logger.error("Unable to display text on Sensor: " + str(error))


def zip_files(file_names_list, files_content_list, save_type="get_bytes_io", file_location=""):
    if save_type == "get_bytes_io":
        return_zip_file = BytesIO()
    else:
        return_zip_file = file_location
    date_time = time.localtime(time.time())[:6]

    file_meta_data_list = []
    for name in file_names_list:
        name_data = ZipInfo(name)
        name_data.date_time = date_time
        name_data.compress_type = ZIP_DEFLATED
        file_meta_data_list.append(name_data)
    with ZipFile(return_zip_file, "w") as zip_file:
        for file_meta_data, file_content in zip(file_meta_data_list, files_content_list):
            zip_file.writestr(file_meta_data, file_content)
    if save_type == "get_bytes_io":
        return_zip_file.seek(0)
        return return_zip_file
    return "Saved to disk"


def get_data_queue_items():
    que_data = []
    while not app_cached_variables.data_queue.empty():
        que_data.append(app_cached_variables.data_queue.get())
        app_cached_variables.data_queue.task_done()
    return que_data


def replace_text_lists(text_file, old_list, new_list):
    for old_text, new_text in zip(old_list, new_list):
        text_file = text_file.replace(old_text, new_text)
    return text_file


def clear_zip_names():
    app_cached_variables.sc_reports_zip_name = ""
    app_cached_variables.sc_logs_zip_name = ""
    if app_cached_variables.sc_databases_zip_in_memory:
        app_cached_variables.sc_databases_zip_name = ""
    if app_cached_variables.sc_big_zip_in_memory:
        app_cached_variables.sc_big_zip_name = ""


def save_to_memory_ok(write_size):
    if psutil.virtual_memory().available > (write_size + 25000):
        return True
    return False
