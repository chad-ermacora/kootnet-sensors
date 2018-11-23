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
_old_config = operations_config.get_installed_config()
_upgraded_config = operations_config.CreateConfig()
_old_installed_sensors = operations_config.get_installed_sensors()
_upgraded_installed_sensors = operations_config.CreateInstalledSensors()


def run_checks_and_updates():
    """ Checks and if necessary, Updates the Installed Sensors & Configuration files after an upgrade. """
    _check_missing_files()
    check_database_structure()

    old_versions = _get_old_version()

    not_current = True
    was_updated = False
    while not_current:
        if old_versions == "":
            operations_logger.primary_logger.info("Unknown Version Upgrade.  Please check your Configuration files")
            _write_current_version_to_file()
        elif old_versions == "Alpha.22.8" or old_versions == "":
            _update_ver_a_22_8()
            operations_logger.primary_logger.info("Upgraded: " + old_versions)
            old_versions = "Alpha.22.9"
            was_updated = True
        else:
            operations_logger.primary_logger.debug("No additional changes required || Old: " + old_versions +
                                                   " New: " + operations_config.version)
            old_versions = operations_config.version

        if old_versions == operations_config.version:
            not_current = False

    if was_updated:
        operations_config.write_config_to_file(_upgraded_config)
        operations_config.write_installed_sensors_to_file(_upgraded_installed_sensors)
        _write_current_version_to_file()
        restart_services()


def _check_missing_files():
    important_files = [operations_config.last_updated_file_location,
                       _old_version_file_location]

    for file in important_files:
        if os.path.isfile(file):
            pass
        else:
            operations_logger.primary_logger.info("Added missing file: " + file)
            os.system("touch " + file)


def _get_old_version():
    old_version_file = open(_old_version_file_location, 'r')
    old_version = old_version_file.read()
    old_version_file.close()

    old_version.strip()

    return old_version


def _write_current_version_to_file():
    current_version_file = open(_old_version_file_location, 'w')
    current_version_file.write(operations_config.version)
    current_version_file.close()


def _update_ver_a_22_8():
    _upgraded_installed_sensors.pimoroni_vl53l1x = _old_installed_sensors.pimoroni_lsm303d
    _upgraded_installed_sensors.pimoroni_lsm303d = _old_installed_sensors.pimoroni_enviro
    _upgraded_installed_sensors.pimoroni_enviro = _old_installed_sensors.pimoroni_bme680
    _upgraded_installed_sensors.pimoroni_bme680 = _old_installed_sensors.pimoroni_bh1745
    _upgraded_installed_sensors.pimoroni_bh1745 = _old_installed_sensors.raspberry_pi_sense_hat
    _upgraded_installed_sensors.raspberry_pi_sense_hat = _old_installed_sensors.raspberry_pi_3b_plus
    _upgraded_installed_sensors.raspberry_pi_3b_plus = 0
    _upgraded_installed_sensors.raspberry_pi_zero_w = _old_installed_sensors.raspberry_pi_zero_w
