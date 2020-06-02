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
from operations_modules import file_locations
from operations_modules import logger
from operations_modules.app_cached_variables import database_variables


class CreateOtherDataEntry:
    """ Creates a object, holding required data for making a 'OtherData' SQL execute string. """

    def __init__(self):
        self.database_location = file_locations.sensor_database
        self.sql_query_start = "INSERT OR IGNORE INTO OtherData ("
        self.sql_query_values_start = ") VALUES ("
        self.sql_query_values_end = ")"
        self.sensor_types = ""
        self.sensor_readings = ""

    def get_sql_execute_string(self):
        return self.sql_query_start + self.sensor_types + self.sql_query_values_start + \
               self.sensor_readings + self.sql_query_values_end


def write_to_sql_database(sql_query, data_entries,
                          sql_database_location=file_locations.sensor_database):
    """ Executes provided string with SQLite3.  Used to write sensor readings to the SQL Database. """
    try:
        db_connection = sqlite3.connect(sql_database_location)
        db_cursor = db_connection.cursor()
        if data_entries is None:
            db_cursor.execute(sql_query)
        else:
            db_cursor.execute(sql_query, data_entries)
        db_connection.commit()
        db_connection.close()
        logger.primary_logger.debug("SQL Write to DataBase OK - " + file_locations.sensor_database)
    except Exception as error:
        logger.primary_logger.error("SQL Write to DataBase Failed - " + str(error))
        logger.primary_logger.debug("Bad SQL Write String: " + str(sql_query))


def sql_execute_get_data(sql_query, sql_database_location=file_locations.sensor_database):
    """ Returns SQL data based on provided sql_query. """
    try:
        database_connection = sqlite3.connect(sql_database_location)
        sqlite_database = database_connection.cursor()
        sqlite_database.execute(sql_query)
        sql_column_data = sqlite_database.fetchall()
        database_connection.close()
    except Exception as error:
        logger.primary_logger.warning("SQL Execute Get Data Error: " + str(error))
        sql_column_data = []
    return sql_column_data


def check_checkin_database_structure(database_location=file_locations.sensor_checkin_database):
    logger.primary_logger.debug("Running Check on 'Checkin' Database")
    columns_created = 0
    columns_already_made = 0

    try:
        db_connection = sqlite3.connect(database_location)
        db_cursor = db_connection.cursor()

        get_sensor_checkin_ids_sql = "SELECT name FROM sqlite_master WHERE type='table';"
        sensor_ids = sql_execute_get_data(get_sensor_checkin_ids_sql, sql_database_location=database_location)

        sensor_check_in_version = database_variables.sensor_check_in_version
        sensor_check_in_primary_log = database_variables.sensor_check_in_primary_log
        sensor_check_in_sensors_log = database_variables.sensor_check_in_sensors_log
        sensor_uptime = database_variables.sensor_uptime

        for sensor_id in sensor_ids:
            cleaned_id = str(sensor_id[0]).strip()
            if check_sql_table_and_column(cleaned_id, sensor_check_in_version, db_cursor):
                columns_created += 1
            else:
                columns_already_made += 1
            if check_sql_table_and_column(cleaned_id, sensor_uptime, db_cursor):
                columns_created += 1
            else:
                columns_already_made += 1
            if check_sql_table_and_column(cleaned_id, sensor_check_in_primary_log, db_cursor):
                columns_created += 1
            else:
                columns_already_made += 1
            if check_sql_table_and_column(cleaned_id, sensor_check_in_sensors_log, db_cursor):
                columns_created += 1
            else:
                columns_already_made += 1

        db_connection.commit()
        db_connection.close()
        debug_log_message = str(columns_already_made) + " Columns found in SQL Tables, "
        logger.primary_logger.debug(debug_log_message + str(columns_created) + " Created")
        write_to_sql_database("VACUUM;", None, sql_database_location=file_locations.sensor_checkin_database)
        return True
    except Exception as error:
        logger.primary_logger.error("Checks on Check-in Database Failed: " + str(error))
        return False


def check_main_database_structure(database_location=file_locations.sensor_database):
    """ Loads or creates the SQLite database then verifies or adds all tables and columns. """
    logger.primary_logger.debug("Running Checks on Main Database")

    columns_created = 0
    columns_already_made = 0

    try:
        db_connection = sqlite3.connect(database_location)
        db_cursor = db_connection.cursor()

        create_table_and_datetime(database_variables.table_interval, db_cursor)
        create_table_and_datetime(database_variables.table_trigger, db_cursor)
        for column_intervals, column_trigger in zip(database_variables.get_sensor_columns_list(),
                                                    database_variables.get_sensor_columns_list()):
            interval_response = check_sql_table_and_column(database_variables.table_interval, column_intervals,
                                                           db_cursor)
            trigger_response = check_sql_table_and_column(database_variables.table_trigger, column_trigger, db_cursor)
            if interval_response:
                columns_created += 1
            else:
                columns_already_made += 1
            if trigger_response:
                columns_created += 1
            else:
                columns_already_made += 1

        create_table_and_datetime(database_variables.table_other, db_cursor)
        for column_other in database_variables.get_other_columns_list():
            other_response = check_sql_table_and_column(database_variables.table_other, column_other, db_cursor)
            if other_response:
                columns_created += 1
            else:
                columns_already_made += 1

        db_connection.commit()
        db_connection.close()
        debug_log_message = str(columns_already_made) + " Columns found in 3 SQL Tables, "
        logger.primary_logger.debug(debug_log_message + str(columns_created) + " Created")
        write_to_sql_database("VACUUM;", None, sql_database_location=file_locations.sensor_database)
        return True
    except Exception as error:
        logger.primary_logger.error("Checks on Main Database Failed: " + str(error))
        return False


def create_table_and_datetime(table, db_cursor):
    """ Add's or verifies provided table and DateTime column in the SQLite Database. """
    try:
        # Create or update table
        db_cursor.execute("CREATE TABLE {tn} ({nf} {ft})".format(tn=table, nf="DateTime", ft="TEXT"))
        logger.primary_logger.debug("Table '" + table + "' - Created")
    except Exception as error:
        logger.primary_logger.debug("SQLite3 Table Check/Creation: " + str(error))


def check_sql_table_and_column(table_name, column_name, db_cursor):
    """ Add's or verifies provided table and column in the SQLite Database. """
    try:
        db_cursor.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}".format(tn=table_name, cn=column_name, ct="TEXT"))
        return True
    except Exception as error:
        if str(error)[:21] != "duplicate column name":
            logger.primary_logger.warning("SQLite3 Column Check Error: " + str(error))
    return False


def validate_sqlite_database(database_location):
    table_to_check = database_variables.table_interval
    sql_table_check_query = "SELECT name FROM sqlite_master WHERE type='table' AND name='" + table_to_check + "';"
    try:
        database_connection = sqlite3.connect(database_location)
        db_cursor = database_connection.cursor()
        db_cursor.execute(sql_table_check_query)
        db_return = db_cursor.fetchone()[0]
        database_connection.close()
        if db_return:
            return True
    except Exception as error:
        logger.primary_logger.error("Database Check: " + str(error))
    return False
