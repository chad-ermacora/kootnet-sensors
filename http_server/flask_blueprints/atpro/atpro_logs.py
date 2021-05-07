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
from operations_modules import logger
from operations_modules import file_locations
from operations_modules import app_cached_variables
from operations_modules.app_generic_functions import zip_files
from flask import Blueprint, render_template, request, send_file
from http_server.server_http_auth import auth

html_atpro_logs_routes = Blueprint("html_atpro_logs_routes", __name__)


@html_atpro_logs_routes.route("/atpro/sensor-logs")
def html_atpro_sensor_logs():
    return render_template("ATPro_admin/page_templates/sensor-logs.html")


@html_atpro_logs_routes.route('/atpro/logs/<path:url_path>')
@auth.login_required
def atpro_get_log(url_path):
    if url_path == "log-download-all-zipped":
        zip_name = "Logs_" + app_cached_variables.ip.split(".")[-1] + app_cached_variables.hostname + ".zip"
        return_zip_file = zip_files(
            ["log_primary.txt", "log_network.txt", "log_sensors.txt"],
            [logger.get_sensor_log(file_locations.primary_log, max_lines=0),
             logger.get_sensor_log(file_locations.network_log, max_lines=0),
             logger.get_sensor_log(file_locations.sensors_log, max_lines=0)]
        )
        if type(return_zip_file) is str:
            return return_zip_file
        else:
            return send_file(return_zip_file, as_attachment=True, attachment_filename=zip_name)
    elif url_path == "log-primary":
        return logger.get_sensor_log(file_locations.primary_log)
    elif url_path == "log-primary-header":
        primary_log_lines = logger.get_number_of_log_entries(file_locations.primary_log)
        return _get_log_view_message("Primary Log", primary_log_lines)
    elif url_path == "log-network":
        return logger.get_sensor_log(file_locations.network_log)
    elif url_path == "log-network-header":
        network_log_lines = logger.get_number_of_log_entries(file_locations.network_log)
        return _get_log_view_message("Network Log", network_log_lines)
    elif url_path == "log-sensors":
        return logger.get_sensor_log(file_locations.sensors_log)
    elif url_path == "log-sensors-header":
        sensors_log_lines = logger.get_number_of_log_entries(file_locations.sensors_log)
        return _get_log_view_message("Sensors Log", sensors_log_lines)


@html_atpro_logs_routes.route('/atpro/delete-log/<path:url_path>')
@auth.login_required
def atpro_delete_log(url_path):
    return_message = "Invalid Path"
    if url_path == "primary":
        logger.network_logger.info("** Primary Sensor Log Deleted by " + str(request.remote_addr))
        logger.clear_primary_log()
        return_message = "Primary Log Deleted"
    elif url_path == "network":
        logger.network_logger.info("** Network Sensor Log Deleted by " + str(request.remote_addr))
        logger.clear_network_log()
        return_message = "Network Log Deleted"
    elif url_path == "sensors":
        logger.network_logger.info("** Sensors Log Deleted by " + str(request.remote_addr))
        logger.clear_sensor_log()
        return_message = "Sensors Log Deleted"
    return return_message


def _get_log_view_message(log_name, log_lines_length):
    if log_lines_length:
        if logger.max_log_lines_return > log_lines_length:
            text_log_entries_return = str(log_lines_length) + "/" + str(log_lines_length)
        else:
            text_log_entries_return = str(logger.max_log_lines_return) + "/" + str(log_lines_length)
    else:
        text_log_entries_return = "0/0"
    return log_name + " - " + text_log_entries_return
