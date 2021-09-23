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
from flask import Blueprint, render_template, request
from http_server.server_http_auth import auth
from http_server.flask_blueprints.local_sensor_downloads import download_zipped_logs
from http_server.flask_blueprints.atpro.atpro_generic import get_html_atpro_index

html_atpro_logs_routes = Blueprint("html_atpro_logs_routes", __name__)


@html_atpro_logs_routes.route("/atpro/sensor-logs")
def html_atpro_sensor_logs():
    return render_template("ATPro_admin/page_templates/sensor-logs.html",
                           PrimaryLogs=_get_log_view_message("Primary Log", file_locations.primary_log),
                           NetworkLogs=_get_log_view_message("Network Log", file_locations.network_log),
                           SensorsLogs=_get_log_view_message("Sensors Log", file_locations.sensors_log))


@html_atpro_logs_routes.route('/atpro/logs/log-download-all-zipped')
@auth.login_required
def atpro_get_all_logs_zipped():
    return download_zipped_logs()


@html_atpro_logs_routes.route('/atpro/delete-log/<path:url_path>')
@auth.login_required
def atpro_delete_log(url_path):
    if url_path == "primary":
        logger.network_logger.info("** Primary Sensor Log Deleted by " + str(request.remote_addr))
        logger.clear_primary_log()
    elif url_path == "network":
        logger.network_logger.info("** Network Sensor Log Deleted by " + str(request.remote_addr))
        logger.clear_network_log()
    elif url_path == "sensors":
        logger.network_logger.info("** Sensors Log Deleted by " + str(request.remote_addr))
        logger.clear_sensor_log()
    return get_html_atpro_index("SelectNav('sensor-logs', skip_menu_select=true);")


def _get_log_view_message(log_name, log_location):
    log_lines = _get_sensor_log_lines(log_location)
    log_lines_length = len(log_lines)

    if log_lines_length:
        if logger.max_log_lines_return > log_lines_length:
            text_log_entries_return = str(log_lines_length) + "/" + str(log_lines_length)
        else:
            text_log_entries_return = str(logger.max_log_lines_return) + "/" + str(log_lines_length)
    else:
        text_log_entries_return = "0/0"

    if log_lines_length > logger.max_log_lines_return:
        log_lines = log_lines[-logger.max_log_lines_return:]
    log_lines.reverse()

    return_log = "<h2>" + log_name + " - " + text_log_entries_return + "</h2>\n\n" + "<div class='log-page-view'>"
    for log in log_lines:
        return_log += log
    return return_log + "</div>"


def _get_sensor_log_lines(log_file):
    """ Opens provided log file location and returns its content as a list of lines. """
    try:
        with open(log_file, "r") as log_content:
            return log_content.readlines()
    except FileNotFoundError:
        return ["Log not found: " + log_file]
