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

from operations_modules import file_locations
from operations_modules import logger


def get_wifi_config_from_file():
    """ Loads wpa_supplicant.conf from file and returns it. """
    logger.primary_logger.debug("Loading Wifi wpa_supplicant File")

    if os.path.isfile(file_locations.wifi_config_file):
        try:
            config_file = open(file_locations.wifi_config_file, "r")
            config_file_content = config_file.read()
            config_file.close()
        except Exception as error:
            config_file_content = ""
            logger.primary_logger.error("Unable to load " + file_locations.wifi_config_file + " - " + str(error))
        return config_file_content
    else:
        logger.primary_logger.error(file_locations.wifi_config_file + " not found")


def write_wifi_config_to_file(config):
    """ Writes provided wpa_supplicant file to local disk. """
    logger.primary_logger.debug("Writing Wifi wpa_supplicant to File")
    try:
        wifi_config = open(file_locations.wifi_config_file, 'w')
        wifi_config.write(config)
        wifi_config.close()
    except Exception as error:
        logger.primary_logger.error("Unable to open wpa_supplicant file: " + str(error))
