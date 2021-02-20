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
import sqlite3
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request
from operations_modules import logger
from operations_modules import file_locations
from operations_modules import app_cached_variables
from configuration_modules import app_config_access
from operations_modules.sqlite_database import create_table_and_datetime, check_sql_table_and_column, \
    sql_execute_get_data, write_to_sql_database, get_clean_sql_table_name
from http_server.server_http_auth import auth
from http_server.server_http_generic_functions import get_html_hidden_state, get_html_checkbox_state

html_sensor_check_ins_routes = Blueprint("html_sensor_check_ins_routes", __name__)
max_sensors_in_main_checkin_view = 20

db_all_tables_datetime = app_cached_variables.database_variables.all_tables_datetime
db_sensor_check_in_version = app_cached_variables.database_variables.sensor_check_in_version
db_sensor_check_in_installed_sensors = app_cached_variables.database_variables.sensor_check_in_installed_sensors
db_sensor_check_in_primary_log = app_cached_variables.database_variables.sensor_check_in_primary_log
db_sensor_check_in_sensors_log = app_cached_variables.database_variables.sensor_check_in_sensors_log
db_sensor_uptime = app_cached_variables.database_variables.sensor_uptime


@html_sensor_check_ins_routes.route("/SensorCheckin", methods=["POST"])
def remote_sensor_check_ins():
    if app_config_access.checkin_config.enable_checkin_recording:
        if request.form.get("checkin_id"):
            checkin_id = get_clean_sql_table_name(str(request.form.get("checkin_id")))
            logger.network_logger.debug("* Sensor ID:" + checkin_id + " checked in from " + str(request.remote_addr))

            current_datetime = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

            try:
                db_connection = sqlite3.connect(file_locations.sensor_checkin_database)
                db_cursor = db_connection.cursor()

                create_table_and_datetime(checkin_id, db_cursor)
                check_sql_table_and_column(checkin_id, db_sensor_check_in_version, db_cursor)
                check_sql_table_and_column(checkin_id, db_sensor_check_in_installed_sensors, db_cursor)
                check_sql_table_and_column(checkin_id, db_sensor_uptime, db_cursor)
                check_sql_table_and_column(checkin_id, db_sensor_check_in_primary_log, db_cursor)
                check_sql_table_and_column(checkin_id, db_sensor_check_in_sensors_log, db_cursor)
                db_connection.commit()
                db_connection.close()

                sql_ex_string = "INSERT OR IGNORE INTO '" + checkin_id + "' (" + \
                                db_all_tables_datetime + "," + \
                                db_sensor_check_in_version + "," + \
                                db_sensor_check_in_installed_sensors + "," + \
                                db_sensor_uptime + "," + \
                                db_sensor_check_in_primary_log + "," + \
                                db_sensor_check_in_sensors_log + ")" + \
                                " VALUES (?,?,?,?,?,?);"

                sql_data = [current_datetime, str(request.form.get("program_version")),
                            str(request.form.get("installed_sensors")), str(request.form.get("sensor_uptime")),
                            str(request.form.get("primary_log")), str(request.form.get("sensor_log"))]
                write_to_sql_database(sql_ex_string, sql_data, sql_database_location=file_locations.sensor_checkin_database)
                return "OK", 202
            except Exception as error:
                logger.network_logger.warning("Sensor Checkin error for " + str(checkin_id) + ": " + str(error))
        return "Failed", 400
    return "Checkin Recording Disabled", 202


