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
import sqlite3
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request
from operations_modules import logger
from operations_modules import file_locations
from operations_modules import app_cached_variables
from operations_modules.sqlite_database import create_table_and_datetime, check_sql_table_and_column, \
    sql_execute_get_data, write_to_sql_database
from http_server.server_http_auth import auth
from http_server.server_http_generic_functions import get_html_hidden_state

html_sensor_check_ins_routes = Blueprint("html_sensor_check_ins_routes", __name__)
max_statistics_lines = 200


@html_sensor_check_ins_routes.route("/SensorCheckin", methods=["POST"])
def remote_sensor_check_ins():
    if request.form.get("checkin_id"):
        checkin_id = "KS" + str(request.form.get("checkin_id"))
        logger.network_logger.debug("* Sensor ID:" + checkin_id + " checked in from " + str(request.remote_addr))

        current_datetime = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        db_all_tables_datetime = app_cached_variables.database_variables.all_tables_datetime
        db_sensor_check_in_version = app_cached_variables.database_variables.sensor_check_in_version
        db_sensor_uptime = app_cached_variables.database_variables.sensor_uptime
        db_sensor_check_in_primary_log = app_cached_variables.database_variables.sensor_check_in_primary_log
        db_sensor_check_in_sensors_log = app_cached_variables.database_variables.sensor_check_in_sensors_log

        try:
            db_connection = sqlite3.connect(file_locations.sensor_checkin_database)
            db_cursor = db_connection.cursor()

            create_table_and_datetime(checkin_id, db_cursor)
            check_sql_table_and_column(checkin_id, db_sensor_check_in_version, db_cursor)
            check_sql_table_and_column(checkin_id, db_sensor_uptime, db_cursor)
            check_sql_table_and_column(checkin_id, db_sensor_check_in_primary_log, db_cursor)
            check_sql_table_and_column(checkin_id, db_sensor_check_in_sensors_log, db_cursor)
            db_connection.commit()
            db_connection.close()

            sql_ex_string = "INSERT OR IGNORE INTO '" + checkin_id + "' (" + \
                            db_all_tables_datetime + "," + \
                            db_sensor_check_in_version + "," + \
                            db_sensor_uptime + "," + \
                            db_sensor_check_in_primary_log + "," + \
                            db_sensor_check_in_sensors_log + ")" + \
                            " VALUES (?,?,?,?,?);"

            sql_data = [current_datetime, str(request.form.get("program_version")),
                        str(request.form.get("sensor_uptime")), str(request.form.get("primary_log")),
                        str(request.form.get("sensor_log"))]
            write_to_sql_database(sql_ex_string, sql_data, sql_database_location=file_locations.sensor_checkin_database)
            return "OK", 202
        except Exception as error:
            logger.network_logger.warning("Sensor Checkin error for " + str(checkin_id) + ": " + str(error))
        return "Failed", 400


