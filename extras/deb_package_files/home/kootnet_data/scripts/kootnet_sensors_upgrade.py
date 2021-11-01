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
import logging
from logging.handlers import RotatingFileHandler
from shutil import rmtree

program_root_dir = ""
log_file_location = ""
try:
    split_location = os.path.dirname(os.path.realpath(__file__)).split("/")
    for section in split_location:
        program_root_dir += "/" + str(section)
    split_location = split_location[:-1]
    for section in split_location:
        log_file_location += "/" + str(section)
    program_root_dir = program_root_dir[1:] + "/"
    log_file_location = log_file_location[1:] + "/logs/primary_log.txt"
except Exception as program_root_error:
    print("File Locations - Script Location Error: " + str(program_root_error))


class CreateUpgradeLogger:
    def __init__(self):
        """
        Creates Kootnet Sensors Upgrade logger. Uses Primary log of main Kootnet Sensors program
        """
        self.primary_logger = logging.getLogger("PrimaryLog")
        self.initialize_logger()

    def initialize_logger(self):
        formatter = logging.Formatter("%(asctime)s - %(levelname)s:  %(message)s", "%Y-%m-%d %H:%M:%S")
        file_handler_main = RotatingFileHandler(log_file_location, maxBytes=256000, backupCount=5)
        file_handler_main.setFormatter(formatter)
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        self.primary_logger.addHandler(file_handler_main)
        self.primary_logger.addHandler(stream_handler)
        self.primary_logger.setLevel(logging.INFO)


class CreateUpgradeInterface:
    def __init__(self, load_config_file=True):
        """
        Creates an object to customize and run Kootnet Sensor upgrades
        :param load_config_file: Load auto-update configuration file, Default True
        """
        self.configuration_file_present = False
        self.upgrade_config_location = program_root_dir + "upgrade_options.conf"
        self.upgrade_running_file_location = program_root_dir + "upgrade_running.txt"
        self.upgrade_file_location = ""
        self.clean_upgrade = 0

        if load_config_file:
            try:
                if os.path.isfile(self.upgrade_config_location):
                    with open(self.upgrade_config_location, "r") as info_file:
                        config_str = info_file.read()
                    config_list = config_str.split(",")
                    self.upgrade_file_location = config_list[0]
                    self.clean_upgrade = int(config_list[1])
                    os.remove(self.upgrade_config_location)
                    self.configuration_file_present = True
                    logger.primary_logger.debug(" --- Configuration file for automatic upgrade loaded successfully")
                else:
                    logger.primary_logger.error("--- Upgrade Configuration File not found")
            except Exception as upgrade_configuration_error:
                logger.primary_logger.error("--- Upgrade Configuration Failed: " + str(upgrade_configuration_error))

    def start_upgrade(self):
        """
        Starts the upgrade process based on class variable settings
        :return: Nothing
        """
        if self.configuration_file_present:
            if self.clean_upgrade:
                self._clean_install()
            self._install_upgrade()
        self._set_upgrade_running_false()

    def _install_upgrade(self):
        """
        Installs the Debian upgrade file
        :return: Nothing
        """
        dpkg_install_str = "dpkg -iEG "
        if self.clean_upgrade:
            dpkg_install_str = "dpkg -i "

        try:
            logger.primary_logger.info(" --- Updating apt-get cache ...")
            os.system("apt-get update")
            logger.primary_logger.info(" --- Starting Install of Debian Package ...")
            os.system(dpkg_install_str + self.upgrade_file_location)
            os.system("date -u >/etc/kootnet/last_updated.txt")
            logger.primary_logger.info(" --- Debian Package Install Complete")
        except Exception as error:
            logger.primary_logger.error(" --- Debian Package Install Failed: " + str(error))

    @staticmethod
    def _clean_install():
        """
        Removes the main Python virtual environment, SSL files, program folder and system services
        Optionally used just before upgrades to clear issue files and or clutter
        :return: Nothing, removes program files
        """
        try:
            logger.primary_logger.info(" --- Starting Clean Removal ...")
            rmtree("/home/kootnet_data/env/")
            rmtree("/home/kootnet_data/ssl_files/")
            rmtree("/opt/kootnet-sensors/")
            os.system("rm -f /usr/share/applications/KootNet*.desktop")
            os.system("rm -f /etc/systemd/system/Kootnet*.service")
            os.system("rm -f /etc/systemd/system/SensorU*.service")
            logger.primary_logger.info(" --- Clean Removal Successful")
        except Exception as error:
            logger.primary_logger.error("--- Clean Removal: " + str(error))

    def _set_upgrade_running_false(self):
        try:
            with open(self.upgrade_running_file_location, "w") as upgrade_file:
                upgrade_file.write("0")
        except Exception as error:
            logger.primary_logger.warning("Accessing upgrade running file: " + str(error))


logger = CreateUpgradeLogger()

# If run directly, start upgrade process
# Requires a pre-made configuration file made by Kootnet Sensors Web Portal or TCT
if __name__ == '__main__':
    logger.primary_logger.info(" --- Kootnet Sensors Upgrade Script Starting ...")
    CreateUpgradeInterface().start_upgrade()
