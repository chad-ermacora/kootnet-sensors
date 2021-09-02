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
import os
from operations_modules import logger
from operations_modules import app_cached_variables
from operations_modules.app_cached_variables_update import check_for_new_version
from operations_modules.app_generic_functions import CreateMonitoredThread, thread_function
from operations_modules.software_version import CreateRefinedVersion, version
from configuration_modules import app_config_access


def start_automatic_upgrades_server():
    text_name = "Automatic Upgrades Server"
    function = _thread_start_automatic_upgrades_server
    app_cached_variables.automatic_upgrades_thread = CreateMonitoredThread(function, thread_name=text_name)
    if not app_config_access.primary_config.enable_automatic_upgrades_major and \
            not app_config_access.primary_config.enable_automatic_upgrades_minor and \
            not app_config_access.primary_config.enable_automatic_upgrades_developmental:
        logger.primary_logger.debug("Automatic Upgrades Disabled in Configuration")
        app_cached_variables.automatic_upgrades_thread.current_state = "Disabled"


def _thread_start_automatic_upgrades_server():
    app_cached_variables.automatic_upgrades_thread.current_state = "Disabled"
    while not app_config_access.primary_config.enable_automatic_upgrades_major \
            and not app_config_access.primary_config.enable_automatic_upgrades_minor \
            and not app_config_access.primary_config.enable_automatic_upgrades_developmental:
        sleep(5)
    app_cached_variables.automatic_upgrades_thread.current_state = "Running"
    app_cached_variables.restart_automatic_upgrades_thread = False
    running_version = CreateRefinedVersion(version)

    while not app_cached_variables.restart_automatic_upgrades_thread:
        sleep_total = 0
        main_sleep = app_config_access.primary_config.automatic_upgrade_delay_hours * 60 * 60
        while sleep_total < main_sleep and not app_cached_variables.restart_automatic_upgrades_thread:
            sleep(30)
            sleep_total += 30
        if not app_cached_variables.restart_automatic_upgrades_thread:
            try:
                check_for_new_version()
                http_dev_version = CreateRefinedVersion(app_cached_variables.developmental_version_available)
                http_std_version = CreateRefinedVersion(app_cached_variables.standard_version_available)

                if app_config_access.primary_config.enable_automatic_upgrades_developmental:
                    if http_dev_version.major_version > running_version.major_version or \
                            http_dev_version.minor_version > running_version.minor_version:
                        logger.primary_logger.info("Starting Automatic Developmental Upgrade")
                        thread_function(os.system, args=app_cached_variables.bash_commands["UpgradeOnlineDEV"])

                elif app_config_access.primary_config.enable_automatic_upgrades_major:
                    if http_std_version.major_version > running_version.major_version:
                        logger.primary_logger.info("Starting Automatic Major Upgrade")
                        thread_function(os.system, args=app_cached_variables.bash_commands["UpgradeOnline"])

                if app_config_access.primary_config.enable_automatic_upgrades_minor and not \
                        app_config_access.primary_config.enable_automatic_upgrades_developmental:
                    if http_std_version.major_version == running_version.major_version and \
                            http_std_version.minor_version > running_version.minor_version:
                        logger.primary_logger.info("Starting Automatic Minor Upgrade")
                        thread_function(os.system, args=app_cached_variables.bash_commands["UpgradeOnline"])
            except Exception as error:
                logger.primary_logger.error("Problem during Automatic Upgrade attempt: " + str(error))
        logger.primary_logger.debug("Automatic Upgrade Check Finished")


def get_automatic_upgrade_enabled_text():
    return_text = "Disabled"
    if app_config_access.primary_config.enable_automatic_upgrades_developmental:
        return_text = "Enabled Developmental"
    else:
        if app_config_access.primary_config.enable_automatic_upgrades_major \
                and app_config_access.primary_config.enable_automatic_upgrades_minor:
            return_text = "Enabled Stable Major & Minor"
        elif app_config_access.primary_config.enable_automatic_upgrades_major:
            return_text = "Enabled Stable Major"
        elif app_config_access.primary_config.enable_automatic_upgrades_minor:
            return_text = "Enabled Stable Minor"
    return return_text
