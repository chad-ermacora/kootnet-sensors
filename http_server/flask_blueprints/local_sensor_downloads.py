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
import time
from flask import Blueprint, send_file, request
from operations_modules import logger
from operations_modules import file_locations
from operations_modules import app_cached_variables
from operations_modules import app_generic_functions
from http_server.server_http_auth import auth

html_local_download_routes = Blueprint("html_local_download_routes", __name__)


@html_local_download_routes.route("/DownloadSQLDatabase")
@auth.login_required
def download_sensors_sql_database_zipped():
    logger.network_logger.debug("* Download Zipped Main SQL Database Accessed by " + str(request.remote_addr))
    try:
        sql_filename = _add_host_and_ip_to_filename("Sensor_Database", "sqlite")
        zip_filename = _add_host_and_ip_to_filename("Sensor_Database", "zip")
        start_time = time.time()
        zip_content = app_generic_functions.get_file_content(file_locations.sensor_database, open_type="rb")
        app_generic_functions.zip_files([sql_filename], [zip_content], save_type="save_to_disk",
                                        file_location=file_locations.database_zipped)
        end_time = time.time()
        logger.network_logger.info("* Main SQL Database zipped and sent to " + str(request.remote_addr))
        logger.network_logger.info("Zip file took " + str(round(end_time - start_time, 2)) + " seconds to create")
        return send_file(file_locations.database_zipped, as_attachment=True, attachment_filename=zip_filename)
    except Exception as error:
        log_msg = "* Unable to Send Main Database to "
        logger.primary_logger.error(log_msg + str(request.remote_addr) + ": " + str(error))
        return "Error sending Database - " + str(error)


@html_local_download_routes.route("/DownloadSQLDatabaseRAW")
@auth.login_required
def download_sensors_sql_database_raw():
    logger.network_logger.debug("* Download RAW Main SQL Database Accessed by " + str(request.remote_addr))
    try:
        sql_filename = _add_host_and_ip_to_filename("Sensor_Database", "sqlite")
        return send_file(file_locations.sensor_database, as_attachment=True, attachment_filename=sql_filename)
    except Exception as error:
        log_msg = "* Unable to Send Main Database to "
        logger.primary_logger.error(log_msg + str(request.remote_addr) + ": " + str(error))
        return "Error sending Database - " + str(error)


@html_local_download_routes.route("/DownloadSQLDatabaseMQTT")
@auth.login_required
def download_mqtt_sql_database_zipped():
    logger.network_logger.debug("* Download Zipped MQTT SQL Database Accessed by " + str(request.remote_addr))
    try:
        sql_filename = _add_host_and_ip_to_filename("MQTT_Database", "sqlite")
        zip_filename = _add_host_and_ip_to_filename("MQTT_Database", "zip")
        start_time = time.time()
        zip_content = app_generic_functions.get_file_content(file_locations.mqtt_subscriber_database, open_type="rb")
        app_generic_functions.zip_files([sql_filename], [zip_content], save_type="save_to_disk",
                                        file_location=file_locations.mqtt_database_zipped)
        end_time = time.time()
        logger.network_logger.info("* MQTT SQL Database zipped and sent to " + str(request.remote_addr))
        logger.network_logger.info("Zip file took " + str(round(end_time - start_time, 2)) + " seconds to create")
        return send_file(file_locations.mqtt_database_zipped, as_attachment=True, attachment_filename=zip_filename)
    except Exception as error:
        log_msg = "* Unable to Send MQTT Database to "
        logger.primary_logger.error(log_msg + str(request.remote_addr) + ": " + str(error))
        return "Error sending Database - " + str(error)


@html_local_download_routes.route("/DownloadSQLDatabaseRAWMQTT")
@auth.login_required
def download_mqtt_sql_database_raw():
    logger.network_logger.debug("* Download RAW MQTT SQL Database Accessed by " + str(request.remote_addr))
    try:
        sql_filename = _add_host_and_ip_to_filename("MQTT_Database", "sqlite")
        return send_file(file_locations.mqtt_subscriber_database, as_attachment=True, attachment_filename=sql_filename)
    except Exception as error:
        log_msg = "* Unable to Send MQTT Database to "
        logger.primary_logger.error(log_msg + str(request.remote_addr) + ": " + str(error))
        return "Error sending Database - " + str(error)


