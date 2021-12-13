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
from time import sleep
from operations_modules import logger
from operations_modules import app_cached_variables
from operations_modules.app_generic_classes import CreateMonitoredThread, CreateRefinedVersion
from operations_modules.software_version import version
from configuration_modules.app_config_access import upgrades_config
from upgrade_modules.upgrade_functions import CreateUpgradeScriptInterface, CreateUpdateChecksInterface


def start_automatic_upgrades_server():
    text_name = "Automatic Upgrades Server"
    function = _thread_start_automatic_upgrades_server
    app_cached_variables.automatic_upgrades_thread = CreateMonitoredThread(function, thread_name=text_name)


def _thread_start_automatic_upgrades_server():
    if not upgrades_config.enable_automatic_upgrades:
        logger.primary_logger.debug("Automatic Upgrades Disabled in Configuration")
        app_cached_variables.automatic_upgrades_thread.current_state = "Disabled"
        while not upgrades_config.enable_automatic_upgrades:
            sleep(10)

    app_cached_variables.automatic_upgrades_thread.current_state = "Running"
    app_cached_variables.restart_automatic_upgrades_thread = False
    upgrade_interface = CreateUpgradeScriptInterface()
    running_version = CreateRefinedVersion(version)
    version_template_msg = " -- New Version Detected - New: {{ NewVersion }} Current: " + version + " - "

    while not app_cached_variables.restart_automatic_upgrades_thread:
        sleep_total = 0
        main_sleep = upgrades_config.automatic_upgrade_delay_hours * 60 * 60
        while sleep_total < main_sleep and not app_cached_variables.restart_automatic_upgrades_thread:
            sleep(30)
            sleep_total += 30
        if not app_cached_variables.restart_automatic_upgrades_thread and upgrades_config.enable_automatic_upgrades:
            upgrade_interface.download_type = upgrades_config.selected_upgrade_type
            upgrade_interface.dev_upgrade = upgrades_config.enable_automatic_upgrades_developmental
            upgrade_interface.verify_ssl = upgrades_config.verify_ssl
            latest_version = CreateRefinedVersion(_get_automatic_upgrade_version())

            try:
                new_version_msg = version_template_msg
                if upgrade_interface.dev_upgrade:
                    if latest_version.major_version != running_version.major_version:
                        _major_upgrade_msg_and_sleep()
                    else:
                        new_version = latest_version.get_version_string()
                        new_version_msg = new_version_msg.replace("{{ NewVersion }}", new_version)
                        if latest_version.feature_version > running_version.feature_version:
                            msg2 = "Starting Automatic Developmental Feature Upgrade"
                            logger.network_logger.info(new_version_msg + msg2)
                            upgrade_interface.start_kootnet_sensors_upgrade()
                        elif latest_version.feature_version == running_version.feature_version:
                            if latest_version.minor_version > running_version.minor_version:
                                msg2 = "Starting Automatic Developmental Minor Upgrade"
                                logger.network_logger.info(new_version_msg + msg2)
                                upgrade_interface.start_kootnet_sensors_upgrade()
                else:
                    new_version = latest_version.get_version_string()
                    new_version_msg = new_version_msg.replace("{{ NewVersion }}", new_version)
                    if upgrades_config.enable_automatic_upgrades_feature:
                        if latest_version.major_version != running_version.major_version:
                            _major_upgrade_msg_and_sleep()
                        else:
                            if latest_version.feature_version > running_version.feature_version:
                                logger.network_logger.info(new_version_msg + "Starting Automatic Feature Upgrade")
                                upgrade_interface.start_kootnet_sensors_upgrade()
                    if upgrades_config.enable_automatic_upgrades_minor:
                        if latest_version.major_version != running_version.major_version:
                            _major_upgrade_msg_and_sleep()
                        else:
                            if latest_version.feature_version == running_version.feature_version:
                                if latest_version.minor_version > running_version.minor_version:
                                    logger.network_logger.info(new_version_msg + "Starting Automatic Minor Upgrade")
                                    upgrade_interface.start_kootnet_sensors_upgrade()
            except Exception as error:
                logger.primary_logger.error("Problem during Automatic Upgrade attempt: " + str(error))
        logger.primary_logger.debug("Automatic Upgrade Check Finished")


def _major_upgrade_msg_and_sleep():
    log_msg = "Automatic Upgrades between Major releases is currently not supported "
    logger.primary_logger.info(log_msg + "due to possible breaks in compatibility")
    logger.primary_logger.info("No further Automatic Upgrade Checks will be made until settings are changed")
    while not app_cached_variables.restart_automatic_upgrades_thread:
        sleep(15)


def _get_automatic_upgrade_version():
    update_checks_interface.update_versions_info_variables()
    if upgrades_config.enable_automatic_upgrades_developmental:
        return update_checks_interface.new_developmental_version
    return update_checks_interface.new_standard_version


def get_automatic_upgrade_enabled_text():
    return_text = "Disabled"
    if upgrades_config.enable_automatic_upgrades_developmental:
        return_text = "Developmental"
    else:
        if upgrades_config.enable_automatic_upgrades_feature \
                and upgrades_config.enable_automatic_upgrades_minor:
            return_text = "Stable Feature & Minor"
        elif upgrades_config.enable_automatic_upgrades_feature:
            return_text = "Stable Feature"
        elif upgrades_config.enable_automatic_upgrades_minor:
            return_text = "Stable Minor"
    return return_text


update_checks_interface = CreateUpdateChecksInterface()
