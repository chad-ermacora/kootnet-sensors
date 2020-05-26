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
from flask import Blueprint, render_template, request
from operations_modules import logger
from operations_modules import file_locations
from operations_modules import app_cached_variables
from operations_modules import sqlite_database
from http_server.server_http_auth import auth
from http_server.server_http_generic_functions import get_html_hidden_state

html_basic_routes = Blueprint("html_basic_routes", __name__)


@html_basic_routes.route("/Quick")
@html_basic_routes.route("/SystemCommands")
@auth.login_required
def html_system_management():
    logger.network_logger.debug("** System Commands accessed from " + str(request.remote_addr))
    return render_template("system_commands.html",
                           PageURL="/SystemCommands",
                           RestartServiceHidden=get_html_hidden_state(app_cached_variables.html_service_restart),
                           RebootSensorHidden=get_html_hidden_state(app_cached_variables.html_sensor_reboot),
                           LoginUserName=app_cached_variables.http_flask_user)


@html_basic_routes.route("/SensorHelp")
def view_help_file():
    logger.network_logger.debug("* Sensor Help Viewed from " + str(request.remote_addr))
    return render_template("sensor_help_page.html")


@html_basic_routes.route("/SensorCheckin", methods=["POST"])
def remote_sensor_check_ins():
    if request.form.get("checkin_id"):
        checkin_id = str(request.form.get("checkin_id"))
        logger.network_logger.debug("* Sensor ID:" + checkin_id + " checked in from " + str(request.remote_addr))

        current_datetime = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        all_tables_datetime = app_cached_variables.database_variables.all_tables_datetime
        sensor_check_in_version = app_cached_variables.database_variables.sensor_check_in_version
        sensor_check_in_primary_log = app_cached_variables.database_variables.sensor_check_in_primary_log
        sensor_check_in_sensors_log = app_cached_variables.database_variables.sensor_check_in_sensors_log
        try:
            db_connection = sqlite3.connect(file_locations.sensor_checkin_database)
            db_cursor = db_connection.cursor()

            sqlite_database.create_table_and_datetime(checkin_id, db_cursor)
            sqlite_database.check_sql_table_and_column(checkin_id, sensor_check_in_version, db_cursor)
            sqlite_database.check_sql_table_and_column(checkin_id, sensor_check_in_primary_log, db_cursor)
            sqlite_database.check_sql_table_and_column(checkin_id, sensor_check_in_sensors_log, db_cursor)

            sql_ex_string = "INSERT OR IGNORE INTO '{CheckinIDTable}' " + \
                            "({DateTimeColumn},{KootnetVersionColumn},{PrimaryLogColumn},{SensorLogColumn})" + \
                            " VALUES ('{CurrentDateTime}','{KootnetVersion}','{PrimaryLog}','{SensorLog}')"
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
        except Exception as error:
            logger.network_logger.debug("Sensor Checkin error: " + str(error))


@html_basic_routes.route("/ViewSensorCheckin")
@auth.login_required
def view_sensor_check_ins():
    try:
        get_sql = "SELECT count(*) FROM sqlite_master WHERE type = 'table' " + \
                  "AND name != 'android_metadata' AND name != 'sqlite_sequence';"
        location = file_locations.sensor_checkin_database
        sensor_count = str(sqlite_database.sql_execute_get_data(get_sql, sql_database_location=location)[0][0])
    except Exception as error:
        print(str(error))
        sensor_count = "Error"
    return render_template("software_checkin.html",
                           PageURL="/ViewSensorCheckin",
                           RestartServiceHidden=get_html_hidden_state(app_cached_variables.html_service_restart),
                           RebootSensorHidden=get_html_hidden_state(app_cached_variables.html_sensor_reboot),
                           SensorsInDatabase=sensor_count)
