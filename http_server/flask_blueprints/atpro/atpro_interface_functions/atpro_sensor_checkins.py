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
from operations_modules.app_generic_functions import get_file_size
from configuration_modules import app_config_access
from operations_modules.sqlite_database import sql_execute_get_data, write_to_sql_database, get_clean_sql_table_name, \
    get_sql_element
from http_server.server_http_auth import auth
from http_server.flask_blueprints.atpro.atpro_interface_functions.atpro_generic import get_html_atpro_index

html_atpro_sensor_check_ins_routes = Blueprint("html_atpro_sensor_check_ins_routes", __name__)

db_all_tables_datetime = app_cached_variables.database_variables.all_tables_datetime
db_sensor_check_in_version = app_cached_variables.database_variables.sensor_check_in_version
db_sensor_check_in_installed_sensors = app_cached_variables.database_variables.sensor_check_in_installed_sensors
db_sensor_check_in_primary_log = app_cached_variables.database_variables.sensor_check_in_primary_log
db_sensor_check_in_sensors_log = app_cached_variables.database_variables.sensor_check_in_sensors_log
db_sensor_uptime = app_cached_variables.database_variables.sensor_uptime


@html_atpro_sensor_check_ins_routes.route("/atpro/sensor-checkin-view")
@auth.login_required
def html_atpro_sensor_checkin_main_view():
    db_location = file_locations.sensor_checkin_database
    get_sensor_checkin_count_sql = "SELECT count(*) FROM sqlite_master WHERE type = 'table'" + \
                                   "AND name != 'android_metadata' AND name != 'sqlite_sequence';"
    sensor_count = sql_execute_get_data(get_sensor_checkin_count_sql, sql_database_location=db_location)
    sensor_ids_and_date_list = _get_sensor_id_and_last_checkin_date_as_list()

    sensor_statistics = ""
    current_date_time = datetime.utcnow()

    sensor_contact_count = 0
    count_contact_days = app_config_access.checkin_config.count_contact_days
    for count, sensor_id_and_date in enumerate(sensor_ids_and_date_list):
        cleaned_id = sensor_id_and_date[0]
        checkin_date = sensor_id_and_date[1]
        if (current_date_time - checkin_date) < timedelta(days=count_contact_days):
            sensor_contact_count += 1
        if count < app_config_access.checkin_config.main_page_max_sensors:
            sensor_statistics += _get_sensor_info_string(cleaned_id)

    try:
        past_checkin_percent = round(((sensor_contact_count / int(get_sql_element(sensor_count))) * 100), 2)
    except ZeroDivisionError:
        logger.primary_logger.debug("No Sensors found for Sensor Checkin View")
        past_checkin_percent = 0.0
    except Exception as error:
        logger.primary_logger.warning("Unknown Sensor Checkin View Error: " + str(error))
        past_checkin_percent = 0.0

    if os.path.isfile(file_locations.sensor_checkin_database):
        db_size_mb = get_file_size(file_locations.sensor_checkin_database, round_to=3)
    else:
        db_size_mb = 0.0

    enabled_text = "<span style='color: red;'>Disabled</span>"
    if app_config_access.checkin_config.enable_checkin_recording:
        enabled_text = "<span style='color: green;'>Enabled</span>"
    return render_template("ATPro_admin/page_templates/sensor_checkins/sensor-checkin-main-view.html",
                           MaxSensorCount=app_config_access.checkin_config.main_page_max_sensors,
                           SensorsInDatabase=get_sql_element(sensor_count),
                           CheckinDBSize=db_size_mb,
                           ContactInPastDays=app_config_access.checkin_config.count_contact_days,
                           TotalSensorsContactDays=sensor_contact_count,
                           PercentOfTotalDays=past_checkin_percent,
                           DeleteSensorsOlderDays=app_config_access.checkin_config.delete_sensors_older_days,
                           CheckinEnabledText=enabled_text,
                           CheckinSensorStatistics=sensor_statistics)


@html_atpro_sensor_check_ins_routes.route("/atpro/sensor-checkin-delete-old-sensors", methods=["POST"])
@auth.login_required
def delete_sensors_older_then():
    try:
        app_config_access.checkin_config.update_with_html_request(request, skip_all_but_delete_setting=True)
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
    return get_html_atpro_index(run_script="SelectNav('sensor-checkin-view');")


@html_atpro_sensor_check_ins_routes.route("/atpro/sensor-checkin-search")
@auth.login_required
def view_search_sensor_check_ins():
    buttons_state = ""
    if app_cached_variables.checkin_search_sensor_id == "":
        buttons_state = "disabled"
    old_text = "col-6 col-m-12 col-sm-12"
    new_text = "col-12 col-m-12 col-sm-12"
    sensor_search_info = app_cached_variables.checkin_sensor_info.replace(old_text, new_text)
    sensor_search_info = sensor_search_info.replace(' class="counter bg-success"', "")
    return render_template("ATPro_admin/page_templates/sensor_checkins/sensor-checkin-search.html",
                           SearchSensorInfo=sensor_search_info,
                           SearchSensorDeleteDisabled=buttons_state,
                           SearchSensorClearDisabled=buttons_state)


