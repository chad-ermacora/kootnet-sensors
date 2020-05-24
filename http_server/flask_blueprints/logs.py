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
from flask import Blueprint, render_template, request, send_file
from operations_modules import logger
from operations_modules import file_locations
from operations_modules import app_generic_functions
from operations_modules import app_cached_variables
from http_server.server_http_auth import auth
from http_server import server_http_generic_functions

html_logs_routes = Blueprint("html_logs_routes", __name__)


@html_logs_routes.route("/GetLogsHTML")
def html_get_log_view():
    logger.network_logger.debug("** HTML Logs accessed from " + str(request.remote_addr))
    primary_log_lines = logger.get_number_of_log_entries(file_locations.primary_log)
    network_log_lines = logger.get_number_of_log_entries(file_locations.network_log)
    sensors_log_lines = logger.get_number_of_log_entries(file_locations.sensors_log)
    return render_template("log_view.html",
                           LogURL="/GetLogsHTML",
                           PrimaryLog=logger.get_sensor_log(file_locations.primary_log),
                           PrimaryLogLinesText=_get_log_view_message(primary_log_lines),
                           NetworkLog=logger.get_sensor_log(file_locations.network_log),
                           NetworkLogLinesText=_get_log_view_message(network_log_lines),
                           SensorsLog=logger.get_sensor_log(file_locations.sensors_log),
                           SensorsLogLinesText=_get_log_view_message(sensors_log_lines))


def _get_log_view_message(log_lines_length):
    if log_lines_length:
        if logger.max_log_lines_return > log_lines_length:
            text_log_entries_return = str(log_lines_length) + "/" + str(log_lines_length)
        else:
            text_log_entries_return = str(logger.max_log_lines_return) + "/" + str(log_lines_length)
    else:
        text_log_entries_return = "0/0"
    return text_log_entries_return


@html_logs_routes.route("/GetZippedLogsSize")
def get_zipped_logs_size():
    logger.network_logger.debug("* Zipped Logs Size Sent to " + str(request.remote_addr))
    try:
        primary_log = app_generic_functions.get_file_content(file_locations.primary_log)
        network_log = app_generic_functions.get_file_content(file_locations.network_log)
        sensors_log = app_generic_functions.get_file_content(file_locations.sensors_log)
        zip_file = app_generic_functions.zip_files([os.path.basename(file_locations.primary_log),
                                                    os.path.basename(file_locations.network_log),
                                                    os.path.basename(file_locations.sensors_log)],
                                                   [primary_log, network_log, sensors_log])
        zip_size = round(app_generic_functions.get_zip_size(zip_file) / 1000, 1)
        return str(zip_size)
    except Exception as error:
        message = "* Unable to Send Zipped Logs Size to " + str(request.remote_addr) + ": " + str(error)
        logger.primary_logger.error(message)
        return "Error"


def _get_zipped_logs():
    try:
        primary_log = app_generic_functions.get_file_content(file_locations.primary_log)
        network_log = app_generic_functions.get_file_content(file_locations.network_log)
        sensors_log = app_generic_functions.get_file_content(file_locations.sensors_log)
        return app_generic_functions.zip_files([os.path.basename(file_locations.primary_log),
                                                os.path.basename(file_locations.network_log),
                                                os.path.basename(file_locations.sensors_log)],
                                               [primary_log, network_log, sensors_log])
    except Exception as error:
        logger.primary_logger.error("* Unable to Zip Logs: " + str(error))
        return None


@html_logs_routes.route("/DownloadZippedLogs")
def download_zipped_logs():
    logger.network_logger.debug("* Download Zip of all Logs Accessed by " + str(request.remote_addr))
    zip_name = "Logs_" + app_cached_variables.ip.split(".")[-1] + app_cached_variables.hostname + ".zip"
    return_zip_file = _get_zipped_logs()
    if return_zip_file is not None:
        return send_file(return_zip_file, as_attachment=True, attachment_filename=zip_name)
    return server_http_generic_functions.message_and_return("Unable to zip logs for Download", url="/GetLogsHTML")


@html_logs_routes.route("/GetPrimaryLog")
def get_raw_primary_log():
    logger.network_logger.debug("* Raw Primary Log Sent to " + str(request.remote_addr))
    return logger.get_sensor_log(file_locations.primary_log)


@html_logs_routes.route("/GetNetworkLog")
def get_raw_network_log():
    logger.network_logger.debug("* Raw Network Log Sent to " + str(request.remote_addr))
    return logger.get_sensor_log(file_locations.network_log)


@html_logs_routes.route("/GetSensorsLog")
def get_raw_sensors_log():
    logger.network_logger.debug("* Raw Sensors Log Sent to " + str(request.remote_addr))
    return logger.get_sensor_log(file_locations.sensors_log)


@html_logs_routes.route("/DeletePrimaryLog")
@auth.login_required
def delete_primary_log():
    logger.network_logger.info("** Primary Sensor Log Deleted by " + str(request.remote_addr))
    logger.clear_primary_log()
    return html_get_log_view()


@html_logs_routes.route("/DeleteNetworkLog")
@auth.login_required
def delete_network_log():
    logger.network_logger.info("** Network Sensor Log Deleted by " + str(request.remote_addr))
    logger.clear_network_log()
    return html_get_log_view()


@html_logs_routes.route("/DeleteSensorsLog")
@auth.login_required
def delete_sensors_log():
    logger.network_logger.info("** Sensors Log Deleted by " + str(request.remote_addr))
    logger.clear_sensor_log()
    return html_get_log_view()
