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
from ipaddress import ip_address as _check_ip_address
from operations_modules import logger
from operations_modules.http_generic_network import check_for_port_in_address, get_ip_and_port_split


def ip_address_is_valid(ip_address):
    """ Checks if an IPv4/6 address is valid. Returns True for valid and False for Invalid. """
    try:
        if check_for_port_in_address(ip_address):
            ip_address, port = get_ip_and_port_split(ip_address)
        ip_address = ip_address.replace("[", "")
        ip_address = ip_address.replace("]", "")
        if _check_ip_address(ip_address):
            return True
    except Exception as error:
        logger.network_logger.debug("IP Failed Validation Check: " + str(error))
    return False


def sensor_address_is_valid(ip_or_dns_address):
    try:
        if check_for_port_in_address(ip_or_dns_address):
            ip_or_dns_address, port = get_ip_and_port_split(ip_or_dns_address)
            ip_or_dns_address = ip_or_dns_address.replace("[", "")
            ip_or_dns_address = ip_or_dns_address.replace("]", "")
        if re.match(r'^[a-zA-Z0-9_:.-]*$', ip_or_dns_address):
            return True
    except Exception as error:
        logger.network_logger.debug("Sensor Address Failed Validation Check: " + str(error))
    return False


def subnet_mask_is_valid(subnet_mask):
    """ Checks if a subnet mask if valid.  Returns True for valid and False for Invalid. """
    try:
        if 0 <= int(subnet_mask[1:]) < 32:
            return True
    except Exception as error:
        logger.network_logger.debug("Subnet Mask Failed Validation Check: " + str(error))
    return False


def wireless_ssid_is_valid(text_ssid):
    """
    Checks if a wireless SSID is valid. Returns True for valid and False for Invalid.
    Checks that text only uses Alphanumeric characters, spaces, underscores and dashes.
    """
    if re.match(r'^[a-zA-Z0-9][A-Za-z0-9_-]*$', text_ssid):
        return True
    return False


def hostname_is_valid(text_hostname):
    """
    Checks for valid Linux Hostname and returns True, else, False
    :param text_hostname: new hostname string
    :return: True if hostname is valid, else, False
    """
    if text_hostname is not None:
        if re.match(r'^[a-zA-Z0-9_-]*$', text_hostname):
            if 1 < len(text_hostname) < 64:
                if text_hostname[0] != "-":
                    return True
    return False


def email_is_valid(email):
    regex = "^(?!\.)[0-9a-zA-Z\.]+(?<!\.)@(?!\.)[0-9a-zA-Z\.]+(?<!\.)$"
    if re.search(regex, str(email)):
        return True
    return False


def validate_smb_username(username):
    if username is not None:
        if username.isalnum():
            return True
    return False


def validate_smb_password(password):
    # ToDo: I'm expecting there to be other characters that should not be used, will add those later
    invalid_characters_list = ["'"]
    password_valid = True
    if password is None or password == "":
        password_valid = False
    else:
        for invalid_character in invalid_characters_list:
            if invalid_character in password:
                password_valid = False
    return password_valid
