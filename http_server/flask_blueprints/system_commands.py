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
from flask import Blueprint, request
from operations_modules import logger
from operations_modules import file_locations
from operations_modules import app_generic_functions
from operations_modules import app_cached_variables
from configuration_modules import app_config_access
from upgrade_modules.generic_upgrade_functions import upgrade_python_pip_modules, upgrade_linux_os
from upgrade_modules.upgrade_functions import start_kootnet_sensors_upgrade, download_type_smb
from http_server.server_http_auth import auth
from http_server.flask_blueprints.atpro.atpro_generic import get_message_page
from sensor_modules import system_access
from sensor_modules import sensor_access

html_system_commands_routes = Blueprint("html_system_commands_routes", __name__)
upgrade_msg = " Upgrade Starting, this may take a few minutes ..."
demo_mode_enabled_msg = "Demo mode enabled, function disabled"


@html_system_commands_routes.route("/UpgradeOnline")
@auth.login_required
def upgrade_http():
    if not app_config_access.primary_config.demo_mode:
        logger.network_logger.info("* Upgrade - HTTP Initiated by " + str(request.remote_addr))
        start_kootnet_sensors_upgrade()
        msg = "HTTP" + upgrade_msg
        return get_message_page("Upgrade Started", msg, page_url="sensor-dashboard")
    return demo_mode_enabled_msg


@html_system_commands_routes.route("/UpgradeOnlineDev")
@auth.login_required
def upgrade_http_dev():
    if not app_config_access.primary_config.demo_mode:
        logger.network_logger.info("** Developer Upgrade - HTTP Initiated by " + str(request.remote_addr))
        start_kootnet_sensors_upgrade(dev_upgrade=True)
        msg = "HTTP Development" + upgrade_msg
        return get_message_page("Upgrade Started", msg, page_url="sensor-dashboard")
    return demo_mode_enabled_msg


@html_system_commands_routes.route("/UpgradeOnlineClean")
@auth.login_required
def upgrade_clean_http():
    if not app_config_access.primary_config.demo_mode:
        logger.network_logger.info("** Clean Upgrade - HTTP Initiated by " + str(request.remote_addr))
        start_kootnet_sensors_upgrade(clean_upgrade=True)
        msg = "HTTP Clean" + upgrade_msg
        return get_message_page("Upgrade Started", msg, page_url="sensor-dashboard")
    return demo_mode_enabled_msg


@html_system_commands_routes.route("/UpgradeOnlineCleanDEV")
@auth.login_required
def upgrade_clean_http_dev():
    if not app_config_access.primary_config.demo_mode:
        logger.network_logger.info("** DEV Clean Upgrade - HTTP Initiated by " + str(request.remote_addr))
        start_kootnet_sensors_upgrade(dev_upgrade=True, clean_upgrade=True)
        msg = "HTTP Development Clean" + upgrade_msg
        return get_message_page("Upgrade Started", msg, page_url="sensor-dashboard")
    return demo_mode_enabled_msg


@html_system_commands_routes.route("/UpgradeSMB")
@auth.login_required
def upgrade_smb():
    if not app_config_access.primary_config.demo_mode:
        logger.network_logger.info("* Upgrade - SMB Initiated by " + str(request.remote_addr))
        start_kootnet_sensors_upgrade(download_type=download_type_smb)
        msg = "SMB" + upgrade_msg
        return get_message_page("Upgrade Started", msg, page_url="sensor-dashboard")
    return demo_mode_enabled_msg


@html_system_commands_routes.route("/UpgradeSMBDev")
@auth.login_required
def upgrade_smb_dev():
    if not app_config_access.primary_config.demo_mode:
        logger.network_logger.info("** Developer Upgrade - SMB Initiated by " + str(request.remote_addr))
        start_kootnet_sensors_upgrade(download_type=download_type_smb, dev_upgrade=True)
        msg = "SMB Development" + upgrade_msg
        return get_message_page("Upgrade Started", msg, page_url="sensor-dashboard")
    return demo_mode_enabled_msg


