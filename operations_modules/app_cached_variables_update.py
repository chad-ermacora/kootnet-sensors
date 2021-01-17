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
import os
import psutil
from time import sleep
from operations_modules import logger
from operations_modules import file_locations
from operations_modules import app_cached_variables
from operations_modules.app_generic_functions import thread_function, get_file_content
from operations_modules import network_ip
from operations_modules import network_wifi

from sensor_modules import sensor_access


def update_cached_variables():
    """ Updates app_cached_variables.py variables. """
    app_cached_variables.total_ram_memory = psutil.virtual_memory().total / 1000000
    if app_cached_variables.total_ram_memory > 1000:
        app_cached_variables.total_ram_memory = app_cached_variables.total_ram_memory / 1000
        app_cached_variables.total_ram_memory_size_type = " GB"
        if app_cached_variables.total_ram_memory > 1000:
            app_cached_variables.total_ram_memory = app_cached_variables.total_ram_memory / 1000
            app_cached_variables.total_ram_memory_size_type = " TB"
    app_cached_variables.total_ram_memory = round(app_cached_variables.total_ram_memory, 2)

    os_name = sensor_access.get_operating_system_name()
    if os_name[:8] == "Raspbian":
        try:
            wifi_config_lines = get_file_content(file_locations.wifi_config_file).split("\n")
        except Exception as error:
            logger.primary_logger.warning("Error checking WiFi configuration: " + str(error))
            wifi_config_lines = []

        app_cached_variables.wifi_country_code = network_wifi.get_wifi_country_code(wifi_config_lines)
        app_cached_variables.wifi_ssid = network_wifi.get_wifi_ssid(wifi_config_lines)
        app_cached_variables.wifi_security_type = network_wifi.get_wifi_security_type(wifi_config_lines)
        app_cached_variables.wifi_psk = network_wifi.get_wifi_psk(wifi_config_lines)

        try:
            dhcpcd_config_lines = get_file_content(file_locations.dhcpcd_config_file).split("\n")
        except Exception as error:
            logger.primary_logger.warning("Error checking dhcpcd.conf: " + str(error))
            dhcpcd_config_lines = []

        if not network_ip.check_for_dhcp(dhcpcd_config_lines):
            app_cached_variables.ip = network_ip.get_dhcpcd_ip(dhcpcd_config_lines)
            app_cached_variables.ip_subnet = network_ip.get_subnet(dhcpcd_config_lines)
            app_cached_variables.gateway = network_ip.get_gateway(dhcpcd_config_lines)
            app_cached_variables.dns1 = network_ip.get_dns(dhcpcd_config_lines)
            app_cached_variables.dns2 = network_ip.get_dns(dhcpcd_config_lines, dns_server=1)

    app_cached_variables.program_last_updated = sensor_access.get_last_updated()
    app_cached_variables.reboot_count = str(sensor_access.get_system_reboot_count())
    app_cached_variables.operating_system_name = os_name
    update_uploaded_databases_names_list()


def start_ip_hostname_refresh():
    thread_function(_ip_hostname_refresh)


def _ip_hostname_refresh():
    """
    Updates app_cached_variables.py variables that may change while running.
    Gives 5 seconds before updating the variables within to allow network to be up.
    """
    sleep(5)
    while True:
        app_cached_variables.ip = sensor_access.get_ip()
        app_cached_variables.hostname = sensor_access.get_hostname()
        sleep(3600)


def update_uploaded_databases_names_list():
    app_cached_variables.uploaded_databases_list = []
    try:
        _, _, filenames = next(os.walk(file_locations.uploaded_databases_folder))
        for database_name in filenames:
            app_cached_variables.uploaded_databases_list.append(database_name)
    except Exception as custom_db_error:
        logger.primary_logger.warning(" -- Make Directory Error: " + str(custom_db_error))
