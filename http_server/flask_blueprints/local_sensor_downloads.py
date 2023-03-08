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
from operations_modules.app_generic_functions import get_file_size, get_zip_size, zip_files, thread_function
from operations_modules.app_generic_disk import get_file_content
from http_server.server_http_auth import auth
from http_server.flask_blueprints.atpro.atpro_generic import get_html_atpro_index

html_local_download_routes = Blueprint("html_local_download_routes", __name__)


@html_local_download_routes.route("/DownloadALLSQLDatabases")
@auth.login_required
def download_all_sql_databases_zipped():
    logger.network_logger.debug("* Download Zip of All Databases Accessed by " + str(request.remote_addr))
    zip_name = _get_net_and_host_name_str("All_Databases", ".zip")

    try:
        return_names = [app_cached_variables.hostname + "_Main_Database.sqlite",
                        app_cached_variables.hostname + "_Checkin_Database.sqlite",
                        app_cached_variables.hostname + "_MQTT_Sub_Database.sqlite"]
        return_files = [get_file_content(file_locations.sensor_database, open_type="rb"),
                        get_file_content(file_locations.sensor_checkin_database, open_type="rb"),
                        get_file_content(file_locations.mqtt_subscriber_database, open_type="rb")]
        return_zip = zip_files(return_names, return_files)
        return send_file(return_zip, download_name=zip_name, as_attachment=True)
    except Exception as error:
        logger.primary_logger.error("* Download All Databases Zip: " + str(error))
        return_zip = "Error Creating Zip on " + app_cached_variables.ip + " - " + app_cached_variables.hostname
        return send_file(return_zip + " - " + str(error), download_name=zip_name + ".txt", as_attachment=True)


@html_local_download_routes.route("/DownloadSQLDatabase")
@auth.login_required
def download_sensors_sql_database_zipped():
    _button_functions("create-main-db-zip")
    while app_cached_variables.creating_zip_main_db:
        time.sleep(1)
    return _button_functions("download-main-db-zip")

# Removed due to DB corruption on downloaded file
# @html_local_download_routes.route("/DownloadSQLDatabaseRAW")
# @auth.login_required
# def download_sensors_sql_database_raw():
#     return _button_functions("download-main-db-raw")


@html_local_download_routes.route("/DownloadSQLDatabaseMQTT")
@auth.login_required
def download_mqtt_sql_database_zipped():
    _button_functions("create-mqtt-sub-db-zip")
    while app_cached_variables.creating_zip_mqtt_sub_db:
        time.sleep(1)
    return _button_functions("download-mqtt-sub-db-zip")

# Removed due to DB corruption on downloaded file
# @html_local_download_routes.route("/DownloadSQLDatabaseRAWMQTT")
# @auth.login_required
# def download_mqtt_sql_database_raw():
#     return _button_functions("download-mqtt-sub-db-raw")


@html_local_download_routes.route("/DownloadSQLDatabaseCheckin")
@auth.login_required
def download_checkin_sql_database_zipped():
    _button_functions("create-checkin-db-zip")
    while app_cached_variables.creating_zip_checkin_db:
        time.sleep(1)
    return _button_functions("download-checkin-db-zip")

# Removed due to DB corruption on downloaded file
# @html_local_download_routes.route("/DownloadSQLDatabaseRAWCheckin")
# @auth.login_required
# def download_checkin_sql_database_raw():
#     return _button_functions("download-checkin-db-raw")


@html_local_download_routes.route("/DatabaseDownloads", methods=["GET", "POST"])
@auth.login_required
def html_atpro_db_downloads():
    if request.method == "POST":
        request_ip = str(request.remote_addr)
        button_pressed = str(request.form.get("button-function"))
        return _button_functions(button_pressed, request_ip)
    return get_html_atpro_index(run_script="SelectNav('sensor-system', skip_menu_select=true);")