@html_sensor_check_ins_routes.route("/ViewSensorCheckin")
@auth.login_required
def view_sensor_check_ins():
    db_location = file_locations.sensor_checkin_database

    get_sensor_checkin_count_sql = "SELECT count(*) FROM sqlite_master WHERE type = 'table'" + \
                                   "AND name != 'android_metadata' AND name != 'sqlite_sequence';"
    sensor_count = sql_execute_get_data(get_sensor_checkin_count_sql, sql_database_location=db_location)

    get_sensor_checkin_ids_sql = "SELECT name FROM sqlite_master WHERE type='table';"
    sensor_ids = sql_execute_get_data(get_sensor_checkin_ids_sql, sql_database_location=db_location)

    sensor_statistics = "Per Sensor Check-in Information\n\n"
    current_date_time = datetime.utcnow()
    contact_in_past_hour = 0
    contact_in_past_12hour = 0
    contact_in_past_day = 0
    contact_in_past_week = 0
    contact_in_past_month = 0
    for sensor_id in sensor_ids:
        cleaned_id = str(sensor_id[0]).strip()

        get_sensor_checkin_count_per_id_sql = "SELECT count('DateTime') FROM '" + cleaned_id + "';"
        checkin_count = sql_execute_get_data(get_sensor_checkin_count_per_id_sql, sql_database_location=db_location)

        get_last_sensor_checkin_date_sql = "SELECT DateTime FROM '" + cleaned_id + "' ORDER BY DateTime DESC LIMIT 1;"
        last_checkin_date = sql_execute_get_data(get_last_sensor_checkin_date_sql, sql_database_location=db_location)

        get_current_version_sql = "SELECT KootnetVersion FROM '" + cleaned_id + "' ORDER BY DateTime DESC LIMIT 1;"
        current_sensor_version = sql_execute_get_data(get_current_version_sql, sql_database_location=db_location)

        get_current_uptime_sql = "SELECT SensorUpTime FROM '" + cleaned_id + "' ORDER BY DateTime DESC LIMIT 1;"
        current_sensor_uptime = sql_execute_get_data(get_current_uptime_sql, sql_database_location=db_location)
        clean_last_checkin_date = _get_sql_element(last_checkin_date)
        web_view_last_checkin_date = clean_last_checkin_date
        if len(clean_last_checkin_date) > 16:

            try:
                checkin_date_converted = datetime.strptime(clean_last_checkin_date[:-4], "%Y-%m-%d %H:%M:%S")
                if (current_date_time - checkin_date_converted) < timedelta(hours=1):
                    contact_in_past_hour += 1
                    contact_in_past_12hour += 1
                    contact_in_past_day += 1
                    contact_in_past_week += 1
                    contact_in_past_month += 1
                elif (current_date_time - checkin_date_converted) < timedelta(hours=12):
                    contact_in_past_12hour += 1
                    contact_in_past_day += 1
                    contact_in_past_week += 1
                    contact_in_past_month += 1
                elif (current_date_time - checkin_date_converted) < timedelta(days=1):
                    contact_in_past_day += 1
                    contact_in_past_week += 1
                    contact_in_past_month += 1
                elif (current_date_time - checkin_date_converted) < timedelta(days=7):
                    contact_in_past_week += 1
                    contact_in_past_month += 1
                elif (current_date_time - checkin_date_converted) < timedelta(weeks=4):
                    contact_in_past_month += 1
                checkin_hour_offset = app_cached_variables.checkin_hour_offset
                checkin_date_converted = checkin_date_converted + timedelta(hours=checkin_hour_offset)
                web_view_last_checkin_date = checkin_date_converted.strftime("%Y-%m-%d %H:%M:%S")
            except Exception as error:
                logger.network_logger.warning("Error in last checkin verification: " + str(error))
        sensor_statistics += "Sensor ID: " + cleaned_id + \
                             "\nSoftware Version: " + _get_sql_element(current_sensor_version) + \
                             "\nSensor Uptime in Minutes: " + _get_sql_element(current_sensor_uptime) + \
                             "\nTotal Checkin Count: " + _get_sql_element(checkin_count) + \
                             "\nLast Check-in DateTime: " + str(web_view_last_checkin_date) + "\n\n"
    sensor_statistics_lines = sensor_statistics.split("\n")
    if len(sensor_statistics_lines) > max_statistics_lines:
        sensor_statistics = ""
        for line in sensor_statistics_lines[:max_statistics_lines]:
            sensor_statistics += line + "\n"
    return render_template("software_checkin.html",
                           PageURL="/ViewSensorCheckin",
                           RestartServiceHidden=get_html_hidden_state(app_cached_variables.html_service_restart),
                           RebootSensorHidden=get_html_hidden_state(app_cached_variables.html_sensor_reboot),
                           SensorsInDatabase=_get_sql_element(sensor_count),
                           TotalSensorCountHour=contact_in_past_hour,
                           TotalSensorCountHour12=contact_in_past_12hour,
                           TotalSensorCountDay=contact_in_past_day,
                           TotalSensorCountWeek=contact_in_past_week,
                           TotalSensorCountMonth=contact_in_past_month,
                           CheckinHourOffset=app_cached_variables.checkin_hour_offset,
                           CheckinSensorStatistics=sensor_statistics)


