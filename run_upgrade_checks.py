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
from operations_modules import software_version
from operations_modules import program_upgrade_functions
from operations_modules import os_cli_commands


def run_upgrade_checks():
    """
     Checks previous written version of the program to the current version.
     If the current version is different, start upgrade functions.
    """
    msg = "Old Version: " + software_version.old_version + " || New Version: " + software_version.version
    logger.primary_logger.debug(msg)
    previous_version = software_version.CreateRefinedVersion(software_version.old_version)
    no_changes = True

    if previous_version.major_version == "New_Install":
        logger.primary_logger.info("New Install Detected")
        no_changes = False
    elif previous_version.major_version == "Beta":
        if previous_version.feature_version == 29:
            if previous_version.minor_version < 13:
                program_upgrade_functions.reset_variance_config()
                program_upgrade_functions.reset_installed_sensors()
    elif previous_version.major_version == "Alpha":
        if previous_version.feature_version < 26:
            msg = "Upgraded: " + software_version.old_version + " || New: " + software_version.version
            logger.primary_logger.info(msg)
            no_changes = False
            program_upgrade_functions.reset_installed_sensors()
            program_upgrade_functions.reset_main_config()
            program_upgrade_functions.reset_variance_config()
        elif previous_version.feature_version > 25:
            no_changes = False
            program_upgrade_functions.reset_installed_sensors()
            program_upgrade_functions.reset_variance_config()
    else:
        no_changes = False
        msg = "Bad or Missing Previous Version Detected - Resetting Config and Installed Sensors"
        logger.primary_logger.error(msg)
        program_upgrade_functions.reset_installed_sensors()
        program_upgrade_functions.reset_main_config()

    # Since run_upgrade_checks is only run if there is a different version, show upgrade but no configuration changes
    if no_changes:
        msg = "Upgrade detected || No configuration changes || Old: "
        logger.primary_logger.info(msg + software_version.old_version + " New: " + software_version.version)
    software_version.write_program_version_to_file()
    os.system(os_cli_commands.restart_sensor_services_command)


# Used as a Linux service to make needed changes outside the main program.  Usually used after upgrades.
run_upgrade_checks()
