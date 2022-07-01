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
from time import sleep
from operations_modules import logger
from operations_modules.app_generic_functions import thread_function
from operations_modules.app_generic_disk import get_file_content
from operations_modules import file_locations
from operations_modules import app_cached_variables
from operations_modules import network_ip

default_wpa_file_content = """
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
country={{ Country }}
"""
wifi_type_secured = "WPA-PSK WPA-EAP SAE"


class CreateWifiInterface:
    def __init__(self, country_code, wpa_supplicant_file=None):
        if wpa_supplicant_file is None:
            wpa_supplicant_file = file_locations.wifi_config_file
        self.wpa_supplicant_file = wpa_supplicant_file

        self.country_code = country_code
        self.current_wifi_networks_dic = {}
        self._update_wifi_networks()

    def get_network_ssid_list(self):
        ssid_return_list = []
        for index, name in self.current_wifi_networks_dic.items():
            ssid_return_list.append(index)
        return ssid_return_list

    def add_wifi_network(self, ssid, pass_key=None):
        if pass_key is None or pass_key == "False":
            self.current_wifi_networks_dic[ssid] = False
        else:
            self.current_wifi_networks_dic[ssid] = pass_key
        self._save_wpa_config()

    def remove_wifi_network(self, ssid):
        if ssid in self.current_wifi_networks_dic:
            del self.current_wifi_networks_dic[ssid]
        self._save_wpa_config()

    def _save_wpa_config(self):
        wpa_cleaned_content = self._get_wpa_file_cleaned()
        for network_name, pass_key in self.current_wifi_networks_dic.items():
            if pass_key:
                wpa_cleaned_content += f'\nnetwork={{\n ssid="{network_name}"\n scan_ssid=1\n' + \
                                       f' key_mgmt={wifi_type_secured}\n psk="{pass_key}"\n}}'
            else:
                wpa_cleaned_content += f'\nnetwork={{\n ssid="{network_name}"\n scan_ssid=1\n key_mgmt=NONE\n}}'

        with open(self.wpa_supplicant_file, "w") as wpa_supplicant_file:
            wpa_supplicant_file.write(wpa_cleaned_content)
        reset_wifi_connection()

    def _get_wpa_file_cleaned(self):
        lines_to_remove = []
        final_wpa_file = ""

        with open(self.wpa_supplicant_file, "r") as wpa_supplicant_file:
            wpa_supplicant_line_list = wpa_supplicant_file.readlines()
            for index, line in enumerate(wpa_supplicant_line_list):
                if line.strip().lower()[:7] == "country":
                    lines_to_remove.append(index)
                elif line.strip().lower()[:7] == "network":
                    lines_to_remove.append(index)

                    index2 = index + 1
                    for new_line in wpa_supplicant_line_list[index + 1:]:
                        lines_to_remove.append(index2)
                        index2 += 1
                        new_line = new_line.strip()
                        if new_line == "}":
                            break
            if len(lines_to_remove) > 0:
                for index, line in enumerate(wpa_supplicant_line_list):
                    if index not in lines_to_remove:
                        final_wpa_file += line

        final_wpa_file = final_wpa_file.strip()
        if final_wpa_file == "":
            final_wpa_file = default_wpa_file_content.replace("{{ Country }}", self.country_code)
        else:
            final_wpa_file = f"country={self.country_code}\n" + final_wpa_file
        return final_wpa_file

    def _update_wifi_networks(self):
        new_wifi_networks_dic = {}
        try:
            if os.path.isfile(self.wpa_supplicant_file):
                with open(self.wpa_supplicant_file, "r") as wpa_supplicant_file:
                    wpa_supplicant_line_list = wpa_supplicant_file.readlines()
                    for index, line in enumerate(wpa_supplicant_line_list):
                        if line.strip().lower()[:4] == "ssid":
                            found_ssid = line.split("=")[1].strip()
                            if found_ssid[0].replace("'", '"') == '"' and found_ssid[-1].replace("'", '"') == '"':
                                found_ssid = found_ssid[1:-1]
                            found_key_pass = False
                            for line2 in wpa_supplicant_line_list[index:]:
                                line2 = line2.replace(" ", "")
                                if line2[:3].lower() == "psk":
                                    pass_key = line2[4:].strip()
                                    if pass_key[0].replace("'", '"') == '"' and pass_key[-1].replace("'", '"') == '"':
                                        pass_key = pass_key[1:-1]
                                    found_key_pass = pass_key
                                elif line2 == "}":
                                    break
                            new_wifi_networks_dic[found_ssid] = str(found_key_pass)
        except Exception as error:
            logger.network_logger.error("Get Wifi SSIDs: " + str(error))
        self.current_wifi_networks_dic = new_wifi_networks_dic


def reset_wifi_connection():
    thread_function(_reset_wifi_connection)


def _get_wifi_device():
    net_device_name = _get_wifi_device_name(network_ip.get_network_devices_list(online_devices_only=True))
    if net_device_name == "":
        net_device_name = _get_wifi_device_name(network_ip.get_network_devices_list(online_devices_only=False))
    return net_device_name


def _get_wifi_device_name(net_devices_list):
    net_device_name = ""
    for device_name in net_devices_list:
        device_name = device_name.strip()
        if device_name[:2] == "wl":
            net_device_name = device_name
            break
    return net_device_name


def _get_wifi_country_code():
    """
    Checks the wpa_supplicant.conf file for the set country code and returns it.
    If not found, returns an empty string.
    """
    if app_cached_variables.running_with_root:
        wifi_config_lines = get_file_content(file_locations.wifi_config_file).split("\n")
        for line in wifi_config_lines:
            line_stripped = line.strip()
            if line_stripped[:8] == "country=":
                return line_stripped[8:].strip()
    return "CA"


def _reset_wifi_connection():
    try:
        net_device_name = _get_wifi_device()
        if net_device_name == "":
            logger.network_logger.warning(f"Resetting Wifi Connection: Wifi adapter not found")
        else:
            subprocess.check_output(f"sudo wpa_cli -i {net_device_name} reconfigure", shell=True)
            sleep(1)
            network_ip.reset_network_device(net_device_name)
    except Exception as error:
        logger.network_logger.error("Network Wifi Reset: " + str(error))


wifi_networks_interface = CreateWifiInterface(_get_wifi_country_code())
