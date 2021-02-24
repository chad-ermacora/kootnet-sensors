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
from http_server.server_http_auth import auth
from http_server.server_http_generic_functions import message_and_return
from sensor_modules import sensor_access

html_system_commands_routes = Blueprint("html_system_commands_routes", __name__)
sensor_network_commands = app_cached_variables.CreateNetworkGetCommands()
message_few_min = "This may take a few minutes ..."


@html_system_commands_routes.route("/CheckOnlineStatus")
def check_online():
    logger.network_logger.debug("Sensor Status Checked by " + str(request.remote_addr))
    return "OK"


@html_system_commands_routes.route("/TestLogin")
@auth.login_required
def test_login():
    return "OK"


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
    return str(sensor_access.get_system_datetime())


@html_system_commands_routes.route("/GetSystemUptime")
def get_system_uptime():
    logger.network_logger.debug("* Sensor's Uptime sent to " + str(request.remote_addr))
    return str(sensor_access.get_uptime_str())


@html_system_commands_routes.route("/GetOSVersion")
def get_operating_system_version():
    logger.network_logger.debug("* Sensor's Operating System Version sent to " + str(request.remote_addr))
    return str(sensor_access.get_operating_system_name())


@html_system_commands_routes.route("/GetSensorVersion")
def get_sensor_program_version():
    logger.network_logger.debug("* Sensor's Version sent to " + str(request.remote_addr))
    return str(software_version.version)


@html_system_commands_routes.route("/GetRAMUsed")
def get_ram_usage_percent():
    logger.network_logger.debug("* Sensor's RAM % used sent to " + str(request.remote_addr))
    return str(sensor_access.get_memory_usage_percent())


@html_system_commands_routes.route("/GetRAMTotal")
def get_ram_total():
    logger.network_logger.debug("* Sensor's Total RAM amount sent to " + str(request.remote_addr))
    return str(app_cached_variables.total_ram_memory)


@html_system_commands_routes.route("/GetRAMTotalSizeType")
def get_ram_total_size_type():
    logger.network_logger.debug("* Sensor's Total RAM amount size type sent to " + str(request.remote_addr))
    return app_cached_variables.total_ram_memory_size_type


@html_system_commands_routes.route("/GetUsedDiskSpace")
def get_disk_usage_percent():
    logger.network_logger.debug("* Sensor's Used Disk Space as GBs sent to " + str(request.remote_addr))
    return str(sensor_access.get_disk_usage_gb())


@html_system_commands_routes.route("/GetProgramLastUpdated")
def get_sensor_program_last_updated():
    logger.network_logger.debug("* Sensor's Program Last Updated sent to " + str(request.remote_addr))
    return sensor_access.get_last_updated()


@html_system_commands_routes.route("/UpgradeOnline")
@auth.login_required
def upgrade_http():
    logger.network_logger.info("* Upgrade - HTTP Initiated by " + str(request.remote_addr))
    app_generic_functions.thread_function(os.system, args=app_cached_variables.bash_commands["UpgradeOnline"])
    return message_and_return("HTTP Upgrade Started", text_message2=message_few_min, url="/SensorInformation")


@html_system_commands_routes.route("/UpgradeOnlineClean")
@auth.login_required
def upgrade_clean_http():
    logger.network_logger.info("** Clean Upgrade - HTTP Initiated by " + str(request.remote_addr))
    app_generic_functions.thread_function(os.system, args=app_cached_variables.bash_commands["UpgradeOnlineClean"])
    return message_and_return("HTTP Clean Upgrade Started", text_message2=message_few_min, url="/SensorInformation")


@html_system_commands_routes.route("/UpgradeOnlineCleanDEV")
@auth.login_required
def upgrade_clean_http_dev():
    logger.network_logger.info("** DEV Clean Upgrade - HTTP Initiated by " + str(request.remote_addr))
    app_generic_functions.thread_function(os.system, args=app_cached_variables.bash_commands["UpgradeOnlineCleanDEV"])
    return message_and_return("DEV HTTP Clean Upgrade Started", text_message2=message_few_min, url="/SensorInformation")


@html_system_commands_routes.route("/UpgradeOnlineDev")
@auth.login_required
def upgrade_http_dev():
    logger.network_logger.info("** Developer Upgrade - HTTP Initiated by " + str(request.remote_addr))
    app_generic_functions.thread_function(os.system, args=app_cached_variables.bash_commands["UpgradeOnlineDEV"])
    return message_and_return("HTTP Developer Upgrade Started", text_message2=message_few_min, url="/SensorInformation")