@html_sensor_check_ins_routes.route("/ViewSensorCheckin")
@auth.login_required
def view_sensor_check_ins():
    db_location = file_locations.sensor_checkin_database
    get_sensor_checkin_count_sql = "SELECT count(*) FROM sqlite_master WHERE type = 'table'" + \
                                   "AND name != 'android_metadata' AND name != 'sqlite_sequence';"
    sensor_count = sql_execute_get_data(get_sensor_checkin_count_sql, sql_database_location=db_location)
    sensor_ids_and_date_list = _get_sensor_id_and_last_checkin_date_as_list()

    sensor_statistics = "Per Sensor Check-in Information\n\n"
    current_date_time = datetime.utcnow()

    sensor_contact_count = 0
    count_contact_days = app_config_access.checkin_config.count_contact_days
    for count, sensor_id_and_date in enumerate(sensor_ids_and_date_list):
        cleaned_id = sensor_id_and_date[0]
        checkin_date = sensor_id_and_date[1]
        if (current_date_time - checkin_date) < timedelta(days=count_contact_days):
            sensor_contact_count += 1
        if count < max_sensors_in_main_checkin_view:
            sensor_statistics += _get_sensor_info_string(cleaned_id)

    if os.path.isfile(file_locations.sensor_checkin_database):
        db_size_mb = round(os.path.getsize(file_locations.sensor_checkin_database) / 1000000, 3)
    else:
        db_size_mb = 0.0

    enable_checkin_recording = app_config_access.checkin_config.enable_checkin_recording
    return render_template("software_checkin.html",
                           PageURL="/ViewSensorCheckin",
                           RestartServiceHidden=get_html_hidden_state(app_cached_variables.html_service_restart),
                           RebootSensorHidden=get_html_hidden_state(app_cached_variables.html_sensor_reboot),
                           SensorsInDatabase=_get_sql_element(sensor_count),
                           TotalSensorCount=sensor_contact_count,
                           CheckinSensorStatistics=sensor_statistics,
                           CheckedEnableCheckin=get_html_checkbox_state(enable_checkin_recording),
                           ContactInPastDays=app_config_access.checkin_config.count_contact_days,
                           CheckinDBSize=db_size_mb,
                           DeleteSensorsOlderDays=app_config_access.checkin_config.delete_sensors_older_days)


@html_sensor_check_ins_routes.route("/DeleteSensorsOlderCheckin", methods=["POST"])
@auth.login_required
def delete_sensors_older_then():
    try:
        app_config_access.checkin_config.update_with_html_request(request, skip_all_but_delete_setting=True)
        app_config_access.checkin_config.save_config_to_file()
        delete_sensors_older_days = app_config_access.checkin_config.delete_sensors_older_days
        datetime_sensor_ids_list = _get_sensor_id_and_last_checkin_date_as_list()
        current_date_time = datetime.utcnow()
        for date_and_sensor_id in datetime_sensor_ids_list:
            clean_last_checkin_date = date_and_sensor_id[1]
            if (current_date_time - clean_last_checkin_date).days >= delete_sensors_older_days:
                _delete_sensor_id(date_and_sensor_id[0])
        write_to_sql_database("VACUUM;", None, sql_database_location=file_locations.sensor_checkin_database)
    except Exception as error:
        logger.primary_logger.warning("Error trying to delete old sensors from the Check-Ins database: " + str(error))
    return view_sensor_check_ins()


@html_sensor_check_ins_routes.route("/CheckinSensorSearch")
@auth.login_required
def view_search_sensor_check_ins():
    buttons_state = ""
    if app_cached_variables.checkin_search_sensor_id == "":
        buttons_state = "disabled"
    return render_template("software_checkin_search.html",
                           PageURL="/CheckinSensorSearch",
                           SearchSensorInfo=app_cached_variables.checkin_sensor_info,
                           SearchSensorDeleteDisabled=buttons_state,
                           SearchSensorClearDisabled=buttons_state,
                           PrimaryLog=app_cached_variables.checkin_search_primary_log,
                           SensorLog=app_cached_variables.checkin_search_sensors_log)


@html_sensor_check_ins_routes.route("/ClearOldSearchSensorCheckIns")
@auth.login_required
def search_sensor_clear_old_check_ins():
    if app_cached_variables.checkin_search_sensor_id != "":
        _clear_old_sensor_checkin_data(app_cached_variables.checkin_search_sensor_id)
        _update_search_sensor_check_ins(app_cached_variables.checkin_search_sensor_id)
    return view_search_sensor_check_ins()


@html_sensor_check_ins_routes.route("/DeleteSensorCheckinID")
@auth.login_required
def search_sensor_delete_senor_id():
    db_location = file_locations.sensor_checkin_database
    sensor_id = app_cached_variables.checkin_search_sensor_id
    if sensor_id != "":
        write_to_sql_database("DROP TABLE '" + sensor_id + "';", None, sql_database_location=db_location)
        _update_search_sensor_check_ins(sensor_id)
    return view_search_sensor_check_ins()


