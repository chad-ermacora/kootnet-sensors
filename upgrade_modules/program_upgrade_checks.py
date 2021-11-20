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
from upgrade_modules import generic_upgrade_functions
from upgrade_modules.old_configuration_conversions.beta_30_x_to_31_x import upgrade_beta_30_x_to_31
from upgrade_modules.old_configuration_conversions.beta_33_x_to_33_96 import upgrade_beta_33_x_to_33_96
from upgrade_modules.old_configuration_conversions.beta_34_164_to_34_plus import upgrade_beta_34_164_to_34_plus


def run_configuration_upgrade_checks():
    """
     Checks previous written version of the program to the current version.
     If the current version is different, start upgrade functions.
    """
    logger.primary_logger.debug(" - Configuration Upgrade Check Starting ...")
    previous_version = software_version.CreateRefinedVersion(software_version.old_version)
    current_version = software_version.CreateRefinedVersion(software_version.version)
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
                if previous_version.minor_version < 51:
                    no_changes = False
                    generic_upgrade_functions.reset_email_config()
            elif previous_version.feature_version == 34:
                if previous_version.minor_version < 165:
                    no_changes = False
                    upgrade_beta_34_164_to_34_plus()
                if previous_version.minor_version < 152:
                    no_changes = False
                    generic_upgrade_functions.reset_flask_login_credentials()
                if previous_version.minor_version < 122:
                    no_changes = False
                    config_class = generic_upgrade_functions.CreateWeatherUndergroundConfiguration
                    generic_upgrade_functions.upgrade_config_load_and_save(config_class)
            elif previous_version.feature_version == 33:
                if previous_version.minor_version < 145:
                    if previous_version.minor_version < 96:
                        if previous_version.minor_version < 61:
                            config_class = generic_upgrade_functions.CreateEmailConfiguration
                            generic_upgrade_functions.upgrade_config_load_and_save(config_class)
                        upgrade_beta_33_x_to_33_96()
                    else:
                        config_class = generic_upgrade_functions.CreatePrimaryConfiguration
                        generic_upgrade_functions.upgrade_config_load_and_save(config_class)
                    no_changes = False
            elif previous_version.feature_version == 32:
                no_changes = False
                generic_upgrade_functions.reset_mqtt_publisher_config()
                generic_upgrade_functions.reset_sensor_control_config()
                upgrade_beta_33_x_to_33_96()
                config_class = generic_upgrade_functions.CreateEmailConfiguration
                generic_upgrade_functions.upgrade_config_load_and_save(config_class)
            elif previous_version.feature_version == 31:
                no_changes = False
                generic_upgrade_functions.reset_mqtt_publisher_config()
                generic_upgrade_functions.reset_sensor_control_config()
                generic_upgrade_functions.reset_checkin_config()
                generic_upgrade_functions.reset_trigger_high_low_config()

                config_classes = [generic_upgrade_functions.CreateInstalledSensorsConfiguration,
                                  generic_upgrade_functions.CreateIntervalRecordingConfiguration,
                                  generic_upgrade_functions.CreateMQTTSubscriberConfiguration]
                for config_class in config_classes:
                    generic_upgrade_functions.upgrade_config_load_and_save(config_class)
                upgrade_beta_33_x_to_33_96()
            elif previous_version.feature_version == 30:
                no_changes = False
                upgrade_beta_30_x_to_31()
            elif previous_version.feature_version < 30:
                no_changes = False
                generic_upgrade_functions.reset_all_configurations()

    if no_changes:
        logger.primary_logger.info(" - No configuration changes detected")
    generic_upgrade_functions.load_and_save_all_configs_silently()
    software_version.write_program_version_to_file()
    software_version.old_version = software_version.version
