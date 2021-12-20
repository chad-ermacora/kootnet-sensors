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
from operations_modules.app_generic_classes import CreateRefinedVersion
from upgrade_modules import generic_upgrade_functions
from upgrade_modules.old_configuration_conversions.beta_34_x_to_35_x import upgrade_beta_34_x_to_35_x


def run_configuration_upgrade_checks():
    """
     Checks previous written version of the program to the current version.
     If the current version is different, start upgrade functions.
    """
    if software_version.old_version != software_version.version:
        logger.primary_logger.debug(" - Configuration Upgrade Check Starting ...")
        previous_version = CreateRefinedVersion(software_version.old_version)
        current_version = CreateRefinedVersion(software_version.version)
        no_changes = True

        if previous_version.major_version == 999:
            logger.primary_logger.info(" - New Install Detected")
            no_changes = False
            generic_upgrade_functions.reset_all_configurations(log_reset=False)
        elif previous_version.major_version == 0 and previous_version.feature_version == 0 and \
                previous_version.minor_version == 0:
            msg = "Bad or Missing Previous Version Detected - Resetting Config and Installed Sensors"
            logger.primary_logger.error(msg)
            no_changes = False
            generic_upgrade_functions.reset_installed_sensors()
            generic_upgrade_functions.reset_primary_config()
        else:
            msg = "Old Version: " + software_version.old_version + " || New Version: " + software_version.version
            logger.primary_logger.info(" - " + msg)

            if previous_version.major_version == 0:
                if previous_version.feature_version > current_version.feature_version:
                    logger.primary_logger.warning("The current version appears to be older then the previous version")
                    log_msg1 = "Configurations compatibility can not be guaranteed, "
                    logger.primary_logger.warning(log_msg1 + "resetting Primary and Installed Sensors configurations")
                    no_changes = False
                    generic_upgrade_functions.reset_installed_sensors()
                    generic_upgrade_functions.reset_primary_config()
                elif previous_version.feature_version == 35:
                    if previous_version.minor_version < 93:
                        no_changes = False
                        generic_upgrade_functions.reset_upgrade_config(log_reset=False)
                    if previous_version.minor_version < 60:
                        no_changes = False
                        generic_upgrade_functions.reset_urls_config()
                    if previous_version.minor_version < 56:
                        no_changes = False
                        generic_upgrade_functions.reset_email_reports_config(log_reset=False)
                        generic_upgrade_functions.reset_email_db_graphs_config(log_reset=False)
                    if previous_version.minor_version < 53:
                        no_changes = False
                        generic_upgrade_functions.reset_live_graph_config(log_reset=False)
                        generic_upgrade_functions.reset_database_graph_config(log_reset=False)
                    if previous_version.minor_version < 51:
                        no_changes = False
                        generic_upgrade_functions.reset_email_config()
                elif previous_version.feature_version == 34:
                    no_changes = False
                    upgrade_beta_34_x_to_35_x()
                    if previous_version.minor_version < 122:
                        config_class = generic_upgrade_functions.CreateWeatherUndergroundConfiguration
                        generic_upgrade_functions.upgrade_config_load_and_save(config_class)
                elif previous_version.feature_version == 33:
                    no_changes = False
                    generic_upgrade_functions.reset_live_graph_config(log_reset=False)
                    generic_upgrade_functions.reset_database_graph_config(log_reset=False)
                    generic_upgrade_functions.reset_email_config()
                    generic_upgrade_functions.reset_flask_login_credentials()
                    if previous_version.minor_version < 145:
                        config_class = generic_upgrade_functions.CreatePrimaryConfiguration
                        generic_upgrade_functions.upgrade_config_load_and_save(config_class)
                elif previous_version.feature_version == 32:
                    no_changes = False
                    generic_upgrade_functions.reset_flask_login_credentials()
                    generic_upgrade_functions.reset_primary_config()
                    generic_upgrade_functions.reset_mqtt_publisher_config()
                    generic_upgrade_functions.reset_sensor_control_config()
                elif previous_version.feature_version < 32:
                    no_changes = False
                    generic_upgrade_functions.reset_all_configurations()

        if no_changes:
            logger.primary_logger.info(" - No configuration changes detected")
        generic_upgrade_functions.load_and_save_all_configs_silently()
        software_version.write_program_version_to_file()
