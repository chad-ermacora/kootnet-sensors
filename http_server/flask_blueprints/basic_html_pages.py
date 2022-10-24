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
from flask import Blueprint, render_template
from operations_modules import logger
from operations_modules import app_cached_variables
from operations_modules.software_version import version
from sensor_modules import system_access

html_basic_routes = Blueprint("html_basic_routes", __name__)


@html_basic_routes.route("/")
@html_basic_routes.route("/index")
@html_basic_routes.route("/index.html")
def html_index():
    disk_message = "<b style='color: green;'>Okay</b>"

    disk_percent_used = system_access.get_disk_space(return_type=3)
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
                           DateTime=system_access.get_system_datetime(),
                           SensorID=app_cached_variables.tmp_sensor_id,
                           HostName=app_cached_variables.hostname,
                           LocalIP=app_cached_variables.ip,
                           DiskSpaceMessage=disk_message,
                           MemoryUsed=str(system_access.get_program_mem_usage()),
                           DateTimeUTC=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"))