@html_local_download_routes.route("/DownloadSQLDatabaseCheckin")
@auth.login_required
def download_checkin_sql_database_zipped():
    logger.network_logger.debug("* Download Zipped Checkin SQL Database Accessed by " + str(request.remote_addr))
    try:
        sql_filename = _add_host_and_ip_to_filename("Checkin_Database", "sqlite")
        zip_filename = _add_host_and_ip_to_filename("Checkin_Database", "zip")
        start_time = time.time()
        zip_content = app_generic_functions.get_file_content(file_locations.sensor_checkin_database, open_type="rb")
        app_generic_functions.zip_files([sql_filename], [zip_content], save_type="save_to_disk",
                                        file_location=file_locations.checkin_database_zipped)
        end_time = time.time()
        logger.network_logger.info("* Checkin SQL Database zipped and sent to " + str(request.remote_addr))
        logger.network_logger.info("Zip file took " + str(round(end_time - start_time, 2)) + " seconds to create")
        return send_file(file_locations.checkin_database_zipped, as_attachment=True, attachment_filename=zip_filename)
    except Exception as error:
        log_msg = "* Unable to Send Checkin Database to "
        logger.primary_logger.error(log_msg + str(request.remote_addr) + ": " + str(error))
        return "Error sending Database - " + str(error)


@html_local_download_routes.route("/DownloadSQLDatabaseRAWCheckin")
@auth.login_required
def download_checkin_sql_database_raw():
    logger.network_logger.debug("* Download RAW Checkin SQL Database Accessed by " + str(request.remote_addr))
    try:
        sql_filename = _add_host_and_ip_to_filename("Sensors_Checkin_Database", "sqlite")
        return send_file(file_locations.sensor_checkin_database, as_attachment=True, attachment_filename=sql_filename)
    except Exception as error:
        log_msg = "* Unable to Send Checkin Database to "
        logger.primary_logger.error(log_msg + str(request.remote_addr) + ": " + str(error))
        return "Error sending Database - " + str(error)


def _add_host_and_ip_to_filename(filename, file_extension):
    file_name_part1 = app_cached_variables.hostname + "-" + app_cached_variables.ip.split(".")[-1]
    return_filename = file_name_part1 + "_" + filename + "." + file_extension
    return return_filename


@html_local_download_routes.route("/DownloadZippedEverything")
@auth.login_required
def download_zipped_everything():
    logger.network_logger.debug("* Download Zip of Everything Accessed by " + str(request.remote_addr))
    zip_name = "Everything_" + app_cached_variables.ip.split(".")[-1] + app_cached_variables.hostname + ".zip"
    database_name = "Database_" + app_cached_variables.hostname + ".sqlite"
    try:
        return_names = [database_name,
                        os.path.basename(file_locations.primary_log),
                        os.path.basename(file_locations.network_log),
                        os.path.basename(file_locations.sensors_log)]
        return_files = [app_generic_functions.get_file_content(file_locations.sensor_database, open_type="rb"),
                        app_generic_functions.get_file_content(file_locations.primary_log),
                        app_generic_functions.get_file_content(file_locations.network_log),
                        app_generic_functions.get_file_content(file_locations.sensors_log)]

        return_zip_file = app_generic_functions.zip_files(return_names, return_files)
        return send_file(return_zip_file, attachment_filename=zip_name, as_attachment=True)
    except Exception as error:
        logger.primary_logger.error("* Unable to Zip Logs: " + str(error))
        return "Unable to zip logs for Download"


@html_local_download_routes.route("/GetSQLDBSize")
def get_main_sql_db_size():
    """ Returns main sensor database size in MB """
    logger.network_logger.debug("* Sensor's Database Size sent to " + str(request.remote_addr))
    return str(app_generic_functions.get_file_size(file_locations.sensor_database))


@html_local_download_routes.route("/GetZippedLogsSize")
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


@html_local_download_routes.route("/DownloadZippedLogs")
@auth.login_required
def download_zipped_logs():
    logger.network_logger.debug("* Download Zip of all Logs Accessed by " + str(request.remote_addr))
    zip_name = "Logs_" + app_cached_variables.ip.split(".")[-1] + app_cached_variables.hostname + ".zip"
    return_zip_file = _get_zipped_logs()
    if return_zip_file is not None:
        return send_file(return_zip_file, as_attachment=True, attachment_filename=zip_name)
    return "None"
