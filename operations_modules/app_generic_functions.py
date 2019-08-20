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
from operations_modules import logger
from operations_modules import app_cached_variables
from operations_modules import network_ip
from operations_modules import network_wifi


def get_file_content(load_file):
    """ Loads provided file and returns it's content. """
    logger.primary_logger.debug("Loading File: " + str(load_file))

    if os.path.isfile(load_file):
        try:
            loaded_file = open(load_file, "r")
            file_content = loaded_file.read()
            loaded_file.close()
        except Exception as error:
            file_content = ""
            logger.primary_logger.error("Unable to load " + load_file + " - " + str(error))
        return file_content
    else:
        logger.primary_logger.error(load_file + " not found")


def write_file_to_disk(file_location, file_content):
    """ Writes provided file and content to local disk. """
    logger.primary_logger.debug("Writing content to " + str(file_location))
    try:
        write_file = open(file_location, 'w')
        write_file.write(file_content)
        write_file.close()
    except Exception as error:
        logger.primary_logger.error("Unable to open or write file: " + str(file_location) + " - " + str(error))


def update_cached_variables(sensor_access):
    try:
        wifi_config_lines = network_wifi.get_wifi_config_from_file().split("\n")
    except Exception as error:
        logger.primary_logger.error("Error checking WiFi configuration: " + str(error))
        wifi_config_lines = []

    try:
        dhcpcd_config_lines = network_ip.get_dhcpcd_config_from_file().split("\n")
    except Exception as error:
        logger.primary_logger.error("Error checking dhcpcd.conf: " + str(error))
        dhcpcd_config_lines = []

    app_cached_variables.program_last_updated = sensor_access.get_last_updated()
    app_cached_variables.reboot_count = str(sensor_access.get_system_reboot_count())

    app_cached_variables.hostname = sensor_access.get_hostname()

    if network_ip.check_for_dhcp(dhcpcd_config_lines):
        app_cached_variables.ip = sensor_access.get_ip()
    else:
        app_cached_variables.ip = network_ip.get_dhcpcd_ip(dhcpcd_config_lines)

    app_cached_variables.gateway = network_ip.get_gateway(dhcpcd_config_lines)
    app_cached_variables.dns1 = network_ip.get_dns(dhcpcd_config_lines)
    app_cached_variables.dns2 = network_ip.get_dns(dhcpcd_config_lines, dns_server=1)

    app_cached_variables.wifi_country_code = network_wifi.get_wifi_country_code(wifi_config_lines)
    app_cached_variables.wifi_ssid = network_wifi.get_wifi_ssid(wifi_config_lines)
    app_cached_variables.wifi_security_type = network_wifi.get_wifi_security_type(wifi_config_lines)
    app_cached_variables.wifi_psk = network_wifi.get_wifi_psk(wifi_config_lines)