@html_sensor_check_ins_routes.route("/SearchCheckinSensorID", methods=["POST"])
@auth.login_required
def search_sensor_check_ins():
    if request.form.get("sensor_id") is not None:
        sensor_id = get_clean_sql_table_name(str(request.form.get("sensor_id")))
        _update_search_sensor_check_ins(sensor_id)
    return view_search_sensor_check_ins()


def _update_search_sensor_check_ins(sensor_id):
    if check_sensor_id_exists(sensor_id):
        app_cached_variables.checkin_search_sensor_id = sensor_id
        new_sensor_info_string = _get_sensor_info_string(app_cached_variables.checkin_search_sensor_id)
        app_cached_variables.checkin_sensor_info = new_sensor_info_string
        _search_checkin_get_logs(app_cached_variables.checkin_search_sensor_id)
    else:
        app_cached_variables.checkin_search_sensor_id = ""
        app_cached_variables.checkin_sensor_info = "Sensor ID Not Found\n\n"
        app_cached_variables.checkin_search_sensor_installed_sensors = ""
        app_cached_variables.checkin_search_primary_log = ""
        app_cached_variables.checkin_search_sensors_log = ""


def _search_checkin_get_logs(sensor_id, db_location=file_locations.sensor_checkin_database):
    app_cached_variables.checkin_search_primary_log = ""
    app_cached_variables.checkin_search_sensors_log = ""
    if sensor_id.isalnum():
        get_primary_log_sql = "SELECT " + db_sensor_check_in_primary_log + " FROM '" + sensor_id + \
                              "' ORDER BY " + db_all_tables_datetime + " DESC;"
        primary_logs = sql_execute_get_data(get_primary_log_sql, sql_database_location=db_location)

        get_sensors_log_sql = "SELECT " + db_sensor_check_in_sensors_log + " FROM '" + sensor_id + \
                              "' ORDER BY " + db_all_tables_datetime + " DESC;"
        sensors_logs = sql_execute_get_data(get_sensors_log_sql, sql_database_location=db_location)

        found_log = False
        for data_entry in primary_logs:
            if found_log:
                break
            for log_entry in data_entry:
                if log_entry != "":
                    app_cached_variables.checkin_search_primary_log = str(log_entry)
                    found_log = True
        found_log = False
        for data_entry in sensors_logs:
            if found_log:
                break
            for log_entry in data_entry:
                if log_entry != "":
                    app_cached_variables.checkin_search_sensors_log = str(log_entry)
                    found_log = True


def _get_sensor_info_string(sensor_id, db_location=file_locations.sensor_checkin_database):
    get_sensor_checkin_count_per_id_sql = "SELECT count('" + db_all_tables_datetime + "') FROM '" + sensor_id + "';"
    checkin_count = sql_execute_get_data(get_sensor_checkin_count_per_id_sql, sql_database_location=db_location)

    get_current_version_sql = "SELECT " + db_sensor_check_in_version + " FROM '" + sensor_id + \
                              "' ORDER BY " + db_all_tables_datetime + " DESC LIMIT 1;"
    current_sensor_version = sql_execute_get_data(get_current_version_sql, sql_database_location=db_location)

    get_installed_sensors_sql = "SELECT " + db_sensor_check_in_installed_sensors + " FROM '" + sensor_id + \
                                "' WHERE " + db_sensor_check_in_installed_sensors + " != '' ORDER BY " \
                                + db_all_tables_datetime + " DESC LIMIT 1;"
    last_installed_sensors = sql_execute_get_data(get_installed_sensors_sql, sql_database_location=db_location)

    get_current_uptime_sql = "SELECT " + db_sensor_uptime + " FROM '" + sensor_id + \
                             "' ORDER BY " + db_all_tables_datetime + " DESC LIMIT 1;"
    current_sensor_uptime = sql_execute_get_data(get_current_uptime_sql, sql_database_location=db_location)

    get_last_sensor_checkin_date_sql = "SELECT " + db_all_tables_datetime + " FROM '" + sensor_id + \
                                       "'ORDER BY " + db_all_tables_datetime + " DESC LIMIT 1;"
    last_checkin_date = sql_execute_get_data(get_last_sensor_checkin_date_sql, sql_database_location=db_location)

    checkin_hour_offset = app_config_access.primary_config.utc0_hour_offset
    clean_last_checkin_date = _get_sql_element(last_checkin_date)
    web_view_last_checkin_date = _get_converted_datetime(clean_last_checkin_date, hour_offset=checkin_hour_offset)
    web_view_last_checkin_date = web_view_last_checkin_date.strftime("%Y-%m-%d %H:%M:%S")
    return "Sensor ID: " + sensor_id + \
           "\nSoftware Version: " + _get_sql_element(current_sensor_version) + \
           "\n" + _get_sql_element(last_installed_sensors) + \
           "\nSensor Uptime in Minutes: " + _get_sql_element(current_sensor_uptime) + \
           "\nTotal Checkin Count: " + _get_sql_element(checkin_count) + \
           "\nLast Check-in DateTime: " + web_view_last_checkin_date + "\n\n"


