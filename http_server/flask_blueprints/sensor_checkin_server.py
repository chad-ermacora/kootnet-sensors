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
from datetime import datetime
from flask import Blueprint, request
from operations_modules import logger
from operations_modules import file_locations
from operations_modules import app_cached_variables
from configuration_modules import app_config_access
from operations_modules.sqlite_database import create_table_and_datetime, check_sql_table_and_column, \
    write_to_sql_database, get_clean_sql_table_name

html_sensor_check_ins_routes = Blueprint("html_sensor_check_ins_routes", __name__)


@html_sensor_check_ins_routes.route("/remote-sensor-checkin", methods=["POST"])
@html_sensor_check_ins_routes.route("/SensorCheckin", methods=["POST"])
def remote_sensor_check_ins():
    if app_config_access.checkin_config.enable_checkin_recording:
        if request.form.get("checkin_id"):
            db_all_tables_datetime = app_cached_variables.database_variables.all_tables_datetime
            db_sensor_check_in_version = app_cached_variables.database_variables.sensor_check_in_version
            db_sensor_check_in_is = app_cached_variables.database_variables.sensor_check_in_installed_sensors
            db_sensor_check_in_primary_log = app_cached_variables.database_variables.sensor_check_in_primary_log
            db_sensor_check_in_sensors_log = app_cached_variables.database_variables.sensor_check_in_sensors_log
            db_sensor_uptime = app_cached_variables.database_variables.sensor_uptime

            checkin_id = get_clean_sql_table_name(str(request.form.get("checkin_id")))
            logger.network_logger.debug("* Sensor ID:" + checkin_id + " checked in from " + str(request.remote_addr))

            current_datetime = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

            try:
                db_connection = sqlite3.connect(file_locations.sensor_checkin_database)
                db_cursor = db_connection.cursor()

                create_table_and_datetime(checkin_id, db_cursor)
                check_sql_table_and_column(checkin_id, db_sensor_check_in_version, db_cursor)
                check_sql_table_and_column(checkin_id, db_sensor_check_in_is, db_cursor)
                check_sql_table_and_column(checkin_id, db_sensor_uptime, db_cursor)
                check_sql_table_and_column(checkin_id, db_sensor_check_in_primary_log, db_cursor)
                check_sql_table_and_column(checkin_id, db_sensor_check_in_sensors_log, db_cursor)
                db_connection.commit()
                db_connection.close()

                sql_ex_string = "INSERT OR IGNORE INTO '" + checkin_id + "' (" + \
                                db_all_tables_datetime + "," + \
                                db_sensor_check_in_version + "," + \
                                db_sensor_check_in_is + "," + \
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
