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
# TODO: Add ability to check for Ethernet vs. Wireless in all relevant areas


def check_for_dhcp(dhcpcd_config_lines):
    """
    Checks the dhcpcd.conf file for a static IP address.
    Returns True if no static IPs are found, otherwise returns false.
    """
    if dhcpcd_config_lines is not None:
        dhcp_status = True
        for line in dhcpcd_config_lines:
            line_stripped = line.strip()
            if line_stripped[:18] == "static ip_address=":
                dhcp_status = False
        return dhcp_status
    return False


def get_dhcpcd_ip(dhcpcd_config_lines):
    """
    Checks the dhcpcd.conf file for a static IP address.
    Returns the IP address if a static IP is found, otherwise returns a empty string.
    """
    if dhcpcd_config_lines is not None:
        for line in dhcpcd_config_lines:
            line_stripped = line.strip()
            if line_stripped[:18] == "static ip_address=":
                ip_address = line_stripped[18:].split("/")[0]
                return ip_address
    return ""


def get_gateway(dhcpcd_config_lines):
    """
    Checks the dhcpcd.conf file for a static gateway address (router).
    Returns the IP address of said gateway if found, otherwise returns a empty string.
    """
    if dhcpcd_config_lines is not None:
        for line in dhcpcd_config_lines:
            line_stripped = line.strip()
            if line_stripped[:15] == "static routers=":
                return line_stripped[15:]
    return ""


def get_subnet(dhcpcd_config_lines):
    """
    Checks the dhcpcd.conf file for a static IP address.
    Returns the Subnet Mask of a static IP if found, otherwise returns a empty string.
    """
    if dhcpcd_config_lines is not None:
        for line in dhcpcd_config_lines:
            line_stripped = line.strip()
            if line_stripped[:18] == "static ip_address=":
                subnet_mask = "/" + line_stripped[18:].split("/")[1]
                return subnet_mask
    return ""


def get_dns(dhcpcd_config_lines, dns_server=0):
    """
    Checks the dhcpcd.conf file for a static IP address.
    Returns the DNS server(s) IP addresses if a static IP is found, otherwise returns a empty string.
    """
    if dhcpcd_config_lines is not None:
        for line in dhcpcd_config_lines:
            line_stripped = line.strip()
            if line_stripped[:27] == "static domain_name_servers=":
                dns_list = line_stripped[27:].split(" ")
                if len(dns_list) > 1 or dns_server == 0:
                    return dns_list[dns_server]
    return ""
