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
from flask import Blueprint, request, render_template
from operations_modules import logger
from operations_modules import app_cached_variables
from configuration_modules.app_config_access import primary_config
from operations_modules.app_generic_functions import thread_function
from upgrade_modules.generic_upgrade_functions import upgrade_python_pip_modules, upgrade_linux_os
from upgrade_modules.upgrade_functions import start_kootnet_sensors_upgrade, download_type_http, download_type_smb
from http_server.server_http_auth import auth
from http_server.flask_blueprints.atpro.atpro_generic import get_message_page
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
    msg_page = get_message_page(title, message, full_reload=False)
    if running_as_service and running_with_root and not primary_config.demo_mode:
        title = "Error!"
        message = "An Error occurred"
        system_command = "exit"
        if str(url_path) == "system-restart-program":
            logger.network_logger.info("** Program Restart Initiated by " + str(request.remote_addr))
            title = "Restarting Program"
            message = "The web interface will be temporarily unavailable"
            system_command = app_cached_variables.bash_commands["RestartService"]
        elif str(url_path) == "system-restart":
            logger.network_logger.info("** System Restart Initiated by " + str(request.remote_addr))
            title = "Restarting System"
            message = "The web interface will be temporarily unavailable"
            system_command = app_cached_variables.bash_commands["RebootSystem"]
        elif str(url_path) == "system-shutdown":
            logger.network_logger.info("** System Shutdown Initiated by " + str(request.remote_addr))
            title = "Shutting Down"
            message = "You will be unable to access the web interface until some one turns the sensor back on"
            system_command = app_cached_variables.bash_commands["ShutdownSystem"]
        elif str(url_path) == "upgrade-http-std":
            logger.network_logger.info("* Upgrade - HTTP Initiated by " + str(request.remote_addr))
            title = "Upgrade Not Available"
            message = "The latest Standard version or higher is already running"
            if app_cached_variables.software_update_available:
                title = "Upgrade Started"
                message = "Standard Upgrade by HTTP Started. This may take awhile ..."
                start_kootnet_sensors_upgrade(dev_upgrade=False, clean_upgrade=False, download_type=download_type_http)
                click_msg = "Kootnet Sensors is currently doing a Standard Upgrade. " + \
                            "Once complete, the software will restart and this message will disappear"
                atpro_notifications.add_custom_message("KS Std HTTP upgrade in progress ...", click_msg)
        elif str(url_path) == "upgrade-http-dev":
            logger.network_logger.info("** Developer Upgrade - HTTP Initiated by " + str(request.remote_addr))
            title = "Upgrade Not Available"
            message = "The latest Developmental version or higher is already running"
            if app_cached_variables.software_update_dev_available:
                title = "Upgrade Started"
                message = "Development Upgrade by HTTP Started. This may take awhile ..."
                start_kootnet_sensors_upgrade(dev_upgrade=True, clean_upgrade=False, download_type=download_type_http)
                click_msg = "Kootnet Sensors is currently doing a Developmental Upgrade. " + \
                            "Once complete, the software will restart and this message will disappear"
                atpro_notifications.add_custom_message("KS Dev HTTP upgrade in progress ...", click_msg)
        elif str(url_path) == "upgrade-http-std-clean":
            logger.network_logger.info("** Clean Upgrade - HTTP Initiated by " + str(request.remote_addr))
            title = "Upgrade Started"
            message = "Re-installing the latest Standard version of Kootnet Sensors. This may take awhile ..."
            start_kootnet_sensors_upgrade(dev_upgrade=False, clean_upgrade=True, download_type=download_type_http)
            click_msg = "Kootnet Sensors is currently Re-installing the latest Standard version of Kootnet Sensors. " + \
                        "Once complete, the software will restart and this message will disappear"
            atpro_notifications.add_custom_message("KS Std Re-install HTTP in progress ...", click_msg)
        elif str(url_path) == "upgrade-http-dev-clean":
            logger.network_logger.info("** DEV Clean Upgrade - HTTP Initiated by " + str(request.remote_addr))
            title = "Upgrade Started"
            message = "Re-installing the latest Developmental version of Kootnet Sensors. This may take awhile ..."
            start_kootnet_sensors_upgrade(dev_upgrade=True, clean_upgrade=True, download_type=download_type_http)
            click_msg = "Kootnet Sensors is currently Re-installing the latest Developmental version of " + \
                        "Kootnet Sensors. Once complete, the software will restart and this message will disappear"
            atpro_notifications.add_custom_message("KS Dev Re-install HTTP in progress ...", click_msg)
        elif str(url_path) == "upgrade-smb-std":
            logger.network_logger.info("* Upgrade - SMB Initiated by " + str(request.remote_addr))
            title = "Upgrade Started"
            message = "Standard Upgrade by SMB Started. This may take awhile ..."
            start_kootnet_sensors_upgrade(dev_upgrade=False, clean_upgrade=False, download_type=download_type_smb)
            click_msg = "Kootnet Sensors is currently doing a SMB Standard Upgrade. " + \
                        "Once complete, the software will restart and this message will disappear"
            atpro_notifications.add_custom_message("KS Std SMB upgrade in progress ...", click_msg)
        elif str(url_path) == "upgrade-smb-dev":
            logger.network_logger.info("** Developer Upgrade - SMB Initiated by " + str(request.remote_addr))
            title = "Upgrade Started"
            message = "Development Upgrade by SMB Started. This may take awhile ..."
            start_kootnet_sensors_upgrade(dev_upgrade=True, clean_upgrade=False, download_type=download_type_smb)
            click_msg = "Kootnet Sensors is currently doing a SMB Developmental Upgrade. " + \
                        "Once complete, the software will restart and this message will disappear"
            atpro_notifications.add_custom_message("KS Dev SMB upgrade in progress ...", click_msg)
        elif str(url_path) == "upgrade-os":
            logger.network_logger.info("** System OS Upgrade - SMB Initiated by " + str(request.remote_addr))
            title = "Upgrade Started"
            message = "Sensor's operating system upgrade started. This may take awhile ..."
            click_msg = "Kootnet Sensors is currently doing a Operating System Upgrade. " + \
                        "Once complete, the system will restart and this message will disappear"
            atpro_notifications.add_custom_message("Operating System upgrade in progress ...", click_msg)
            upgrade_linux_os()
        elif str(url_path) == "upgrade-py3-modules":
            logger.network_logger.info("** Python3 Module Upgrades Initiated by " + str(request.remote_addr))
            title = "Upgrades Started"
            message = "Python3 Module Upgrades Started. This may take awhile ..."
            click_msg = "Kootnet Sensors is currently doing a Python Module Upgrade. " + \
                        "Once complete, the software will restart and this message will disappear"
            atpro_notifications.add_custom_message("Python Module upgrades in progress ...", click_msg)
            upgrade_python_pip_modules()
        msg_page = get_message_page(title, message, full_reload=False)
        thread_function(os.system, args=system_command)
    return msg_page
