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
import re
from operations_modules import logger
from ipaddress import ip_address as _check_ip_address
from operations_modules.app_cached_variables import no_sensor_present
from operations_modules.app_generic_functions import check_for_port_in_address


def text_is_alphanumeric(text_string):
    """
    Returns True if provided text only uses Alphanumeric characters.
    Otherwise returns False.
    """
    if text_string.isalnum():
        return True
    else:
        return False


def ip_address_is_valid(ip_address):
    ip_address_tweaked = ip_address.replace(":", "a")
    ip_address_tweaked = ip_address_tweaked.replace(".", "a")
    if ip_address != "" and text_is_alphanumeric(ip_address_tweaked):
        if check_for_port_in_address(ip_address):
            return True
        else:
            try:
                if _check_ip_address(ip_address):
                    return True
            except Exception as error:
                logger.network_logger.debug("Validating Address Failed: " + str(error))
    return False


def subnet_mask_is_valid(subnet_mask):
    subnet_ok = False
    count = 8
    while count <= 30:
        good_subnet = "/" + str(count)
        if subnet_mask == good_subnet:
            subnet_ok = True
        count += 1
    return subnet_ok


def wireless_ssid_is_valid(text_ssid):
    """
    Returns True if provided text only uses Alphanumeric characters, spaces, underscores and dashes.
    Otherwise returns False.
    """
    if re.match(r'^[a-zA-Z0-9][ A-Za-z0-9_-]*$', text_ssid):
        return True
    else:
        return False


def text_has_no_double_quotes(text_string):
    if text_string.find('"') is not -1:
        return False
    else:
        return True


def hostname_is_valid(text_hostname):
    """
    Returns True if provided text only uses Alphanumeric characters plus underscores and dashes.
    Otherwise returns False.
    """
    if text_hostname is None:
        return False
    if re.match(r'^[a-zA-Z0-9_-]*$', text_hostname):
        return True
    return False


def valid_sensor_reading(reading):
    if reading == no_sensor_present:
        return False
    return True
