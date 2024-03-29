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
from threading import Thread
from flask import Blueprint, request, render_template
from configuration_modules.app_config_access import primary_config
from operations_modules import logger
from operations_modules import app_cached_variables
from operations_modules import file_locations
from operations_modules.app_generic_functions import thread_function
from operations_modules.sqlite_database import run_database_integrity_check
from upgrade_modules.generic_upgrade_functions import upgrade_python_pip_modules, upgrade_linux_os
from upgrade_modules.upgrade_functions import CreateUpdateChecksInterface, CreateUpgradeScriptInterface, \
    download_type_smb
from http_server.server_http_auth import auth
from http_server.flask_blueprints.atpro.atpro_generic import get_message_page, sanitize_text
from http_server.flask_blueprints.atpro.atpro_notifications import atpro_notifications

html_atpro_system_commands_routes = Blueprint("html_atpro_system_commands_routes", __name__)
running_with_root = app_cached_variables.running_with_root
running_as_service = app_cached_variables.running_as_service


@html_atpro_system_commands_routes.route("/atpro/system-upgrades-power")
def html_atpro_system_upgrades_power():
    return render_template("ATPro_admin/page_templates/system/system-upgrades-power.html")


@html_atpro_system_commands_routes.route('/atpro/system/<path:url_path>')
@auth.login_required
def atpro_upgrade_urls(url_path):
    title = "Function Disabled"
    message = "Kootnet Sensors must be running as a service with root access"
    if primary_config.demo_mode:
        message = "Function Disabled in Demo mode"

    url_path = sanitize_text(url_path)
    if url_path == "db-integrity-quick":
        title = "Quick Integrity Checks"
        message = "Starting Integrity Checks on Main, Sensor Checkins & MQTT databases"
        _start_db_integrity_checks(True)
    elif url_path == "db-integrity-full":
        title = "Full Integrity Checks"
        message = "Starting Integrity Checks on Main, Sensor Checkins & MQTT databases"
        _start_db_integrity_checks(False)
    elif running_as_service and running_with_root and not primary_config.demo_mode:
        title = "Error!"
        message = "An Error occurred"
        system_command = "exit"
        if url_path == "system-restart-program":
            logger.network_logger.info("** Program Restart Initiated by " + str(request.remote_addr))
            title = "Restarting Program"
            message = "The web interface will be temporarily unavailable"
            system_command = app_cached_variables.bash_commands["RestartService"]
        elif url_path == "system-restart":
            logger.network_logger.info("** System Restart Initiated by " + str(request.remote_addr))
            title = "Restarting System"
            message = "The web interface will be temporarily unavailable"
            system_command = app_cached_variables.bash_commands["RebootSystem"]
        elif url_path == "system-shutdown":
            logger.network_logger.info("** System Shutdown Initiated by " + str(request.remote_addr))
            title = "Shutting Down"
            message = "You will be unable to access the web interface until some one turns the sensor back on"
            system_command = app_cached_variables.bash_commands["ShutdownSystem"]
        elif url_path == "upgrade-http-std":
            logger.network_logger.info("* Upgrade - HTTP Initiated by " + str(request.remote_addr))
            title = "Upgrade Not Available"
            message = "The latest Standard version or higher is already running"
            update_checks_interface = CreateUpdateChecksInterface(start_auto_checks=False)
            if update_checks_interface.standard_update_available:
                title = "Upgrade Started"
                message = "Standard Upgrade by HTTP Started. This may take awhile ..."
                upgrade_interface = CreateUpgradeScriptInterface()
                upgrade_interface.start_kootnet_sensors_upgrade()
        elif url_path == "upgrade-http-dev":
            logger.network_logger.info("** Developer Upgrade - HTTP Initiated by " + str(request.remote_addr))
            title = "Upgrade Not Available"
            message = "The latest Developmental version or higher is already running"
            update_checks_interface = CreateUpdateChecksInterface(start_auto_checks=False)
            if update_checks_interface.developmental_update_available:
                title = "Upgrade Started"
                message = "Development Upgrade by HTTP Started. This may take awhile ..."
                upgrade_interface = CreateUpgradeScriptInterface()
                upgrade_interface.dev_upgrade = True
                upgrade_interface.start_kootnet_sensors_upgrade()
        elif url_path == "upgrade-http-std-clean":
            logger.network_logger.info("** Clean Upgrade - HTTP Initiated by " + str(request.remote_addr))
            title = "Upgrade Started"
            message = "Re-installing the latest Standard version of Kootnet Sensors. This may take awhile ..."
            upgrade_interface = CreateUpgradeScriptInterface()
            upgrade_interface.clean_upgrade = True
            upgrade_interface.start_kootnet_sensors_upgrade()
        elif url_path == "upgrade-http-dev-clean":
            logger.network_logger.info("** DEV Clean Upgrade - HTTP Initiated by " + str(request.remote_addr))
            title = "Upgrade Started"
            message = "Re-installing the latest Developmental version of Kootnet Sensors. This may take awhile ..."
            upgrade_interface = CreateUpgradeScriptInterface()
            upgrade_interface.dev_upgrade = True
            upgrade_interface.clean_upgrade = True
            upgrade_interface.start_kootnet_sensors_upgrade()
        elif url_path == "upgrade-smb-std":
            logger.network_logger.info("* Upgrade - SMB Initiated by " + str(request.remote_addr))
            title = "Upgrade Started"
            message = "Standard Upgrade by SMB Started. This may take awhile ..."
            upgrade_interface = CreateUpgradeScriptInterface()
            upgrade_interface.download_type = download_type_smb
            upgrade_interface.start_kootnet_sensors_upgrade()
        elif url_path == "upgrade-smb-dev":
            logger.network_logger.info("** Developer Upgrade - SMB Initiated by " + str(request.remote_addr))
            title = "Upgrade Started"
            message = "Development Upgrade by SMB Started. This may take awhile ..."
            upgrade_interface = CreateUpgradeScriptInterface()
            upgrade_interface.download_type = download_type_smb
            upgrade_interface.dev_upgrade = True
            upgrade_interface.start_kootnet_sensors_upgrade()
        elif url_path == "upgrade-os":
            logger.network_logger.info("** System OS Upgrade - SMB Initiated by " + str(request.remote_addr))
            title = "Upgrade Started"
            message = "Sensor's operating system upgrade started. This may take awhile ..."
            click_msg = "Kootnet Sensors is currently doing a Operating System Upgrade. " + \
                        "Once complete, the system will restart and this message will disappear"
            notification_short_msg = "Operating System upgrade in progress ...<br>Click Here for more information"
            atpro_notifications.add_custom_message(notification_short_msg, click_msg)
            upgrade_linux_os()
        elif url_path == "upgrade-py3-modules":
            logger.network_logger.info("** Python3 Module Upgrades Initiated by " + str(request.remote_addr))
            title = "Upgrades Started"
            message = "Python3 Module Upgrades Started. This may take awhile ..."
            click_msg = "Kootnet Sensors is currently doing a Python Module Upgrade. " + \
                        "Once complete, the software will restart and this message will disappear"
            notification_short_msg = "Python Module upgrades in progress ...<br>Click Here for more information"
            atpro_notifications.add_custom_message(notification_short_msg, click_msg)
            upgrade_python_pip_modules()
        thread_function(os.system, args=system_command)
    msg_page = get_message_page(title, message, full_reload=False)
    return msg_page


def _start_db_integrity_checks(quick):
    for database in [file_locations.sensor_database, file_locations.sensor_checkin_database,
                     file_locations.mqtt_subscriber_database]:
        system_thread = Thread(target=run_database_integrity_check, args=[database, quick])
        system_thread.daemon = True
        system_thread.start()
