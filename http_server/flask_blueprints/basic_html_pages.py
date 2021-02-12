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
from datetime import datetime
from flask import Blueprint, render_template, request
from operations_modules import logger
from operations_modules import app_cached_variables
from operations_modules.software_version import version
from http_server.server_http_auth import auth
from http_server.server_http_generic_functions import get_html_hidden_state
from sensor_modules import sensor_access

html_basic_routes = Blueprint("html_basic_routes", __name__)


@html_basic_routes.route("/robots.txt")
def no_robots():
    return "User-agent: *\nDisallow: /"


@html_basic_routes.route("/")
@html_basic_routes.route("/index")
@html_basic_routes.route("/index.html")
def html_index():
    disk_message = "<b style='color: green;'>Okay</b>"

    disk_percent_used = sensor_access.get_disk_usage_percent()
    if disk_percent_used is not None:
        try:
            disk_percent_used = float(disk_percent_used)
            if disk_percent_used > 90.0:
                disk_message = "<b style='color: yellow;'>Low Disk Space</b>"
        except Exception as error:
            logger.primary_logger.warning("Error getting disk usage: " + str(error))
            disk_message = "<b style='color: yellow;'>Error</b>"
    return render_template("index.html",
                           KootnetVersion=version,
                           DateTime=sensor_access.get_system_datetime(),
                           SensorID=app_cached_variables.tmp_sensor_id,
                           HostName=app_cached_variables.hostname,
                           LocalIP=app_cached_variables.ip,
                           DiskSpaceMessage=disk_message,
                           DateTimeUTC=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"))


@html_basic_routes.route("/Quick")
@html_basic_routes.route("/SystemCommands")
@auth.login_required
def html_system_management():
    logger.network_logger.debug("** System Commands accessed from " + str(request.remote_addr))
    return render_template("system_commands.html",
                           PageURL="/SystemCommands",
                           RestartServiceHidden=get_html_hidden_state(app_cached_variables.html_service_restart),
                           RebootSensorHidden=get_html_hidden_state(app_cached_variables.html_sensor_reboot),
                           LoginUserName=app_cached_variables.http_flask_user)


@html_basic_routes.route("/SensorHelp")
def view_help_file():
    logger.network_logger.debug("* Sensor Help Viewed from " + str(request.remote_addr))
    return render_template("sensor_help_page.html")