@html_atpro_sensor_check_ins_routes.route("/atpro/sc-logs/log-primary")
@auth.login_required
def get_sensor_checkin_log_primary():
    return app_cached_variables.checkin_search_primary_log.replace("\n", "<br>")


@html_atpro_sensor_check_ins_routes.route("/atpro/sc-logs/log-sensors")
@auth.login_required
def get_sensor_checkin_log_sensors():
    return app_cached_variables.checkin_search_sensors_log.replace("\n", "<br>")


@html_atpro_sensor_check_ins_routes.route("/atpro/sensor-checkin-clear-old-checkins")
@auth.login_required
def search_sensor_clear_old_check_ins():
    if app_cached_variables.checkin_search_sensor_id != "":
        _clear_old_sensor_checkin_data(app_cached_variables.checkin_search_sensor_id)
        _update_search_sensor_check_ins(app_cached_variables.checkin_search_sensor_id)
    return view_search_sensor_check_ins()


@html_atpro_sensor_check_ins_routes.route("/atpro/sensor-checkin-search-delete-sensor")
@auth.login_required
def search_sensor_delete_senor_id():
    db_location = file_locations.sensor_checkin_database
    sensor_id = app_cached_variables.checkin_search_sensor_id
    if sensor_id != "":
        write_to_sql_database("DROP TABLE '" + sensor_id + "';", None, sql_database_location=db_location)
        _update_search_sensor_check_ins(sensor_id)
    return view_search_sensor_check_ins()


@html_atpro_sensor_check_ins_routes.route("/atpro/sensor-checkin-id-search", methods=["POST"])
@auth.login_required
def search_sensor_check_ins():
    if request.form.get("sensor_id") is not None:
        sensor_id = get_clean_sql_table_name(str(request.form.get("sensor_id")))
        _update_search_sensor_check_ins(sensor_id)
    return view_search_sensor_check_ins()


def _update_search_sensor_check_ins(sensor_id):
    if _check_sensor_id_exists(sensor_id):
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

    get_primary_log_sql = "SELECT " + db_sensor_check_in_primary_log + " FROM '" + sensor_id + \
                          "' WHERE " + db_sensor_check_in_primary_log + " != '' ORDER BY " \
                          + db_all_tables_datetime + " DESC LIMIT 1;"
    primary_logs = sql_execute_get_data(get_primary_log_sql, sql_database_location=db_location)

    get_sensors_log_sql = "SELECT " + db_sensor_check_in_sensors_log + " FROM '" + sensor_id + \
                          "' WHERE " + db_sensor_check_in_sensors_log + " != '' ORDER BY " \
                          + db_all_tables_datetime + " DESC LIMIT 1;"
    sensors_logs = sql_execute_get_data(get_sensors_log_sql, sql_database_location=db_location)
    try:
        app_cached_variables.checkin_search_primary_log = str(primary_logs[0][0])
        app_cached_variables.checkin_search_sensors_log = str(sensors_logs[0][0])
    except Exception as error:
        log_msg = "Sensor Checkin Search - Unable to get/set logs: "
        logger.network_logger.warning(log_msg + str(error))


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
    clean_last_checkin_date = get_sql_element(last_checkin_date)
    web_view_last_checkin_date = _get_converted_datetime(clean_last_checkin_date, hour_offset=checkin_hour_offset)
    web_view_last_checkin_date = web_view_last_checkin_date.strftime("%Y-%m-%d %H:%M:%S")
    return render_template("ATPro_admin/page_templates/sensor_checkins/sensor-checkin-info-template.html",
                           SensorID=sensor_id,
                           LastCheckinDate=web_view_last_checkin_date,
                           TotalCheckins=get_sql_element(checkin_count),
                           SoftwareVersion=get_sql_element(current_sensor_version),
                           SensorUptime=get_sql_element(current_sensor_uptime),
                           InstalledSensors=get_sql_element(last_installed_sensors))


@html_atpro_sensor_check_ins_routes.route("/atpro/sensor-checkin-clear-old-data")
@auth.login_required
def clear_check_ins_counts():
    for sensor_id in _get_check_in_sensor_ids():
        _clear_old_sensor_checkin_data(sensor_id)
    write_to_sql_database("VACUUM;", None, sql_database_location=file_locations.sensor_checkin_database)
    return get_html_atpro_index(run_script="SelectNav('sensor-checkin-view');")


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

        sql_data = [get_sql_element(raw_last_checkin_date), get_sql_element(sensor_version),
                    get_sql_element(sensor_installed_sensors), get_sql_element(sensor_uptime),
                    get_sql_element(sensor_primary_log), get_sql_element(sensor_sensor_log)]
        write_to_sql_database(sql_ex_string, sql_data, sql_database_location=db_location)
    except Exception as error:
        logger.network_logger.error("Sensor Check-ins - Clearing Sensor '" + sensor_id + "' Data: " + str(error))


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
        clean_last_checkin_date = get_sql_element(raw_last_checkin_date)
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


def _check_sensor_id_exists(sensor_id):
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
