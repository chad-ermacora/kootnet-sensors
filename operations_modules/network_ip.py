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
import subprocess
import shutil
from time import sleep
from operations_modules import logger
from operations_modules import file_locations
from operations_modules import app_cached_variables_update
from operations_modules.app_generic_functions import thread_function
from operations_modules.app_generic_disk import get_file_content, write_file_to_disk
from operations_modules.app_validation_checks import ip_address_is_valid, subnet_mask_is_valid

adapter_resetting = False


class CreateNetDeviceInterface:
    def __init__(self, net_device_name, auto_fill_address_info=None):
        if auto_fill_address_info is None:
            auto_fill_address_info = True

        self.dhcp_config_file = file_locations.dhcpcd_config_file

        self.net_device_name = net_device_name
        self.dhcp_set = _check_for_dhcp(self.net_device_name, self.dhcp_config_file)
        self.ip_address = ""
        self.ip_subnet = ""
        self.ip_gateway = ""
        self.ip_dns1 = ""
        self.ip_dns2 = ""

        if auto_fill_address_info:
            self.ip_address = _get_device_ip_address(net_device_name)
            self.ip_subnet = _get_device_subnet_address(net_device_name)
            self.ip_gateway = _get_gateway_address()
            dns_addresses = _get_dns_address_list()
            if len(dns_addresses) > 0:
                self.ip_dns1 = dns_addresses[0]
                if len(dns_addresses) > 1:
                    self.ip_dns2 = dns_addresses[1]

    def valid_net_addresses(self):
        if self.get_validation_msg() == "OK":
            return True
        return False

    def get_validation_msg(self):
        if not ip_address_is_valid(self.ip_address):
            return "Invalid IP Address "
        if not subnet_mask_is_valid(self.ip_subnet):
            return "Invalid IP Subnet Mask "
        if self.ip_gateway != "" and not ip_address_is_valid(self.ip_gateway):
            return "Invalid Gateway IP Address "
        if self.ip_dns1 != "" and not ip_address_is_valid(self.ip_dns1):
            return "Invalid DNS Address #1 "
        if self.ip_dns2 != "" and not ip_address_is_valid(self.ip_dns2):
            return "Invalid DNS Address #2 "
        return "OK"

    def remove_device_enable_dhcp(self):
        remove_lines = []
        final_dhcpcd_text = ""

        try:
            if os.path.isfile(self.dhcp_config_file):
                with open(self.dhcp_config_file) as dhcpcd_conf:
                    dhcpcd_conf_lines = dhcpcd_conf.readlines()
                    for index, line in enumerate(dhcpcd_conf_lines):
                        line_stripped = line.strip()
                        if line_stripped[:9] == "interface":
                            if line_stripped[10:].strip() == self.net_device_name:
                                remove_lines.append(index)
                                index2 = index + 1
                                for new_line in dhcpcd_conf_lines[index + 1:]:
                                    new_line = new_line.strip().lower()
                                    if new_line == "":
                                        index2 += 1
                                    else:
                                        start_line = new_line.strip()[:6]
                                        if start_line == "static":
                                            remove_lines.append(index2)
                                            index2 += 1
                                        else:
                                            break

                if len(remove_lines) > 0:
                    for index, line in enumerate(dhcpcd_conf_lines):
                        if index not in remove_lines:
                            final_dhcpcd_text += line
                    with open(self.dhcp_config_file, "w") as dhcpcd_conf:
                        dhcpcd_conf.write(final_dhcpcd_text)
                    reset_network_device(self.net_device_name)
        except Exception as error:
            logger.network_logger.error(f"Enable DHCP on {self.dhcp_config_file}: {error}")

    def save_static_network_config(self):
        if self.valid_net_addresses():
            try:
                if not os.path.isfile(self.dhcp_config_file):
                    logger.network_logger.warning(f"Saving dhcpcd.conf: {self.dhcp_config_file} not found")
                else:
                    self.remove_device_enable_dhcp()
                    new_dhcpcd_file_content = get_file_content(self.dhcp_config_file).strip()
                    new_dhcpcd_file_content += \
                        f"\n\ninterface {self.net_device_name}" + \
                        f"\nstatic ip_address={self.ip_address}/{self.ip_subnet}" + \
                        f"\nstatic routers={self.ip_gateway}" + \
                        f"\nstatic domain_name_servers={self.ip_dns1} {self.ip_dns2}\n\n"

                    write_file_to_disk(self.dhcp_config_file, new_dhcpcd_file_content)
                    shutil.chown(self.dhcp_config_file, "root", "netdev")
                    os.chmod(self.dhcp_config_file, 0o664)
                    reset_network_device(self.net_device_name)
                    self.dhcp_set = _check_for_dhcp(self.net_device_name, self.dhcp_config_file)
            except Exception as error:
                logger.network_logger.error(f"Saving {self.dhcp_config_file}: " + str(error))


