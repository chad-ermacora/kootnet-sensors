import os
from flask import Blueprint, request
from operations_modules import logger
from operations_modules import app_cached_variables_update
from http_server.server_http_generic_functions import message_and_return
from http_server.server_http_auth import auth
from sensor_modules import sensor_access

html_legacy_cc_routes = Blueprint("html_legacy_cc_routes", __name__)


@html_legacy_cc_routes.route("/GetSensorReadings")
def cc_get_sensor_readings():
    logger.network_logger.debug("* CC Sensor Readings sent to " + str(request.remote_addr))
    sensor_readings = sensor_access.get_sensor_readings()
    return_str = str(sensor_readings[0]) + "," + str(sensor_readings[1])
    return return_str


@html_legacy_cc_routes.route("/GetSystemData")
def cc_get_system_data():
    logger.network_logger.debug("* CC Sensor System Data Sent to " + str(request.remote_addr))
    return sensor_access.get_system_information()


@html_legacy_cc_routes.route("/SetHostName", methods=["PUT"])
@auth.login_required
def cc_set_hostname():
    logger.network_logger.debug("** CC Set Hostname Initiated by " + str(request.remote_addr))
    try:
        new_host = request.form['command_data']
        os.system("hostnamectl set-hostname " + new_host)
        message = "Hostname Changed to " + new_host
        app_cached_variables_update.update_cached_variables()
    except Exception as error:
        logger.network_logger.error(
            "** Hostname Change Failed from " + str(request.remote_addr) + " - " + str(error))
        message = "Failed to change Hostname"
    return message_and_return(message, url="/SensorInformation")


@html_legacy_cc_routes.route("/SetDateTime", methods=["PUT"])
@auth.login_required
def cc_set_date_time():
    logger.network_logger.debug("** CC Set DateTime Initiated by " + str(request.remote_addr))
    try:
        new_datetime = request.form['command_data']
        os.system("date --set " + new_datetime[:10] + " && date --set " + new_datetime[11:])
        logger.network_logger.info(
            "** CC System DateTime Set by " + str(request.remote_addr) + " to " + new_datetime)
    except Exception as error:
        logger.network_logger.error(
            "** DateTime Change Failed from " + str(request.remote_addr) + ": " + str(error))


@html_legacy_cc_routes.route("/GetConfigurationReport")
def cc_get_configuration_report():
    logger.network_logger.debug("* CC Sensor Configuration Data Sent to " + str(request.remote_addr))
    return sensor_access.get_config_information()


@html_legacy_cc_routes.route("/GetDatabaseNotes")
def cc_get_db_notes():
    logger.network_logger.debug("* CC Sensor Notes Sent to " + str(request.remote_addr))
    return sensor_access.get_db_notes()


@html_legacy_cc_routes.route("/GetDatabaseNoteDates")
def cc_get_db_note_dates():
    logger.network_logger.debug("* CC Sensor Note Dates Sent to " + str(request.remote_addr))
    return sensor_access.get_db_note_dates()


@html_legacy_cc_routes.route("/GetDatabaseNoteUserDates")
def cc_get_db_note_user_dates():
    logger.network_logger.debug("* CC User Set Sensor Notes Dates Sent to " + str(request.remote_addr))
    return sensor_access.get_db_note_user_dates()


@html_legacy_cc_routes.route("/DeleteDatabaseNote", methods=["PUT"])
@auth.login_required
def cc_del_db_note():
    logger.network_logger.debug("* CC Delete Sensor Note Accessed by " + str(request.remote_addr))
    note_datetime = request.form['command_data']
    logger.network_logger.info("** CC - " + str(request.remote_addr) + " Deleted Note " + str(note_datetime))
    sensor_access.delete_db_note(note_datetime)


@html_legacy_cc_routes.route("/PutDatabaseNote", methods=["PUT"])
@auth.login_required
def cc_put_sql_note():
    new_note = request.form['command_data']
    sensor_access.add_note_to_database(new_note)
    logger.network_logger.info("** SQL Note Inserted by " + str(request.remote_addr))
    return "OK"


@html_legacy_cc_routes.route("/UpdateDatabaseNote", methods=["PUT"])
@auth.login_required
def cc_update_sql_note():
    datetime_entry_note_csv = request.form['command_data']
    sensor_access.update_note_in_database(datetime_entry_note_csv)
    logger.network_logger.debug("** Updated Note in Database from " + str(request.remote_addr))
    return "OK"
