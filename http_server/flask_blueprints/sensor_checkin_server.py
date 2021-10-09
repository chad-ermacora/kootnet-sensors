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
db_v = app_cached_variables.database_variables
sc_database_location = file_locations.sensor_checkin_database


@html_sensor_check_ins_routes.route("/remote-sensor-checkin", methods=["POST"])
@html_sensor_check_ins_routes.route("/SensorCheckin", methods=["POST"])
def remote_sensor_check_ins():
    if app_config_access.checkin_config.enable_checkin_recording:
        if request.form.get("checkin_id"):
            checkin_id = get_clean_sql_table_name(str(request.form.get("checkin_id")))
            logger.network_logger.debug("* Sensor ID:" + checkin_id + " checked in from " + str(request.remote_addr))
            check_sensor_checkin_columns(checkin_id)
            try:
                sql_ex_string = "INSERT OR IGNORE INTO '" + checkin_id + "' (" + \
                                db_v.all_tables_datetime + "," + \
                                db_v.sensor_name + "," + \
                                db_v.ip + "," + \
                                db_v.sensor_check_in_version + "," + \
                                db_v.sensor_check_in_installed_sensors + "," + \
                                db_v.sensor_uptime + "," + \
                                db_v.sensor_check_in_primary_log + "," + \
                                db_v.sensor_check_in_network_log + "," + \
                                db_v.sensor_check_in_sensors_log + ")" + \
                                " VALUES (?,?,?,?,?,?,?,?,?);"

                sensor_name = _get_cleaned_data(request.form.get("sensor_name"))
                ip_address = _get_cleaned_data(request.form.get("ip_address"))
                program_version = _get_cleaned_data(request.form.get("program_version"))
                installed_sensors = _get_cleaned_data(request.form.get("installed_sensors"))
                sensor_uptime = _get_cleaned_data(request.form.get("sensor_uptime"))
                primary_log = _get_cleaned_data(request.form.get("primary_log"))
                network_log = _get_cleaned_data(request.form.get("network_log"))
                sensor_log = _get_cleaned_data(request.form.get("sensor_log"))

                sql_data = [datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"), sensor_name, ip_address, program_version,
                            installed_sensors, sensor_uptime, primary_log, network_log, sensor_log]
                write_to_sql_database(sql_ex_string, sql_data, sql_database_location=sc_database_location)
                return "OK", 202
            except Exception as error:
                logger.network_logger.warning("Sensor Checkin error for " + checkin_id + ": " + str(error))
        return "Failed", 400
    return "Checkin Recording Disabled", 202


def check_sensor_checkin_columns(checkin_id):
    db_connection = sqlite3.connect(sc_database_location)
    db_cursor = db_connection.cursor()

    create_table_and_datetime(checkin_id, db_cursor)
    check_sql_table_and_column(checkin_id, db_v.sensor_name, db_cursor)
    check_sql_table_and_column(checkin_id, db_v.ip, db_cursor)
    check_sql_table_and_column(checkin_id, db_v.sensor_check_in_version, db_cursor)
    check_sql_table_and_column(checkin_id, db_v.sensor_check_in_installed_sensors, db_cursor)
    check_sql_table_and_column(checkin_id, db_v.sensor_uptime, db_cursor)
    check_sql_table_and_column(checkin_id, db_v.sensor_check_in_primary_log, db_cursor)
    check_sql_table_and_column(checkin_id, db_v.sensor_check_in_network_log, db_cursor)
    check_sql_table_and_column(checkin_id, db_v.sensor_check_in_sensors_log, db_cursor)

    db_connection.commit()
    db_connection.close()


def _get_cleaned_data(data):
    if data == "" or data is None:
        return None
    return str(data).strip()