@html_sensor_check_ins_routes.route("/ClearOldCheckinData")
@auth.login_required
def clear_check_ins_counts():
    for sensor_id in _get_check_in_sensor_ids():
        _clear_old_sensor_checkin_data(sensor_id)
    write_to_sql_database("VACUUM;", None, sql_database_location=file_locations.sensor_checkin_database)
    return view_sensor_check_ins()


def _clear_old_sensor_checkin_data(sensor_id):
    db_location = file_locations.sensor_checkin_database

    try:
        get_last_checkin_date_sql = "SELECT " + db_all_tables_datetime + " FROM '" + sensor_id + \
                                    "' ORDER BY " + db_all_tables_datetime + " DESC LIMIT 1;"
        raw_last_checkin_date = sql_execute_get_data(get_last_checkin_date_sql, sql_database_location=db_location)

        get_version_sql = "SELECT " + db_sensor_check_in_version + " FROM '" + sensor_id + \
                          "' ORDER BY " + db_all_tables_datetime + " DESC LIMIT 1;"
        sensor_version = sql_execute_get_data(get_version_sql, sql_database_location=db_location)

        get_installed_sensors_sql = "SELECT " + db_sensor_check_in_installed_sensors + " FROM '" + sensor_id + \
                                    "' WHERE " + db_sensor_check_in_installed_sensors + \
                                    " != '' ORDER BY " + db_all_tables_datetime + " DESC LIMIT 1;"
        sensor_installed_sensors = sql_execute_get_data(get_installed_sensors_sql, sql_database_location=db_location)

        get_uptime_sql = "SELECT " + db_sensor_uptime + " FROM '" + sensor_id + \
                         "' ORDER BY " + db_all_tables_datetime + " DESC LIMIT 1;"
        sensor_uptime = sql_execute_get_data(get_uptime_sql, sql_database_location=db_location)

        get_primary_log_sql = "SELECT " + db_sensor_check_in_primary_log + " FROM '" + sensor_id + \
                              "' WHERE " + db_sensor_check_in_primary_log + \
                              " != '' ORDER BY " + db_all_tables_datetime + " DESC LIMIT 1;"
        sensor_primary_log = sql_execute_get_data(get_primary_log_sql, sql_database_location=db_location)

        get_sensor_log_sql = "SELECT " + db_sensor_check_in_sensors_log + " FROM '" + sensor_id + \
                             "' WHERE " + db_sensor_check_in_sensors_log + \
                             " != '' ORDER BY " + db_all_tables_datetime + " DESC LIMIT 1;"
        sensor_sensor_log = sql_execute_get_data(get_sensor_log_sql, sql_database_location=db_location)

        write_to_sql_database("DELETE FROM '" + sensor_id + "';", None, sql_database_location=db_location)

        sql_ex_string = "INSERT OR IGNORE INTO '" + sensor_id + "' (" + \
                        db_all_tables_datetime + "," + \
                        db_sensor_check_in_version + "," + \
                        db_sensor_check_in_installed_sensors + "," + \
                        db_sensor_uptime + "," + \
                        db_sensor_check_in_primary_log + "," + \
                        db_sensor_check_in_sensors_log + ")" + \
                        " VALUES (?,?,?,?,?,?);"

        sql_data = [_get_sql_element(raw_last_checkin_date), _get_sql_element(sensor_version),
                    _get_sql_element(sensor_installed_sensors), _get_sql_element(sensor_uptime),
                    _get_sql_element(sensor_primary_log), _get_sql_element(sensor_sensor_log)]
        write_to_sql_database(sql_ex_string, sql_data, sql_database_location=db_location)
    except Exception as error:
        logger.network_logger.error("Sensor Check-ins - Clearing Sensor '" + sensor_id + "' Data: " + str(error))


