import os
from flask import Blueprint, send_file, request
from operations_modules import logger
from operations_modules import file_locations
from operations_modules import app_cached_variables
from operations_modules import app_generic_functions
from operations_modules import app_config_access
from http_server import server_http_generic_functions

html_download_routes = Blueprint("html_downloads", __name__)


@html_download_routes.route("/DownloadSQLDatabase")
def download_sensors_sql_database_zipped():
    logger.network_logger.debug("* Download SQL Database Accessed by " + str(request.remote_addr))
    try:
        file_name_part1 = app_cached_variables.ip.split(".")[-1] + app_cached_variables.hostname
        sql_filename = file_name_part1 + "SensorDatabase.sqlite"
        zip_filename = file_name_part1 + "SensorDatabase.zip"

        zip_content = app_generic_functions.get_file_content(file_locations.sensor_database, open_type="rb")
        app_generic_functions.zip_files([sql_filename], [zip_content], save_type="save_to_disk",
                                        file_location=file_locations.database_zipped)

        logger.network_logger.info("* Sensor SQL Database Sent to " + str(request.remote_addr))
        return send_file(file_locations.database_zipped, as_attachment=True,
                         attachment_filename=zip_filename)
    except Exception as error:
        logger.primary_logger.error("* Unable to Send Database to " + str(request.remote_addr) + ": " + str(error))
        return server_http_generic_functions.message_and_return("Error sending Database - " + str(error))


@html_download_routes.route("/DownloadZippedLogs")
def download_zipped_logs():
    logger.network_logger.debug("* Download Zip of all Logs Accessed by " + str(request.remote_addr))
    zip_name = "Logs_" + app_cached_variables.ip.split(".")[-1] + app_cached_variables.hostname + ".zip"
    try:
        primary_log = app_generic_functions.get_file_content(file_locations.primary_log)
        network_log = app_generic_functions.get_file_content(file_locations.network_log)
        sensors_log = app_generic_functions.get_file_content(file_locations.sensors_log)

        return_zip_file = app_generic_functions.zip_files([os.path.basename(file_locations.primary_log),
                                                           os.path.basename(file_locations.network_log),
                                                           os.path.basename(file_locations.sensors_log)],
                                                          [primary_log, network_log, sensors_log])

        return send_file(return_zip_file, as_attachment=True, attachment_filename=zip_name)
    except Exception as error:
        logger.primary_logger.error("* Unable to Zip Logs: " + str(error))
        return server_http_generic_functions.message_and_return("Unable to zip logs for Download", url="/GetLogsHTML")


@html_download_routes.route("/DownloadZippedEverything")
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


@html_download_routes.route("/DownloadSCDatabasesZip")
def download_sc_databases_zip():
    logger.network_logger.debug("* Download Zip of Multiple Sensor DBs Accessed by " + str(request.remote_addr))
    if not app_config_access.creating_databases_zip:
        if app_cached_variables.sc_databases_zip_name != "":
            try:
                if app_cached_variables.sc_databases_zip_in_memory:
                    zip_file = app_cached_variables.sc_in_memory_zip
                else:
                    zip_file = file_locations.html_sensor_control_databases_zip

                zip_filename = app_cached_variables.sc_databases_zip_name
                app_cached_variables.sc_databases_zip_name = ""
                app_cached_variables.sc_databases_zip_in_memory = False
                return send_file(zip_file, attachment_filename=zip_filename, as_attachment=True)
            except Exception as error:
                logger.network_logger.error("Send Databases Zip Error: " + str(error))
                app_cached_variables.sc_databases_zip_name = ""
                app_cached_variables.sc_databases_zip_in_memory = False
                return server_http_generic_functions.message_and_return("Problem loading Zip",
                                                                        url="/SensorControlManage")
    else:
        return server_http_generic_functions.message_and_return("Zipped Databases Creation in Progress",
                                                                url="/SensorControlManage")


