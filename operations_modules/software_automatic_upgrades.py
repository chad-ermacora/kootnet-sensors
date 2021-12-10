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
from operations_modules.app_cached_variables_update import check_for_new_version
from operations_modules.app_generic_classes import CreateMonitoredThread
from operations_modules.software_version import CreateRefinedVersion, version
from configuration_modules import app_config_access
from upgrade_modules.upgrade_functions import start_kootnet_sensors_upgrade


def start_automatic_upgrades_server():
    text_name = "Automatic Upgrades Server"
    function = _thread_start_automatic_upgrades_server
    app_cached_variables.automatic_upgrades_thread = CreateMonitoredThread(function, thread_name=text_name)


def _thread_start_automatic_upgrades_server():
    if not app_config_access.upgrades_config.enable_automatic_upgrades:
        logger.primary_logger.debug("Automatic Upgrades Disabled in Configuration")
        app_cached_variables.automatic_upgrades_thread.current_state = "Disabled"
        while not app_config_access.upgrades_config.enable_automatic_upgrades:
            sleep(10)

    app_cached_variables.automatic_upgrades_thread.current_state = "Running"
    app_cached_variables.restart_automatic_upgrades_thread = False
    running_version = CreateRefinedVersion(version)
    version_template_msg = " -- New Version Detected - New: {{ NewVersion }} Current: " + version + " - "

    while not app_cached_variables.restart_automatic_upgrades_thread:
        sleep_total = 0
        main_sleep = app_config_access.upgrades_config.automatic_upgrade_delay_hours * 60 * 60
        while sleep_total < main_sleep and not app_cached_variables.restart_automatic_upgrades_thread:
            sleep(30)
            sleep_total += 30
        if not app_cached_variables.restart_automatic_upgrades_thread:
            selected_upgrade_type = app_config_access.upgrades_config.selected_upgrade_type
            try:
                check_for_new_version()
                new_version_msg = version_template_msg
                if app_config_access.upgrades_config.enable_automatic_upgrades_developmental:
                    http_dev_version = CreateRefinedVersion(app_cached_variables.developmental_version_available)
                    if http_dev_version.major_version != running_version.major_version:
                        _major_upgrade_msg_and_sleep()
                    else:
                        new_version = http_dev_version.get_version_string()
                        new_version_msg = new_version_msg.replace("{{ NewVersion }}", new_version)
                        if http_dev_version.feature_version > running_version.feature_version:
                            msg2 = "Starting Automatic Developmental Feature Upgrade"
                            logger.network_logger.info(new_version_msg + msg2)
                            start_kootnet_sensors_upgrade(download_type=selected_upgrade_type, dev_upgrade=True)
                        elif http_dev_version.feature_version == running_version.feature_version:
                            if http_dev_version.minor_version > running_version.minor_version:
                                msg2 = "Starting Automatic Developmental Minor Upgrade"
                                logger.network_logger.info(new_version_msg + msg2)
                                start_kootnet_sensors_upgrade(download_type=selected_upgrade_type, dev_upgrade=True)
                else:
                    http_std_version = CreateRefinedVersion(app_cached_variables.standard_version_available)
                    new_version = http_std_version.get_version_string()
                    new_version_msg = new_version_msg.replace("{{ NewVersion }}", new_version)
                    if app_config_access.upgrades_config.enable_automatic_upgrades_feature:
                        if http_std_version.major_version != running_version.major_version:
                            _major_upgrade_msg_and_sleep()
                        else:
                            if http_std_version.feature_version > running_version.feature_version:
                                logger.network_logger.info(new_version_msg + "Starting Automatic Feature Upgrade")
                                start_kootnet_sensors_upgrade(download_type=selected_upgrade_type)
                    if app_config_access.upgrades_config.enable_automatic_upgrades_minor:
                        if http_std_version.major_version != running_version.major_version:
                            _major_upgrade_msg_and_sleep()
                        else:
                            if http_std_version.feature_version == running_version.feature_version:
                                if http_std_version.minor_version > running_version.minor_version:
                                    logger.network_logger.info(new_version_msg + "Starting Automatic Minor Upgrade")
                                    start_kootnet_sensors_upgrade(download_type=selected_upgrade_type)
            except Exception as error:
                logger.primary_logger.error("Problem during Automatic Upgrade attempt: " + str(error))
        logger.primary_logger.debug("Automatic Upgrade Check Finished")


def _major_upgrade_msg_and_sleep():
    log_msg = "Automatic Upgrades between Major releases is currently not supported "
    logger.primary_logger.info(log_msg + "due to possible breaks in compatibility")
    logger.primary_logger.info("No further Automatic Upgrade Checks will be made until settings are changed")
    while not app_cached_variables.restart_automatic_upgrades_thread:
        sleep(15)


def get_automatic_upgrade_enabled_text():
    return_text = "Disabled"
    if app_config_access.upgrades_config.enable_automatic_upgrades_developmental:
        return_text = "Developmental"
    else:
        if app_config_access.upgrades_config.enable_automatic_upgrades_feature \
                and app_config_access.upgrades_config.enable_automatic_upgrades_minor:
            return_text = "Stable Feature & Minor"
        elif app_config_access.upgrades_config.enable_automatic_upgrades_feature:
            return_text = "Stable Feature"
        elif app_config_access.upgrades_config.enable_automatic_upgrades_minor:
            return_text = "Stable Minor"
    return return_text
