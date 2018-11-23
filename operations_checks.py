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
from operations_db import check_database_structure

_old_version_file_location = "/etc/kootnet/installed_version.txt"
_upgrade_current_config = operations_config.get_installed_config()
_upgrade_installed_sensors = operations_config.CreateInstalledSensors()


def run_checks_and_updates():
    """ Checks and if necessary, Updates the Installed Sensors & Configuration files after an upgrade. """
    _check_missing_files()
    check_database_structure()

    old_versions = _get_old_version()

    if old_versions == "Alpha.22.8":
        _ver_a_22_8()
    elif old_versions == "Alpha.22.10":
        print("W00ts!")
    else:
        operations_logger.primary_logger.debug("No updates needed for " + old_versions +
                                               " to " + operations_config.version)
    _write_current_version_to_file()


def _check_missing_files():
    important_files = [operations_config.last_updated_file_location,
                       _old_version_file_location]

    for file in important_files:
        if os.path.isfile(file):
            pass
        else:
            operations_logger.primary_logger.info("Missing file: " + file)
            os.system("touch " + file)


def _get_old_version():
    old_version_file = open(_old_version_file_location, 'r')
    old_version = old_version_file.read()
    old_version_file.close()

    return old_version


def _write_current_version_to_file():
    current_version_file = open(_old_version_file_location, 'w')
    current_version_file.write(operations_config.version)
    current_version_file.close()


def _ver_a_22_8():
    operations_logger.primary_logger.info("Upgrading from Alpha.22.8 to " + operations_config.version)
    _upgrade_installed_sensors.pimoroni_vl53l1x = _upgrade_installed_sensors.pimoroni_lsm303d
    _upgrade_installed_sensors.pimoroni_lsm303d = _upgrade_installed_sensors.pimoroni_enviro
    _upgrade_installed_sensors.pimoroni_enviro = _upgrade_installed_sensors.pimoroni_bme680
    _upgrade_installed_sensors.pimoroni_bme680 = _upgrade_installed_sensors.pimoroni_bh1745
    _upgrade_installed_sensors.pimoroni_bh1745 = _upgrade_installed_sensors.raspberry_pi_sense_hat
    _upgrade_installed_sensors.raspberry_pi_sense_hat = _upgrade_installed_sensors.raspberry_pi_3b_plus
    _upgrade_installed_sensors.raspberry_pi_3b_plus = 0
    operations_config.write_installed_sensors_to_file(_upgrade_installed_sensors)