def _button_functions(button_pressed, request_ip="N/A"):
    try:
        # Removed due to DB corruption on downloaded file
        # if button_pressed == "download-main-db-raw":
        #     logger.network_logger.debug("* Download RAW Main SQL Database Accessed by " + request_ip)
        #     sensor_database = file_locations.sensor_database
        #     if os.path.isfile(sensor_database):
        #         sql_filename = _add_host_and_ip_to_filename("Sensor_Database", "sqlite")
        #         return send_file(sensor_database, as_attachment=True, download_name=sql_filename)
        #     return "Kootnet Sensors main database not found"
        #
        # elif button_pressed == "download-mqtt-sub-db-raw":
        #     logger.network_logger.debug("* Download RAW MQTT SQL Database Accessed by " + str(request.remote_addr))
        #     mqtt_subscriber_database = file_locations.mqtt_subscriber_database
        #     if os.path.isfile(mqtt_subscriber_database):
        #         sql_filename = _add_host_and_ip_to_filename("MQTT_Database", "sqlite")
        #         return send_file(mqtt_subscriber_database, as_attachment=True, download_name=sql_filename)
        #     return "Kootnet Sensors MQTT Subscriber database not found"
        #
        # elif button_pressed == "download-checkin-db-raw":
        #     logger.network_logger.debug("* Download RAW Checkin SQL Database Accessed by " + str(request_ip))
        #     sensor_checkin_database = file_locations.sensor_checkin_database
        #     if os.path.isfile(sensor_checkin_database):
        #         sql_filename = _add_host_and_ip_to_filename("Sensors_Checkin_Database", "sqlite")
        #         return send_file(sensor_checkin_database, as_attachment=True, download_name=sql_filename)
        #     return "Kootnet Sensors Checkin database not found"

        if button_pressed == "download-main-db-zip":
            if not app_cached_variables.creating_zip_main_db:
                database_zipped = file_locations.database_zipped
                if os.path.isfile(database_zipped):
                    zip_filename = _add_host_and_ip_to_filename("Main_Database", "zip")
                    logger.network_logger.debug("* Download Zipped Main SQL Database Accessed by " + request_ip)
                    return send_file(database_zipped, as_attachment=True, download_name=zip_filename)
                return "Zipped Main SQL database not found, 'Generate New Zip' before trying again."
            else:
                return "Creating database zip, please try again later ..."

        elif button_pressed == "download-mqtt-sub-db-zip":
            if not app_cached_variables.creating_zip_mqtt_sub_db:
                mqtt_database_zipped = file_locations.mqtt_database_zipped
                if os.path.isfile(mqtt_database_zipped):
                    zip_filename = _add_host_and_ip_to_filename("MQTT_Subscriber_Database", "zip")
                    log_msg = "* Download Zipped MQTT Subscriber SQL Database Accessed by "
                    logger.network_logger.debug(log_msg + request_ip)
                    return send_file(mqtt_database_zipped, as_attachment=True, download_name=zip_filename)
                return "Zipped MQTT Subscriber SQL database not found, 'Generate New Zip' before trying again."
            else:
                return "Creating database zip, please try again later ..."

        elif button_pressed == "download-checkin-db-zip":
            if not app_cached_variables.creating_zip_checkin_db:
                checkin_database_zipped = file_locations.checkin_database_zipped
                if os.path.isfile(checkin_database_zipped):
                    zip_filename = _add_host_and_ip_to_filename("Checkin_Database", "zip")
                    logger.network_logger.debug("* Download Zipped Checkin SQL Database Accessed by " + request_ip)
                    return send_file(checkin_database_zipped, as_attachment=True, download_name=zip_filename)
                return "Zipped Sensor Checkin SQL database not found, 'Generate New Zip' before trying again."
            else:
                return "Creating database zip, please try again later ..."

        elif button_pressed == "create-main-db-zip":
            if not app_cached_variables.creating_zip_main_db:
                app_cached_variables.creating_zip_main_db = True
                thread_function(_zip_main_db_worker)

        elif button_pressed == "create-mqtt-sub-db-zip":
            if not app_cached_variables.creating_zip_mqtt_sub_db:
                app_cached_variables.creating_zip_mqtt_sub_db = True
                thread_function(_zip_mqtt_sub_db_worker)

        elif button_pressed == "create-checkin-db-zip":
            if not app_cached_variables.creating_zip_checkin_db:
                app_cached_variables.creating_zip_checkin_db = True
                thread_function(_zip_checkin_db_worker)
    except Exception as error:
        log_msg = "HTML Database Request Error from " + request_ip + " using command " + button_pressed + ": "
        logger.primary_logger.error(log_msg + str(error))
    return get_html_atpro_index(run_script="SelectNav('sensor-system', skip_menu_select=true);")


def _add_host_and_ip_to_filename(filename, file_extension):
    try:
        file_name_part1 = app_cached_variables.hostname + "-" + app_cached_variables.ip.split(".")[-1]
        return_filename = file_name_part1 + "_" + filename + "." + file_extension
    except Exception as error:
        logger.network_logger.error("Error adding hostname & IP to filename" + str(error))
        return_filename = f"{filename}.{file_extension}"
    return return_filename