@html_system_commands_routes.route("/UpgradeSMB")
@auth.login_required
def upgrade_smb():
    logger.network_logger.info("* Upgrade - SMB Initiated by " + str(request.remote_addr))
    app_generic_functions.thread_function(os.system, args=app_cached_variables.bash_commands["UpgradeSMB"])
    return message_and_return("SMB Upgrade Started", text_message2=message_few_min, url="/SensorInformation")


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
    return message_and_return("SMB Developer Upgrade Started", text_message2=message_few_min, url="/SensorInformation")


@html_system_commands_routes.route("/inkupg")
@auth.login_required
def upgrade_rp_controller():
    logger.network_logger.info("* Upgrade - E-Ink Mobile Initiated by " + str(request.remote_addr))
    app_generic_functions.thread_function(os.system, args=app_cached_variables.bash_commands["inkupg"])
    return "OK"


@html_system_commands_routes.route("/RestartServices")
@auth.login_required
def services_restart():
    message = "This should only take 5 to 30 seconds."
    logger.network_logger.info("** Service restart Initiated by " + str(request.remote_addr))
    app_generic_functions.thread_function(sensor_access.restart_services)
    return message_and_return("Restarting Sensor Service", text_message2=message, url="/SensorInformation")


@html_system_commands_routes.route("/RebootSystem")
@auth.login_required
def system_reboot():
    logger.network_logger.info("** System Reboot Initiated by " + str(request.remote_addr))
    app_generic_functions.thread_function(os.system, args=app_cached_variables.bash_commands["RebootSystem"])
    return message_and_return("Sensor Rebooting", text_message2=message_few_min, url="/SensorInformation")


@html_system_commands_routes.route("/ShutdownSystem")
@auth.login_required
def system_shutdown():
    logger.network_logger.info("** System Shutdown Initiated by " + str(request.remote_addr))
    message2 = "You will be unable to access it until some one turns it back on."
    app_generic_functions.thread_function(os.system, args=app_cached_variables.bash_commands["ShutdownSystem"])
    return message_and_return("Sensor Shutting Down", text_message2=message2, url="/")


@html_system_commands_routes.route("/UpgradeSystemOS")
@auth.login_required
def upgrade_system_os():
    logger.network_logger.info("** OS Upgrade and Reboot Initiated by " + str(request.remote_addr))
    message = "An Upgrade is already running"
    message2 = "Once complete, the sensor programs will be restarted.\n" + message_few_min
    if app_cached_variables.sensor_ready_for_upgrade:
        message = "Operating System Upgrade Started"
        app_cached_variables.sensor_ready_for_upgrade = False
        app_generic_functions.thread_function(_upgrade_linux_os)
    else:
        logger.network_logger.warning("* Upgrades Already Running")
    return message_and_return(message, text_message2=message2, url="/SensorInformation")


def _upgrade_linux_os():
    """ Runs a bash command to upgrade the Linux System with apt-get. """
    try:
        os.system(app_cached_variables.bash_commands["UpgradeSystemOS"])
        logger.primary_logger.warning("Linux OS Upgrade Done")
        logger.primary_logger.info("Rebooting System")
        os.system(app_cached_variables.bash_commands["RebootSystem"])
    except Exception as error:
        logger.primary_logger.error("Linux OS Upgrade Error: " + str(error))


@html_system_commands_routes.route("/UpdatePipModules")
@auth.login_required
def upgrade_pip_modules():
    logger.network_logger.info("** Program pip3 modules upgrade Initiated by " + str(request.remote_addr))
    message = "An Upgrade is already running"
    message2 = "Once complete, the sensor programs will be restarted.\n" + message_few_min
    if app_cached_variables.sensor_ready_for_upgrade:
        app_cached_variables.sensor_ready_for_upgrade = False
        with open(file_locations.program_root_dir + "/requirements.txt") as file:
            requirements_text = file.readlines()
            app_generic_functions.thread_function(_pip_upgrades, args=requirements_text)
            message = "Python3 module upgrades Started"
    else:
        logger.network_logger.warning("* Upgrades Already Running")
    return message_and_return(message, text_message2=message2, url="/SensorInformation")


def _pip_upgrades(requirements_text):
    for line in requirements_text:
        if line[0] != "#":
            command = file_locations.sensor_data_dir + "/env/bin/pip3 install --upgrade " + line.strip()
            os.system(command)
    logger.primary_logger.info("Python3 Module Upgrades Complete")
    os.system(app_cached_variables.bash_commands["RestartService"])


@html_system_commands_routes.route("/CreateNewSelfSignedSSL")
@auth.login_required
def create_new_self_signed_ssl():
    logger.network_logger.info("** Create New Self-Signed SSL Initiated by " + str(request.remote_addr))
    message2 = "Once complete, the sensor programs will be restarted. " + message_few_min
    os.system("rm -f -r " + file_locations.http_ssl_folder)
    app_generic_functions.thread_function(sensor_access.restart_services)
    return message_and_return("Creating new Self-Signed SSL", text_message2=message2, url="/SensorInformation")


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
