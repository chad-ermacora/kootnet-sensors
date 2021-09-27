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
from operations_modules import software_version
from configuration_modules.app_config_access import primary_config
from upgrade_modules.generic_upgrade_functions import upgrade_python_pip_modules, upgrade_linux_os
from http_server.server_http_auth import auth
from http_server.flask_blueprints.atpro.atpro_generic import get_message_page, get_uptime_str
from sensor_modules import system_access
from sensor_modules import sensor_access

html_system_commands_routes = Blueprint("html_system_commands_routes", __name__)
upgrade_msg = " Upgrade Starting, this may take a few minutes ..."


@html_system_commands_routes.route("/GetSensorID")
def get_sensor_id():
    logger.network_logger.debug("* Sensor's ID sent to " + str(request.remote_addr))
    return str(primary_config.sensor_id)


@html_system_commands_routes.route("/GetHostName")
def get_hostname():
    logger.network_logger.debug("* Sensor's HostName sent to " + str(request.remote_addr))
    return app_cached_variables.hostname


@html_system_commands_routes.route("/GetSystemDateTime")
def get_system_date_time():
    logger.network_logger.debug("* Sensor's Date & Time sent to " + str(request.remote_addr))
    return str(system_access.get_system_datetime())


@html_system_commands_routes.route("/GetSystemUptime")
def get_system_uptime():
    logger.network_logger.debug("* Sensor's Uptime sent to " + str(request.remote_addr))
    return str(get_uptime_str().replace("<br>", " "))


@html_system_commands_routes.route("/GetOSVersion")
def get_operating_system_version():
    logger.network_logger.debug("* Sensor's Operating System Version sent to " + str(request.remote_addr))
    return app_cached_variables.operating_system_name


@html_system_commands_routes.route("/GetSensorVersion")
def get_sensor_program_version():
    logger.network_logger.debug("* Sensor's Version sent to " + str(request.remote_addr))
    return str(software_version.version)


@html_system_commands_routes.route("/GetRAMUsed")
def get_ram_usage_percent():
    logger.network_logger.debug("* Sensor's RAM % used sent to " + str(request.remote_addr))
    return str(system_access.get_ram_space(return_type=3))


@html_system_commands_routes.route("/GetRAMFree")
def get_ram_free():
    logger.network_logger.debug("* Sensor's Free RAM sent to " + str(request.remote_addr))
    return str(system_access.get_ram_space(return_type=0))


@html_system_commands_routes.route("/GetRAMTotal")
def get_ram_total():
    logger.network_logger.debug("* Sensor's Total RAM amount sent to " + str(request.remote_addr))
    return str(app_cached_variables.total_ram_memory)


@html_system_commands_routes.route("/GetRAMTotalSizeType")
def get_ram_total_size_type():
    logger.network_logger.debug("* Sensor's Total RAM amount size type sent to " + str(request.remote_addr))
    return "GB"


@html_system_commands_routes.route("/GetUsedDiskSpace")
def get_disk_usage_gb():
    logger.network_logger.debug("* Sensor's Used Disk Space as GBs sent to " + str(request.remote_addr))
    return str(system_access.get_disk_space(return_type=1))


@html_system_commands_routes.route("/GetFreeDiskSpace")
def get_disk_free_gb():
    logger.network_logger.debug("* Sensor's Free Disk Space as GBs sent to " + str(request.remote_addr))
    return str(system_access.get_disk_space(return_type=0))


@html_system_commands_routes.route("/GetProgramLastUpdated")
def get_sensor_program_last_updated():
    logger.network_logger.debug("* Sensor's Program Last Updated sent to " + str(request.remote_addr))
    return app_cached_variables.program_last_updated


@html_system_commands_routes.route("/UpgradeOnline")
@auth.login_required
def upgrade_http():
    logger.network_logger.info("* Upgrade - HTTP Initiated by " + str(request.remote_addr))
    app_generic_functions.thread_function(os.system, args=app_cached_variables.bash_commands["UpgradeOnline"])
    msg = "HTTP" + upgrade_msg
    return get_message_page("Upgrade Started", msg, page_url="sensor-dashboard")


@html_system_commands_routes.route("/UpgradeOnlineDev")
@auth.login_required
def upgrade_http_dev():
    logger.network_logger.info("** Developer Upgrade - HTTP Initiated by " + str(request.remote_addr))
    app_generic_functions.thread_function(os.system, args=app_cached_variables.bash_commands["UpgradeOnlineDEV"])
    msg = "HTTP Development" + upgrade_msg
    return get_message_page("Upgrade Started", msg, page_url="sensor-dashboard")


@html_system_commands_routes.route("/UpgradeOnlineClean")
@auth.login_required
def upgrade_clean_http():
    logger.network_logger.info("** Clean Upgrade - HTTP Initiated by " + str(request.remote_addr))
    app_generic_functions.thread_function(os.system, args=app_cached_variables.bash_commands["UpgradeOnlineClean"])
    msg = "HTTP Clean" + upgrade_msg
    return get_message_page("Upgrade Started", msg, page_url="sensor-dashboard")


@html_system_commands_routes.route("/UpgradeOnlineCleanDEV")
@auth.login_required
def upgrade_clean_http_dev():
    logger.network_logger.info("** DEV Clean Upgrade - HTTP Initiated by " + str(request.remote_addr))
    app_generic_functions.thread_function(os.system, args=app_cached_variables.bash_commands["UpgradeOnlineCleanDEV"])
    msg = "HTTP Development Clean" + upgrade_msg
    return get_message_page("Upgrade Started", msg, page_url="sensor-dashboard")


