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
from operations_modules import logger
from operations_modules import software_version
from upgrade_modules.old_configuration_conversions import generic_upgrade_functions
from upgrade_modules.old_configuration_conversions.alpha_to_beta import upgrade_alpha_to_beta
from upgrade_modules.old_configuration_conversions.beta_29_x_to_30_x import upgrade_beta_29_to_30, \
    upgrade_beta_30_x_to_30_90, upgrade_beta_30_90_to_30_138


def run_configuration_upgrade_checks():
    """
     Checks previous written version of the program to the current version.
     If the current version is different, start upgrade functions.
    """
    logger.primary_logger.debug(" - Configuration Upgrade Check Starting ...")
    previous_version = software_version.CreateRefinedVersion(software_version.old_version)
    current_version = software_version.CreateRefinedVersion(software_version.version)
    no_changes = True

    if previous_version.major_version == "New_Install":
        logger.primary_logger.info(" - New Install Detected")
        no_changes = False
        generic_upgrade_functions.reset_all_silent()
    elif previous_version.major_version == "Unknown":
        logger.primary_logger.warning("Unknown Previous Version Detected")
        no_changes = False
        generic_upgrade_functions.reset_installed_sensors()
        generic_upgrade_functions.reset_primary_config()
    else:
        msg = "Old Version: " + software_version.old_version + " || New Version: " + software_version.version
        logger.primary_logger.info(" - " + msg)

        if previous_version.major_version == "Beta":
            if previous_version.feature_version > current_version.feature_version:
                logger.primary_logger.warning("The current version appears to be older then the previous version")
                log_msg1 = "Configurations compatibility can not be guaranteed, "
                logger.primary_logger.warning(log_msg1 + "resetting Primary and Installed Sensors configurations")
                no_changes = False
                generic_upgrade_functions.reset_installed_sensors()
                generic_upgrade_functions.reset_primary_config()
            elif previous_version.feature_version == 31:
                if previous_version.minor_version < 18:
                    generic_upgrade_functions.reset_trigger_high_low_config(log_reset=False)
            elif previous_version.feature_version == 30:
                if previous_version.minor_version < 138:
                    no_changes = False
                    upgrade_beta_30_90_to_30_138()
                if previous_version.minor_version < 90:
                    no_changes = False
                    upgrade_beta_30_x_to_30_90()
            elif previous_version.feature_version == 29:
                no_changes = False
                upgrade_beta_29_to_30()
        elif previous_version.major_version == "Alpha":
            no_changes = False
            upgrade_alpha_to_beta()
        else:
            msg = "Bad or Missing Previous Version Detected - Resetting Config and Installed Sensors"
            logger.primary_logger.error(msg)
            no_changes = False
            generic_upgrade_functions.reset_installed_sensors()
            generic_upgrade_functions.reset_primary_config()

    if no_changes:
        logger.primary_logger.info(" - No configuration changes detected")
    software_version.write_program_version_to_file()
    software_version.old_version = software_version.version
