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

import operations_config
import operations_logger
from operations_commands import restart_services
from operations_db import check_database_structure

_old_version_file_location = "/etc/kootnet/installed_version.txt"


class CreateChecksUpgradesData:
    def __init__(self):
        self.old_config = operations_config.get_installed_config()
        self.upgraded_config = operations_config.CreateConfig()
        self.old_installed_sensors = operations_config.get_installed_sensors()
        self.upgraded_installed_sensors = operations_config.CreateInstalledSensors()

        self.old_versions = _get_old_version()


def run_checks_and_updates():
    """ Checks and if necessary, Updates the Installed Sensors & Configuration files after an upgrade. """
    _check_missing_files()
    check_database_structure()
    upgrade_data_obj = CreateChecksUpgradesData()

    if upgrade_data_obj.old_versions == operations_config.version:
        not_current = False
    else:
        not_current = True

    was_updated = False
    while not_current:
        was_updated = True
        if upgrade_data_obj.old_versions == "":
            operations_logger.primary_logger.warning("Missing version file: " +
                                                     _old_version_file_location +
                                                     " - Configuration files Reset to defaults")
            upgrade_data_obj.old_versions = operations_config.version
        elif upgrade_data_obj.old_versions == "Alpha.22.8":
            _update_ver_a_22_8(upgrade_data_obj)
            operations_logger.primary_logger.info("Upgraded: " + upgrade_data_obj.old_versions)
            upgrade_data_obj.old_versions = "Alpha.22.9"
        else:
            operations_logger.primary_logger.debug("No additional changes required || Old: " + upgrade_data_obj.old_versions +
                                                   " New: " + operations_config.version)
            upgrade_data_obj.old_versions = operations_config.version
            upgrade_data_obj.upgraded_config = upgrade_data_obj.old_config
            upgrade_data_obj.upgraded_installed_sensors = upgrade_data_obj.old_installed_sensors

        if upgrade_data_obj.old_versions == operations_config.version:
            not_current = False

    if was_updated:
        operations_config.write_config_to_file(upgrade_data_obj.upgraded_config)
        operations_config.write_installed_sensors_to_file(upgrade_data_obj.upgraded_installed_sensors)
        _write_current_version_to_file()
        restart_services()


def _check_missing_files():
    important_files = [operations_config.last_updated_file_location,
                       _old_version_file_location]

    for file in important_files:
        if os.path.isfile(file):
            pass
        else:
            operations_logger.primary_logger.warning("Added missing file: " + file)
            os.system("touch " + file)


def _get_old_version():
    old_version_file = open(_old_version_file_location, 'r')
    old_version = old_version_file.read()
    old_version_file.close()

    old_version.strip()

    return old_version


def _write_current_version_to_file():
    operations_logger.primary_logger.debug("Current version file updating")
    current_version_file = open(_old_version_file_location, 'w')
    current_version_file.write(operations_config.version)
    current_version_file.close()


def _update_ver_a_22_8(upgrade_data_obj):
    upgrade_data_obj.upgraded_installed_sensors.pimoroni_vl53l1x = upgrade_data_obj.old_installed_sensors.pimoroni_lsm303d
    upgrade_data_obj.upgraded_installed_sensors.pimoroni_lsm303d = upgrade_data_obj.old_installed_sensors.pimoroni_enviro
    upgrade_data_obj.upgraded_installed_sensors.pimoroni_enviro = upgrade_data_obj.old_installed_sensors.pimoroni_bme680
    upgrade_data_obj.upgraded_installed_sensors.pimoroni_bme680 = upgrade_data_obj.old_installed_sensors.pimoroni_bh1745
    upgrade_data_obj.upgraded_installed_sensors.pimoroni_bh1745 = upgrade_data_obj.old_installed_sensors.raspberry_pi_sense_hat
    upgrade_data_obj.upgraded_installed_sensors.raspberry_pi_sense_hat = upgrade_data_obj.old_installed_sensors.raspberry_pi_3b_plus
    upgrade_data_obj.upgraded_installed_sensors.raspberry_pi_3b_plus = 0
    upgrade_data_obj.upgraded_installed_sensors.raspberry_pi_zero_w = upgrade_data_obj.old_installed_sensors.raspberry_pi_zero_w

    os.system("rm -f /etc/systemd/system/SensorHTTP.service 2>/dev/null")
    print("\n\nInstalling Additional libraries, please wait ...")
    os.system("pip3 install Flask gevent")
    print("Done\n\n")
