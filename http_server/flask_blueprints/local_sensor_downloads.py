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
from http_server import server_http_generic_functions

html_local_download_routes = Blueprint("html_local_download_routes", __name__)


@html_local_download_routes.route("/DownloadSQLDatabase")
def download_sensors_sql_database_zipped():
    logger.network_logger.debug("* Download Zipped SQL Database Accessed by " + str(request.remote_addr))
    try:
        file_name_part1 = app_cached_variables.ip.split(".")[-1] + app_cached_variables.hostname
        sql_filename = file_name_part1 + "SensorDatabase.sqlite"
        zip_filename = file_name_part1 + "SensorDatabase.zip"
        start_time = time.time()
        zip_content = app_generic_functions.get_file_content(file_locations.sensor_database, open_type="rb")
        app_generic_functions.zip_files([sql_filename], [zip_content], save_type="save_to_disk",
                                        file_location=file_locations.database_zipped)
        end_time = time.time()
        logger.network_logger.info("* SQL Database zipped and sent to " + str(request.remote_addr))
        logger.network_logger.info("Zip file took " + str(round(end_time - start_time, 2)) + " seconds to create")
        return send_file(file_locations.database_zipped, as_attachment=True, attachment_filename=zip_filename)
    except Exception as error:
        logger.primary_logger.error("* Unable to Send Database to " + str(request.remote_addr) + ": " + str(error))
        return server_http_generic_functions.message_and_return("Error sending Database - " + str(error))


@html_local_download_routes.route("/DownloadSQLDatabaseRAW")
def download_sensors_sql_database_raw():
    logger.network_logger.debug("* Download RAW SQL Database Accessed by " + str(request.remote_addr))
    try:
        file_name_part1 = app_cached_variables.ip.split(".")[-1] + "-" + app_cached_variables.hostname
        sql_filename = file_name_part1 + "SensorDatabase.sqlite"
        return send_file(file_locations.sensor_database, as_attachment=True, attachment_filename=sql_filename)
    except Exception as error:
        logger.primary_logger.error("* Unable to Send Database to " + str(request.remote_addr) + ": " + str(error))
        return server_http_generic_functions.message_and_return("Error sending Database - " + str(error))


@html_local_download_routes.route("/DownloadZippedEverything")
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
        return server_http_generic_functions.message_and_return("Unable to zip logs for Download", url="/GetLogsHTML")