@html_sensor_check_ins_routes.route("/ClearOldCheckinData")
@auth.login_required
def clear_check_ins_counts():
    db_location = file_locations.sensor_checkin_database
    get_sensor_checkin_ids_sql = "SELECT name FROM sqlite_master WHERE type='table';"
    sensor_ids = sql_execute_get_data(get_sensor_checkin_ids_sql, sql_database_location=db_location)

    for sensor_id in sensor_ids:
        cleaned_id = str(sensor_id[0]).strip()

        db_all_tables_datetime = app_cached_variables.database_variables.all_tables_datetime
        db_sensor_check_in_version = app_cached_variables.database_variables.sensor_check_in_version
        db_sensor_check_in_primary_log = app_cached_variables.database_variables.sensor_check_in_primary_log
        db_sensor_check_in_sensors_log = app_cached_variables.database_variables.sensor_check_in_sensors_log
        db_sensor_uptime = app_cached_variables.database_variables.sensor_uptime

        get_last_checkin_date_sql = "SELECT " + db_all_tables_datetime + " FROM '" + cleaned_id + \
                                           "' ORDER BY DateTime DESC LIMIT 1;"
        raw_last_checkin_date = sql_execute_get_data(get_last_checkin_date_sql, sql_database_location=db_location)

        get_version_sql = "SELECT " + db_sensor_check_in_version + " FROM '" + cleaned_id + \
                          "' ORDER BY DateTime DESC LIMIT 1;"
        sensor_version = sql_execute_get_data(get_version_sql, sql_database_location=db_location)

        get_uptime_sql = "SELECT " + db_sensor_uptime + " FROM '" + cleaned_id + \
                         "' ORDER BY DateTime DESC LIMIT 1;"
        sensor_uptime = sql_execute_get_data(get_uptime_sql, sql_database_location=db_location)

        get_primary_log_sql = "SELECT " + db_sensor_check_in_primary_log + " FROM '" + cleaned_id + \
                              "' ORDER BY DateTime DESC LIMIT 1;"
        sensor_primary_log = sql_execute_get_data(get_primary_log_sql, sql_database_location=db_location)

        get_sensor_log_sql = "SELECT " + db_sensor_check_in_sensors_log + " FROM '" + cleaned_id + \
                             "' ORDER BY DateTime DESC LIMIT 1;"
        sensor_sensor_log = sql_execute_get_data(get_sensor_log_sql, sql_database_location=db_location)

        write_to_sql_database("DELETE FROM '" + cleaned_id + "';", None, sql_database_location=db_location)

        sql_ex_string = "INSERT OR IGNORE INTO '" + cleaned_id + "' (" + \
                        db_all_tables_datetime + "," + \
                        db_sensor_check_in_version + "," + \
                        db_sensor_uptime + "," + \
                        db_sensor_check_in_primary_log + "," + \
                        db_sensor_check_in_sensors_log + ")" + \
                        " VALUES (?,?,?,?,?);"

        sql_data = [_get_sql_element(raw_last_checkin_date), _get_sql_element(sensor_version),
                    _get_sql_element(sensor_uptime), _get_sql_element(sensor_primary_log),
                    _get_sql_element(sensor_sensor_log)]
        if _get_sql_element(raw_last_checkin_date) != "NA":
            write_to_sql_database(sql_ex_string, sql_data, sql_database_location=file_locations.sensor_checkin_database)
    return view_sensor_check_ins()


@html_sensor_check_ins_routes.route("/SaveCheckinSettings", methods=["POST"])
@auth.login_required
def html_set_checkin_settings():
    logger.network_logger.debug("** HTML Apply - Saving Check-ins Settings - Source: " + str(request.remote_addr))
    if request.method == "POST":
        if request.form.get("checkin_hour_offset") is not None:
            try:
                new_offset = float(request.form.get("checkin_hour_offset"))
                app_cached_variables.checkin_hour_offset = new_offset
            except Exception as error:
                logger.network_logger.warning("Unable to set new Sensor Check-in Hour Offset: " + str(error))
    return view_sensor_check_ins()


def _get_sql_element(sql_data):
    try:
        for date_entry in sql_data:
            for date_entry2 in date_entry:
                return str(date_entry2)
    except Exception as error:
        logger.network_logger.debug("Error extracting data in Sensor Check-ins: " + str(error))
        return "Error"
    return "NA"