@html_download_routes.route("/DownloadSCReportsZip")
def download_sc_reports_zip():
    logger.network_logger.debug("* Download SC Reports Zipped Accessed by " + str(request.remote_addr))
    try:
        if not app_config_access.creating_the_reports_zip:
            if app_cached_variables.sc_reports_zip_name != "":
                zip_file = app_cached_variables.sc_in_memory_zip
                zip_filename = app_cached_variables.sc_reports_zip_name
                app_cached_variables.sc_reports_zip_name = ""
                return send_file(zip_file, attachment_filename=zip_filename, as_attachment=True)
        else:
            return server_http_generic_functions.message_and_return("Zipped Reports Creation in Progress",
                                                                    url="/SensorControlManage")
    except Exception as error:
        logger.network_logger.error("Send Reports Zip Error: " + str(error))

    app_cached_variables.sc_reports_zip_name = ""
    return server_http_generic_functions.message_and_return("Problem loading Zip", url="/SensorControlManage")


@html_download_routes.route("/DownloadSCLogsZip")
def download_sc_logs_zip():
    logger.network_logger.debug("* Download SC Logs Zipped Accessed by " + str(request.remote_addr))
    try:
        if not app_config_access.creating_logs_zip:
            if app_cached_variables.sc_logs_zip_name != "":
                zip_file = app_cached_variables.sc_in_memory_zip
                zip_filename = app_cached_variables.sc_logs_zip_name
                app_cached_variables.sc_logs_zip_name = ""
                return send_file(zip_file, attachment_filename=zip_filename, as_attachment=True)
        else:
            return server_http_generic_functions.message_and_return("Zipped Multiple Sensors Logs Creation in Progress",
                                                                    url="/SensorControlManage")
    except Exception as error:
        logger.network_logger.error("Send SC Logs Zip Error: " + str(error))

    app_cached_variables.sc_logs_zip_name = ""
    return server_http_generic_functions.message_and_return("Problem loading Zip", url="/SensorControlManage")


@html_download_routes.route("/DownloadSCBigZip")
def download_sc_big_zip():
    logger.network_logger.debug("* Download 'The Big Zip' Accessed by " + str(request.remote_addr))
    try:
        if not app_config_access.creating_the_big_zip:
            if app_cached_variables.sc_big_zip_name != "":
                if app_cached_variables.sc_big_zip_in_memory:
                    zip_file = app_cached_variables.sc_in_memory_zip
                else:
                    zip_file = file_locations.html_sensor_control_big_zip

                zip_filename = app_cached_variables.sc_big_zip_name
                app_cached_variables.sc_big_zip_name = ""
                app_cached_variables.sc_big_zip_in_memory = False
                return send_file(zip_file, attachment_filename=zip_filename, as_attachment=True)
        else:
            return server_http_generic_functions.message_and_return("Big Zip Creation in Progress",
                                                                    url="/SensorControlManage")
    except Exception as error:
        logger.network_logger.error("Send Big Zip Error: " + str(error))
    app_cached_variables.sc_big_zip_in_memory = False
    return server_http_generic_functions.message_and_return("Problem loading Zip", url="/SensorControlManage")


@html_download_routes.route("/GetZippedSQLDatabaseSize")
def get_zipped_sql_database_size():
    logger.network_logger.debug("* Zipped SQL Database Size Sent to " + str(request.remote_addr))
    try:
        if not os.path.isfile(file_locations.database_zipped):
            database_name = app_cached_variables.hostname + "SensorDatabase.sqlite"
            sql_database = app_generic_functions.get_file_content(file_locations.sensor_database, open_type="rb")
            app_generic_functions.zip_files([database_name], [sql_database], save_type="save_to_disk",
                                            file_location=file_locations.database_zipped)
        sql_database_size = os.path.getsize(file_locations.database_zipped)
        return str(sql_database_size)
    except Exception as error:
        logger.primary_logger.error(
            "* Unable to Send Database Size to " + str(request.remote_addr) + ": " + str(error))
        return "Error"
