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
from flask import Blueprint, request
from operations_modules import logger
from operations_modules import app_config_access
from operations_modules import app_cached_variables
from operations_modules import app_cached_variables_update
from operations_modules import software_version
from sensor_recording_modules.recording_interval import get_interval_sensor_readings
from http_server.server_http_generic_functions import message_and_return
from http_server.server_http_auth import auth
from sensor_modules import sensor_access

html_legacy_cc_routes = Blueprint("html_legacy_cc_routes", __name__)


@html_legacy_cc_routes.route("/GetSensorReadings")
def cc_get_sensor_readings():
    logger.network_logger.debug("* CC Sensor Readings sent to " + str(request.remote_addr))
    interval_readings = get_interval_sensor_readings().split(app_cached_variables.command_data_separator)
    str_interval_types = interval_readings[0].split(",")
    str_interval_types_data = interval_readings[1].split(",")

    return_data = ""
    return_types = ""
    for interval_type, interval_data in zip(str_interval_types, str_interval_types_data):
        return_types += "<th><span style='background-color: #00ffff;'>" + interval_type + "</span></th>"
        return_data += "<th><span style='background-color: #0BB10D;'>" + interval_data + "</span></th>"
    return return_types + "," + return_data


@html_legacy_cc_routes.route("/GetSystemData")
def cc_get_system_data():
    logger.network_logger.debug("* CC Sensor System Data Sent to " + str(request.remote_addr))
    return app_cached_variables.hostname + ",<a href='https://" + app_cached_variables.ip + \
           ":10065/Quick' target='_blank'>" + app_cached_variables.ip + "</a>" + \
           "," + str(sensor_access.get_system_datetime()) + \
           "," + str(sensor_access.get_uptime_minutes()) + \
           "," + str(software_version.version) + \
           "," + str(round(float(sensor_access.get_cpu_temperature()), 2)) + \
           "," + str(sensor_access.get_disk_usage_gb()) + \
           "," + str(sensor_access.get_db_size()) + \
           "," + str(sensor_access.get_last_updated())


@html_legacy_cc_routes.route("/SetHostName", methods=["PUT"])
@auth.login_required
def cc_set_hostname():
    logger.network_logger.debug("** CC Set Hostname Initiated by " + str(request.remote_addr))
    try:
        new_host = request.form.get("command_data")
        os.system("hostnamectl set-hostname " + new_host)
        message = "Hostname Changed to " + new_host
        app_cached_variables_update.update_cached_variables()
    except Exception as error:
        log_msg = "** Hostname Change Failed from " + str(request.remote_addr) + " - " + str(error)
        logger.network_logger.error(log_msg)
        message = "Failed to change Hostname"
    return message_and_return(message, url="/SensorInformation")


@html_legacy_cc_routes.route("/SetDateTime", methods=["PUT"])
@auth.login_required
def cc_set_date_time():
    logger.network_logger.debug("** CC Set DateTime Initiated by " + str(request.remote_addr))
    try:
        new_datetime = request.form.get("command_data")
        os.system("date --set " + new_datetime[:10] + " && date --set " + new_datetime[11:])
        log_msg = "** CC System DateTime Set by " + str(request.remote_addr) + " to " + new_datetime
        logger.network_logger.info(log_msg)
    except Exception as error:
        log_msg = "** DateTime Change Failed from " + str(request.remote_addr) + ": " + str(error)
        logger.network_logger.error(log_msg)


@html_legacy_cc_routes.route("/GetConfigurationReport")
def cc_get_configuration_report():
    logger.network_logger.debug("* CC Sensor Configuration Data Sent to " + str(request.remote_addr))
    config_str_csv = str(app_config_access.primary_config.enable_interval_recording) + "," + \
                     str(app_config_access.primary_config.enable_trigger_recording) + "," + \
                     str(app_config_access.primary_config.sleep_duration_interval) + "," + \
                     str(app_config_access.primary_config.enable_custom_temp) + "," + \
                     str(app_config_access.primary_config.temperature_offset)
    cvs_config_and_installed_sensors = config_str_csv + ","
    cvs_config_and_installed_sensors += app_config_access.installed_sensors.get_installed_names_str()
    return cvs_config_and_installed_sensors.strip()


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
    note_datetime = request.form.get("command_data")
    logger.network_logger.info("** CC - " + str(request.remote_addr) + " Deleted Note " + str(note_datetime))
    sensor_access.delete_db_note(note_datetime)


@html_legacy_cc_routes.route("/PutDatabaseNote", methods=["PUT"])
@auth.login_required
def cc_put_sql_note():
    new_note = request.form.get("command_data")
    sensor_access.add_note_to_database(new_note)
    logger.network_logger.info("** SQL Note Inserted by " + str(request.remote_addr))
    return "OK"


@html_legacy_cc_routes.route("/UpdateDatabaseNote", methods=["PUT"])
@auth.login_required
def cc_update_sql_note():
    datetime_entry_note_csv = request.form.get("command_data")
    sensor_access.update_note_in_database(datetime_entry_note_csv)
    logger.network_logger.debug("** Updated Note in Database from " + str(request.remote_addr))
    return "OK"