def _zip_main_db_worker():
    sql_filename = _add_host_and_ip_to_filename("Main_Database", "sqlite")
    zip_content = get_file_content(file_locations.sensor_database, open_type="rb")
    _zip_db(file_locations.database_zipped, sql_filename, zip_content)
    app_cached_variables.creating_zip_main_db = False


def _zip_mqtt_sub_db_worker():
    sql_filename = _add_host_and_ip_to_filename("MQTT_Subscriber_Database", "sqlite")
    zip_content = get_file_content(file_locations.mqtt_subscriber_database, open_type="rb")
    _zip_db(file_locations.mqtt_database_zipped, sql_filename, zip_content)
    app_cached_variables.creating_zip_mqtt_sub_db = False


def _zip_checkin_db_worker():
    sql_filename = _add_host_and_ip_to_filename("Checkin_Database", "sqlite")
    zip_content = get_file_content(file_locations.sensor_checkin_database, open_type="rb")
    _zip_db(file_locations.checkin_database_zipped, sql_filename, zip_content)
    app_cached_variables.creating_zip_checkin_db = False


def _zip_db(zip_location, sql_filename, zip_content):
    try:
        start_time = time.time()
        zip_files([sql_filename], [zip_content], save_type="save_to_disk", file_location=zip_location)
        end_time = time.time()
        total_zip_time = str(round(end_time - start_time, 2))
        logger.network_logger.info("Zipping " + sql_filename + " took " + total_zip_time + " seconds")
    except Exception as error:
        logger.primary_logger.error("* Unable to create Database zip of " + sql_filename + ": " + str(error))


@html_local_download_routes.route("/DownloadZippedEverything")
@auth.login_required
def download_zipped_everything():
    logger.network_logger.debug("* Download Zip of Everything Accessed by " + str(request.remote_addr))
    zip_name = _get_net_and_host_name_str("Everything", ".zip")

    try:
        zipped_logs = _get_zipped_logs()
        return_names = [app_cached_variables.hostname + "_Main_Database.sqlite",
                        app_cached_variables.hostname + "_Checkin_Database.sqlite",
                        app_cached_variables.hostname + "_MQTT_Sub_Database.sqlite",
                        app_cached_variables.hostname + "_Logs.zip"]
        return_files = [get_file_content(file_locations.sensor_database, open_type="rb"),
                        get_file_content(file_locations.sensor_checkin_database, open_type="rb"),
                        get_file_content(file_locations.mqtt_subscriber_database, open_type="rb"),
                        zipped_logs.read()]
        return send_file(zip_files(return_names, return_files), download_name=zip_name, as_attachment=True)
    except Exception as error:
        logger.primary_logger.error("* Download Everything Zip: " + str(error))
        return_zip = "Error Creating Zip on " + app_cached_variables.ip + " - " + app_cached_variables.hostname
        return send_file(return_zip + " - " + str(error), download_name=zip_name + ".txt", as_attachment=True)


@html_local_download_routes.route("/GetSQLDBSize")
def get_main_sql_db_size():
    """ Returns main sensor database size in MB """
    logger.network_logger.debug("* Sensor's Database Size sent to " + str(request.remote_addr))
    return str(get_file_size(file_locations.sensor_database))


@html_local_download_routes.route("/GetZippedLogsSize")
def get_zipped_logs_size():
    logger.network_logger.debug("* Zipped Logs Size Sent to " + str(request.remote_addr))
    zipped_logs = _get_zipped_logs()
    if zipped_logs is not None:
        return str(round(get_zip_size(zipped_logs) / 1000, 1))
    return "0.0"


def _get_zipped_logs():
    try:
        return_names = [app_cached_variables.hostname + "_" + os.path.basename(file_locations.primary_log),
                        app_cached_variables.hostname + "_" + os.path.basename(file_locations.network_log),
                        app_cached_variables.hostname + "_" + os.path.basename(file_locations.sensors_log)]
        return_files = [get_file_content(file_locations.primary_log, open_type="rb"),
                        get_file_content(file_locations.network_log, open_type="rb"),
                        get_file_content(file_locations.sensors_log, open_type="rb")]
        return zip_files(return_names, return_files)
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
        return send_file(return_zip_file, as_attachment=True, download_name=zip_name)
    return "None"


def _get_net_and_host_name_str(beginning, end_extension):
    if len(app_cached_variables.ip.split(".")) > 1:
        return_name = beginning + "_" + app_cached_variables.ip.split(".")[-1]
        return_name += "_" + app_cached_variables.hostname + "_" + end_extension
        return return_name
    return beginning + "_" + "NA_" + app_cached_variables.hostname + "_" + end_extension
