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
from operations_modules import file_locations


class CreateWiFiAccess:
    def __init__(self, configuration_main):
        self.configuration_main = configuration_main
        self.wifi_configuration_lines_list = get_wifi_config_from_file().split("\n")
        self.update_all_wifi_cache()

    def update_all_wifi_cache(self):
        self.configuration_main.cache_wifi_country_code = self.get_wifi_country_code()
        self.configuration_main.cache_wifi_ssid1 = self.get_wifi_ssid()
        self.configuration_main.cache_wifi_security_type1 = self.get_wifi_security_type()
        self.configuration_main.cache_wifi_psk1 = self.get_wifi_psk()

        self.configuration_main.cache_wifi_ssid2 = self.get_wifi_ssid2()
        self.configuration_main.cache_wifi_security_type2 = self.get_wifi_security_type2()
        self.configuration_main.cache_wifi_psk2 = self.get_wifi_psk2()

    def get_wifi_country_code(self):
        for line in self.wifi_configuration_lines_list:
            line_stripped = line.strip()
            if line_stripped[:8] == "country=":
                return line_stripped[8:]

    def get_wifi_ssid(self):
        for line in self.wifi_configuration_lines_list:
            line_stripped = line.strip()
            if line_stripped[:5] == "ssid=":
                return line_stripped[6:-1]

    def get_wifi_ssid2(self):
        count = 0
        for line in self.wifi_configuration_lines_list:
            line_stripped = line.strip()
            if line_stripped[:5] == "ssid=":
                if count:
                    return line_stripped[6:-1]
                count += 1

    def get_wifi_security_type(self):
        for line in self.wifi_configuration_lines_list:
            line_stripped = line.strip()
            if line_stripped[:9] == "key_mgmt=":
                return line_stripped[9:]

    def get_wifi_security_type2(self):
        count = 0
        for line in self.wifi_configuration_lines_list:
            line_stripped = line.strip()
            if line_stripped[:9] == "key_mgmt=":
                if count:
                    return line_stripped[9:]
                count += 1

    def get_wifi_psk(self):
        for line in self.wifi_configuration_lines_list:
            line_stripped = line.strip()
            if line_stripped[:4] == "psk=":
                return line_stripped[5:-1]

    def get_wifi_psk2(self):
        count = 0
        for line in self.wifi_configuration_lines_list:
            line_stripped = line.strip()
            if line_stripped[:4] == "psk=":
                if count:
                    return line_stripped[5:-1]
                count += 1


def get_wifi_config_from_file(load_file=file_locations.wifi_config_file):
    """ Loads wpa_supplicant.conf from file and returns it. """
    logger.primary_logger.debug("Loading Wifi wpa_supplicant File")

    if os.path.isfile(load_file):
        try:
            config_file = open(load_file, "r")
            config_file_content = config_file.read()
            config_file.close()
        except Exception as error:
            config_file_content = ""
            logger.primary_logger.error("Unable to load " + load_file + " - " + str(error))
        return config_file_content
    else:
        logger.primary_logger.error(load_file + " not found")


def write_wifi_config_to_file(config):
    """ Writes provided wpa_supplicant file to local disk. """
    logger.primary_logger.debug("Writing Wifi wpa_supplicant to File")
    try:
        wifi_config = open(file_locations.wifi_config_file, 'w')
        wifi_config.write(config)
        wifi_config.close()
    except Exception as error:
        logger.primary_logger.error("Unable to open wpa_supplicant file: " + str(error))
