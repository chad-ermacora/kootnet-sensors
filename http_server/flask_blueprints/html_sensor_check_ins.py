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
    sql_execute_get_data
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
        all_tables_datetime = app_cached_variables.database_variables.all_tables_datetime
        sensor_check_in_version = app_cached_variables.database_variables.sensor_check_in_version
        sensor_check_in_primary_log = app_cached_variables.database_variables.sensor_check_in_primary_log
        sensor_check_in_sensors_log = app_cached_variables.database_variables.sensor_check_in_sensors_log
        try:
            db_connection = sqlite3.connect(file_locations.sensor_checkin_database)
            db_cursor = db_connection.cursor()

            create_table_and_datetime(checkin_id, db_cursor)
            check_sql_table_and_column(checkin_id, sensor_check_in_version, db_cursor)
            check_sql_table_and_column(checkin_id, sensor_check_in_primary_log, db_cursor)
            check_sql_table_and_column(checkin_id, sensor_check_in_sensors_log, db_cursor)

            sql_ex_string = "INSERT OR IGNORE INTO '{CheckinIDTable}' " + \
                            "({DateTimeColumn},{KootnetVersionColumn},{PrimaryLogColumn},{SensorLogColumn})" + \
                            " VALUES ('{CurrentDateTime}','{KootnetVersion}','{PrimaryLog}','{SensorLog}');"
            sql_ex_string = sql_ex_string.format(CheckinIDTable=checkin_id, DateTimeColumn=all_tables_datetime,
                                                 KootnetVersionColumn=sensor_check_in_version,
                                                 PrimaryLogColumn=sensor_check_in_primary_log,
                                                 SensorLogColumn=sensor_check_in_sensors_log,
                                                 CurrentDateTime=current_datetime,
                                                 KootnetVersion=str(request.form.get("program_version")),
                                                 PrimaryLog=str(request.form.get("primary_log")),
                                                 SensorLog=str(request.form.get("sensor_log")))
            db_cursor.execute(sql_ex_string)
            db_connection.commit()
            db_connection.close()
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

        get_current_version_sql = "SELECT KootnetVersion FROM '" + cleaned_id + "' ORDER BY KootnetVersion DESC LIMIT 1;"
        current_sensor_version = sql_execute_get_data(get_current_version_sql, sql_database_location=db_location)
        clean_last_checkin_date = _get_sql_element(last_checkin_date)
        if len(clean_last_checkin_date) > 16:
            try:
                last_remote_checkin_date = datetime.strptime(clean_last_checkin_date[:-4], "%Y-%m-%d %H:%M:%S")
                if (current_date_time - last_remote_checkin_date) < timedelta(0.04167):
                    contact_in_past_hour += 1
                    contact_in_past_12hour += 1
                    contact_in_past_day += 1
                    contact_in_past_week += 1
                    contact_in_past_month += 1
                elif (current_date_time - last_remote_checkin_date) < timedelta(0.5):
                    contact_in_past_12hour += 1
                    contact_in_past_day += 1
                    contact_in_past_week += 1
                    contact_in_past_month += 1
                elif (current_date_time - last_remote_checkin_date) < timedelta(1):
                    contact_in_past_day += 1
                    contact_in_past_week += 1
                    contact_in_past_month += 1
                elif (current_date_time - last_remote_checkin_date) < timedelta(7):
                    contact_in_past_week += 1
                    contact_in_past_month += 1
                elif (current_date_time - last_remote_checkin_date) < timedelta(30):
                    contact_in_past_month += 1
            except Exception as error:
                logger.network_logger.warning("Error in last checkin verification: " + str(error))
        sensor_statistics += "Sensor ID: " + cleaned_id + \
                             "\nSoftware Version: " + _get_sql_element(current_sensor_version) + \
                             "\nTotal Checkin Count: " + _get_sql_element(checkin_count) + \
                             "\nLast Checkin in 'UTC0': " + clean_last_checkin_date + "\n\n"
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
                           CheckinSensorStatistics=sensor_statistics)


def _get_sql_element(sql_data):
    try:
        for date_entry in sql_data:
            for date_entry2 in date_entry:
                return str(date_entry2)
    except Exception as error:
        logger.network_logger.debug("Error extracting data in Sensor Check-ins: " + str(error))
        return "Error"
    return ""


def clear_check_ins_counts():
    pass