def _get_sql_element(sql_data):
    try:
        for entry1 in sql_data:
            for entry2 in entry1:
                return str(entry2)
    except Exception as error:
        logger.network_logger.debug("Error extracting data in Sensor Check-ins: " + str(error))
        return "Error"
    return ""


def _get_check_in_sensor_ids():
    """
    Returns a list of Sensor ID's from the Check-In database.
    If include_last_datetime=True, returns a list of [datetime, sensor_id]
    """
    db_location = file_locations.sensor_checkin_database
    try:
        get_sensor_checkin_ids_sql = "SELECT name FROM sqlite_master WHERE type='table';"
        sensor_ids = sql_execute_get_data(get_sensor_checkin_ids_sql, sql_database_location=db_location)

        cleaned_sensor_list = []
        for sensor in sensor_ids:
            cleaned_sensor_list.append(str(sensor[0]))
        return cleaned_sensor_list
    except Exception as error:
        logger.network_logger.error("Unable to retrieve Check-In Sensor IDs: " + str(error))
    return []


def _get_sensor_id_and_last_checkin_date_as_list(sort_by_date_time=True):
    db_location = file_locations.sensor_checkin_database
    sensor_id_list = _get_check_in_sensor_ids()

    return_sensor_ids_list = []
    for sensor_id in sensor_id_list:
        get_last_checkin_date_sql = "SELECT " + db_all_tables_datetime + " FROM '" + sensor_id + \
                                    "' ORDER BY " + db_all_tables_datetime + " DESC LIMIT 1;"
        raw_last_checkin_date = sql_execute_get_data(get_last_checkin_date_sql, sql_database_location=db_location)
        clean_last_checkin_date = _get_sql_element(raw_last_checkin_date)
        return_sensor_ids_list.append([sensor_id, _get_converted_datetime(clean_last_checkin_date)])
    if sort_by_date_time:
        return_sensor_ids_list.sort(key=lambda x: x[1], reverse=True)
    return return_sensor_ids_list


def _get_converted_datetime(date_time_string, date_format="%Y-%m-%d %H:%M:%S", hour_offset=None):
    try:
        date_time_object = datetime.strptime(date_time_string[:19], date_format)
        if hour_offset is not None:
            date_time_object = date_time_object + timedelta(hours=hour_offset)
        return date_time_object
    except Exception as error:
        logger.network_logger.debug("Checkins View - Unable to convert Date & Time from string: " + str(error))
    return datetime.strptime("1901-01-01 01:01:01", date_format)


def _delete_sensor_id(sensor_id):
    """ Deletes provided Text Sensor ID from the Check-In database """
    database_location = file_locations.sensor_checkin_database
    write_to_sql_database("DROP TABLE '" + sensor_id + "';", None, sql_database_location=database_location)


def check_sensor_id_exists(sensor_id):
    sql_query = "SELECT count(name) FROM sqlite_master WHERE type='table' AND name='" + sensor_id + "'"
    try:
        database_connection = sqlite3.connect(file_locations.sensor_checkin_database)
        sqlite_database = database_connection.cursor()
        sqlite_database.execute(sql_query)
        if sqlite_database.fetchone()[0]:
            database_connection.close()
            return True
        else:
            database_connection.close()
            return False
    except Exception as error:
        logger.primary_logger.error("Unable to access CheckIns Database: " + str(error))