def reset_network_device(net_device_name):
    thread_function(_reset_network_device, args=net_device_name)


def get_network_devices_list(online_devices_only=False):
    device_names_list = []
    try:
        command_text = "ip link ls"
        if online_devices_only:
            command_text += " up"
        ip_command_output = subprocess.check_output(command_text, shell=True).decode()

        for text_line in ip_command_output.strip().split("\n"):
            if text_line.strip()[0].isdigit():
                # line will be as follows. like 1: eth0: <BROADCAST,MULTICAST> ETC, ETC
                device_name = text_line.split(":")[1].strip()
                if device_name != "lo":
                    device_names_list.append(device_name)
    except Exception as error:
        logger.network_logger.error("Get Network Devices: " + str(error))
    return device_names_list


def _check_for_dhcp(net_device_name, config_location=file_locations.dhcpcd_config_file):
    """
    Checks the dhcpcd.conf file for a static IP address.
    Returns True if no static IPs are found, otherwise returns false.
    """

    try:
        if os.path.isfile(config_location):
            with open(config_location) as dhcpcd_conf:
                dhcpcd_conf_lines = dhcpcd_conf.readlines()
                for line in dhcpcd_conf_lines:
                    line_stripped = line.strip()
                    if line_stripped[:9] == "interface":
                        if line_stripped[10:].strip() == net_device_name:
                            return False
    except Exception as error:
        logger.network_logger.error("Network DHCP Check: " + str(error))
    return True


def _get_device_ip_address(net_device_name, get_version_6=False):
    return_value = _get_device_informational_value(net_device_name, "inet", get_version_6)
    new_return = return_value.split("/")
    if len(new_return) > 1:
        return new_return[0]
    return return_value


def _get_device_subnet_address(net_device_name, get_version_6=False):
    return_value = _get_device_informational_value(net_device_name, "inet", get_version_6)
    new_return = return_value.split("/")
    if len(new_return) > 1:
        return new_return[1]
    return return_value


def _get_gateway_address():
    try:
        ip_command_output = subprocess.check_output("ip r", shell=True).decode()
        ip_output_split = ip_command_output.split("\n")
        for line in ip_output_split:
            if line[:7] == "default":
                return line.split(" ")[2]
    except Exception as error:
        logger.network_logger.error("Get Network Gateway Address: " + str(error))
    return ""


def _get_dns_address_list():
    resolv_conf_file_location = "/etc/resolv.conf"
    dns_address_list = []
    try:
        if os.path.isfile(resolv_conf_file_location):
            resolv_file_content = get_file_content(resolv_conf_file_location)
            resolv_file_content_list = resolv_file_content.split("\n")
            for line in resolv_file_content_list:
                if line[:10] == "nameserver":
                    dns_address_list.append(line.split(" ")[1])
    except Exception as error:
        logger.network_logger.error("Get Network DNS Addresses: " + str(error))
    return dns_address_list


def _reset_network_device(net_device_name):
    logger.network_logger.debug(f"Network adapter {net_device_name} resetting")
    global adapter_resetting
    try:
        while adapter_resetting:
            sleep(2)
        adapter_resetting = True
        sleep(1)
        ip_command_output = subprocess.check_output(f"ip link set dev {net_device_name} down", shell=True).decode()
        logger.network_logger.debug(f"Network adapter {net_device_name} 'down': {str(ip_command_output)}")
        sleep(2)
        ip_command_output = subprocess.check_output(f"ip link set dev {net_device_name} up", shell=True).decode()
        logger.network_logger.debug(f"Network adapter {net_device_name} 'up': {str(ip_command_output)}")
        sleep(2)
        logger.network_logger.info(f"Network adapter {net_device_name} reset")
    except Exception as error:
        logger.network_logger.error("Network adapter reset: " + str(error))
    adapter_resetting = False
    app_cached_variables_update.update_cached_variables()


def _get_device_informational_value(net_device_name, info_name, get_version_6):
    net_device_info = "NA"
    try:
        if get_version_6:
            ip_command_output = subprocess.check_output("ip -6 a show " + net_device_name, shell=True).decode()
        else:
            ip_command_output = subprocess.check_output("ip -4 a show " + net_device_name, shell=True).decode()
        ip_command_list = ip_command_output.strip().split(" ")

        for index, text_line in enumerate(ip_command_list):
            if text_line.strip() == info_name:
                net_device_info = ip_command_list[index + 1]
    except Exception as error:
        logger.network_logger.error("Network Device Get Info: " + str(error))
    return net_device_info