@html_system_commands_routes.route("/RestartServices")
@auth.login_required
def services_restart():
    if not app_config_access.primary_config.demo_mode:
        logger.network_logger.info("** Service restart Initiated by " + str(request.remote_addr))
        system_access.restart_services()
        return get_message_page("Restarting Program", page_url="sensor-dashboard")
    return demo_mode_enabled_msg


@html_system_commands_routes.route("/RebootSystem")
@auth.login_required
def system_reboot():
    if not app_config_access.primary_config.demo_mode:
        logger.network_logger.info("** System Reboot Initiated by " + str(request.remote_addr))
        app_generic_functions.thread_function(os.system, args=app_cached_variables.bash_commands["RebootSystem"])
        return_msg = "This may take a few Minutes ..."
        return get_message_page("Rebooting System", message=return_msg, page_url="sensor-dashboard")
    return demo_mode_enabled_msg


@html_system_commands_routes.route("/ShutdownSystem")
@auth.login_required
def system_shutdown():
    if not app_config_access.primary_config.demo_mode:
        logger.network_logger.info("** System Shutdown Initiated by " + str(request.remote_addr))
        app_generic_functions.thread_function(os.system, args=app_cached_variables.bash_commands["ShutdownSystem"])
        msg = "You must physically turn the sensor back on for future access"
        return get_message_page("Shutting Down System", message=msg, page_url="sensor-dashboard")
    return demo_mode_enabled_msg


@html_system_commands_routes.route("/UpgradeSystemOS")
@auth.login_required
def upgrade_system_os():
    if not app_config_access.primary_config.demo_mode:
        logger.network_logger.info("** OS Upgrade and Reboot Initiated by " + str(request.remote_addr))
        upgrade_linux_os()
        msg = "Upgrading the Operating System requires Internet & may take up to an hour or more.<br>"
        msg = msg + "Once complete, the system will automatically reboot."
        return get_message_page("Upgrading Operating System", message=msg, page_url="sensor-dashboard")
    return demo_mode_enabled_msg


@html_system_commands_routes.route("/UpdatePipModules")
@auth.login_required
def upgrade_pip_modules():
    if not app_config_access.primary_config.demo_mode:
        logger.network_logger.info("** Program pip3 modules upgrade Initiated by " + str(request.remote_addr))
        upgrade_python_pip_modules()
        msg = "Python Modules for Kootnet Sensors are being upgraded. Once complete, the program will be restarted."
        return get_message_page("Upgrading Python Modules", message=msg, page_url="sensor-dashboard")
    return demo_mode_enabled_msg


@html_system_commands_routes.route("/CreateNewSelfSignedSSL")
@auth.login_required
def create_new_self_signed_ssl():
    if not app_config_access.primary_config.demo_mode:
        logger.network_logger.info("** Create New Self-Signed SSL Initiated by " + str(request.remote_addr))
        os.system("rm -f -r " + file_locations.http_ssl_folder)
        system_access.restart_services()
        msg = "You may have to clear your browser cache to re-gain access. The program is now restarting."
        return get_message_page("New SSL Key Created", message=msg, page_url="sensor-dashboard")
    return demo_mode_enabled_msg


@html_system_commands_routes.route("/DisplayText", methods=["PUT"])
def display_text():
    max_length_text_message = 250
    logger.network_logger.info("* Show Message on Display Initiated by " + str(request.remote_addr))
    text_message = request.form.get("command_data")
    if len(text_message) > max_length_text_message:
        logger.network_logger.warning("Message sent to Display is longer then " + str(max_length_text_message) +
                                      ". Truncating to " + str(max_length_text_message) + " Character")
        text_message = text_message[:max_length_text_message]
    sensor_access.display_message(text_message)
    return "OK"