@html_system_commands_routes.route("/UpgradeSMB")
@auth.login_required
def upgrade_smb():
    logger.network_logger.info("* Upgrade - SMB Initiated by " + str(request.remote_addr))
    app_generic_functions.thread_function(os.system, args=app_cached_variables.bash_commands["UpgradeSMB"])
    msg = "SMB" + upgrade_msg
    return get_message_page("Upgrade Started", msg, page_url="sensor-dashboard")


# NOTE SMB needs to be setup before clean SMB upgrades can be done.  Disabling by default.
# @html_system_commands_routes.route("/UpgradeSMBClean")
# @auth.login_required
# def upgrade_clean_smb():
#     logger.network_logger.info("** Clean Upgrade - SMB Initiated by " + str(request.remote_addr))
#     app_generic_functions.thread_function(os.system, args=app_cached_variables.bash_commands["UpgradeSMBClean"])
#     return message_and_return("SMB Clean Upgrade Started", text_message2=message_few_min, url="/SensorInformation")
#
#
# @html_system_commands_routes.route("/UpgradeSMBCleanDEV")
# @auth.login_required
# def upgrade_clean_smb_dev():
#     logger.network_logger.info("** DEV Clean Upgrade - SMB Initiated by " + str(request.remote_addr))
#     app_generic_functions.thread_function(os.system, args=app_cached_variables.bash_commands["UpgradeSMBCleanDEV"])
#     return message_and_return("DEV SMB Clean Upgrade Started", text_message2=message_few_min, url="/SensorInformation")


@html_system_commands_routes.route("/UpgradeSMBDev")
@auth.login_required
def upgrade_smb_dev():
    logger.network_logger.info("** Developer Upgrade - SMB Initiated by " + str(request.remote_addr))
    app_generic_functions.thread_function(os.system, args=app_cached_variables.bash_commands["UpgradeSMBDEV"])
    msg = "SMB Development" + upgrade_msg
    return get_message_page("Upgrade Started", msg, page_url="sensor-dashboard")


# Old Method, upgrade or remove?
# @html_system_commands_routes.route("/inkupg")
# @auth.login_required
# def upgrade_rp_controller():
#     logger.network_logger.info("* Upgrade - E-Ink Mobile Initiated by " + str(request.remote_addr))
#     app_generic_functions.thread_function(os.system, args=app_cached_variables.bash_commands["inkupg"])
#     return "OK"


@html_system_commands_routes.route("/RestartServices")
@auth.login_required
def services_restart():
    logger.network_logger.info("** Service restart Initiated by " + str(request.remote_addr))
    system_access.restart_services()
    return get_message_page("Restarting Program", page_url="sensor-dashboard")


@html_system_commands_routes.route("/RebootSystem")
@auth.login_required
def system_reboot():
    logger.network_logger.info("** System Reboot Initiated by " + str(request.remote_addr))
    app_generic_functions.thread_function(os.system, args=app_cached_variables.bash_commands["RebootSystem"])
    return get_message_page("Rebooting System", message="This may take a few Minutes ...", page_url="sensor-dashboard")


@html_system_commands_routes.route("/ShutdownSystem")
@auth.login_required
def system_shutdown():
    logger.network_logger.info("** System Shutdown Initiated by " + str(request.remote_addr))
    app_generic_functions.thread_function(os.system, args=app_cached_variables.bash_commands["ShutdownSystem"])
    msg = "You must physically turn the sensor back on for future access"
    return get_message_page("Shutting Down System", message=msg, page_url="sensor-dashboard")


@html_system_commands_routes.route("/UpgradeSystemOS")
@auth.login_required
def upgrade_system_os():
    logger.network_logger.info("** OS Upgrade and Reboot Initiated by " + str(request.remote_addr))
    if app_cached_variables.sensor_ready_for_upgrade:
        upgrade_linux_os()
    else:
        logger.network_logger.warning("* Upgrades Already Running")
    msg = "Upgrading the Operating System requires Internet & may take up to an hour or more.<br>"
    msg = msg + "Once complete, the system will automatically reboot."
    return get_message_page("Upgrading Operating System", message=msg, page_url="sensor-dashboard")


@html_system_commands_routes.route("/UpdatePipModules")
@auth.login_required
def upgrade_pip_modules():
    logger.network_logger.info("** Program pip3 modules upgrade Initiated by " + str(request.remote_addr))
    if app_cached_variables.sensor_ready_for_upgrade:
        upgrade_python_pip_modules()
    else:
        logger.network_logger.warning("* Upgrades Already Running")
    msg = "Python Modules for Kootnet Sensors are being upgraded. Once complete, the program will be restarted."
    return get_message_page("Upgrading Python Modules", message=msg, page_url="sensor-dashboard")


@html_system_commands_routes.route("/CreateNewSelfSignedSSL")
@auth.login_required
def create_new_self_signed_ssl():
    logger.network_logger.info("** Create New Self-Signed SSL Initiated by " + str(request.remote_addr))
    os.system("rm -f -r " + file_locations.http_ssl_folder)
    system_access.restart_services()
    msg = "You may have to clear your browser cache to re-gain access. The program is now restarting."
    return get_message_page("New SSL Key Created", message=msg, page_url="sensor-dashboard")


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
