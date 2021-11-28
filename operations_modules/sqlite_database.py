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
from operations_modules.app_cached_variables import database_variables as db_v
from operations_modules.app_generic_functions import adjust_datetime
from configuration_modules.app_config_access import primary_config


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


def write_to_sql_database(sql_query, data_entries, sql_database_location=file_locations.sensor_database):
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
        logger.primary_logger.debug("SQL Write to DataBase OK - " + sql_database_location)
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
        if str(error)[:13] == "no such table":
            logger.primary_logger.debug("SQL Table name was not found in the Database: " + str(error))
        elif str(error)[:14] == "no such column":
            logger.primary_logger.debug("SQL Column name was not found in the Database: " + str(error))
        else:
            logger.primary_logger.warning("SQL Execute Get Data Error: " + str(error))
        return []
    return sql_column_data


def universal_database_structure_check(database_location, expected_database_type=None):
    """
    Returns validated database type from the database itself, else, returns False
    :param expected_database_type: Optional: Check to make sure it's the correct Type of Database
    :param database_location: Location of Database
    :return: If found and validated, Database type as string, else, False
    """
    try:
        sql_query = "SELECT " + db_v.db_info_database_type_column + " FROM '" + db_v.table_db_info + "' WHERE " \
                    + db_v.db_info_database_type_column + " != ''"
        database_type = get_sql_element(sql_execute_get_data(sql_query, sql_database_location=database_location))
        if expected_database_type is None:
            expected_database_type = database_type

        logger.primary_logger.debug("Database Type for " + database_location + ": " + str(database_type))
        if expected_database_type != database_type:
            log_msg = "Database Structure Check Failed: Expected Database Type '" + expected_database_type
            logger.network_logger.warning(log_msg + "' not '" + str(database_type) + "'")
            return False

        if database_type == db_v.db_info_database_type_main:
            check_main_database_structure(database_location)
        elif database_type == db_v.db_info_database_type_sensor_checkins:
            check_checkin_database_structure(database_location)
        elif database_type == db_v.db_info_database_type_mqtt:
            check_mqtt_subscriber_database_structure(database_location)
        else:
            log_msg = "Database Structure Check Failed - Unknown Database type for " + database_type
            logger.network_logger.warning(log_msg)
            return False
        return database_type
    except Exception as error:
        logger.network_logger.error("Database Structure Check Failed: " + str(error))
    return False


def check_main_database_structure(database_location=file_locations.sensor_database):
    """ Loads or creates the SQLite database then verifies or adds all tables and columns. """
    logger.primary_logger.debug("Running Checks on Main Database")
    columns_created = 0
    columns_already_made = 0
    try:
        db_connection = sqlite3.connect(database_location)
        db_cursor = db_connection.cursor()

        create_ks_db_info_table(db_v.db_info_database_type_main, db_cursor)
        create_table_and_datetime(db_v.table_interval, db_cursor)
        create_table_and_datetime(db_v.table_trigger, db_cursor)
        for column in db_v.get_sensor_columns_list():
            interval_response = check_sql_table_and_column(db_v.table_interval, column, db_cursor)
            trigger_response = check_sql_table_and_column(db_v.table_trigger, column, db_cursor)
            for response in [interval_response, trigger_response]:
                if response:
                    columns_created += 1
                else:
                    columns_already_made += 1
        if check_sql_table_and_column(db_v.table_trigger, db_v.trigger_state, db_cursor):
            columns_created += 1
        else:
            columns_already_made += 1

        create_table_and_datetime(db_v.table_other, db_cursor)
        for column_other in db_v.get_other_columns_list():
            other_response = check_sql_table_and_column(db_v.table_other, column_other, db_cursor)
            if other_response:
                columns_created += 1
            else:
                columns_already_made += 1

        db_connection.commit()
        db_connection.close()
        debug_log_message = str(columns_already_made) + " Columns found in 3 SQL Tables, "
        logger.primary_logger.debug(debug_log_message + str(columns_created) + " Created")
        logger.primary_logger.debug("Checks on Main Database Complete")
        return True
    except Exception as error:
        logger.primary_logger.error("Checks on Main Database Failed: " + str(error))
    return False


def check_checkin_database_structure(database_location=file_locations.sensor_checkin_database):
    logger.primary_logger.debug("Running Check on 'Checkin' Database")
    try:
        db_connection = sqlite3.connect(database_location)
        db_cursor = db_connection.cursor()

        create_ks_db_info_table(db_v.db_info_database_type_sensor_checkins, db_cursor)
        get_sensor_checkin_ids_sql = "SELECT name FROM sqlite_master WHERE type='table';"
        sensor_ids = sql_execute_get_data(get_sensor_checkin_ids_sql, sql_database_location=database_location)

        columns = [db_v.kootnet_sensors_version,
                   db_v.sensor_uptime,
                   db_v.sensor_check_in_installed_sensors,
                   db_v.sensor_check_in_primary_log,
                   db_v.sensor_check_in_sensors_log]
        for sensor_id in sensor_ids:
            cleaned_id = str(sensor_id[0]).strip()
            if not _ks_system_table(cleaned_id):
                for column in columns:
                    try:
                        add_columns_sql = "ALTER TABLE '" + cleaned_id + "' ADD COLUMN " + column + " TEXT"
                        db_cursor.execute(add_columns_sql)
                    except Exception as error:
                        if str(error)[:21] != "duplicate column name":
                            logger.primary_logger.error("Checkin Database Error: " + str(error))
        db_connection.commit()
        db_connection.close()
        logger.primary_logger.debug("Check on 'Checkin' Database Complete")
        return True
    except Exception as error:
        logger.primary_logger.error("Checks on 'Checkin' Database Failed: " + str(error))
    return False


def check_mqtt_subscriber_database_structure(database_location=file_locations.mqtt_subscriber_database):
    logger.primary_logger.debug("Running Check on 'MQTT Subscriber' Database")
    try:
        db_connection = sqlite3.connect(database_location)
        db_cursor = db_connection.cursor()

        create_ks_db_info_table(db_v.db_info_database_type_mqtt, db_cursor)
        get_sensor_checkin_ids_sql = "SELECT name FROM sqlite_master WHERE type='table';"
        mqtt_sensor_strings = sql_execute_get_data(get_sensor_checkin_ids_sql, sql_database_location=database_location)

        for sensor_string in mqtt_sensor_strings:
            cleaned_id = str(sensor_string[0]).strip()
            if not _ks_system_table(cleaned_id):
                for column in db_v.get_sensor_columns_list():
                    try:
                        add_columns_sql = "ALTER TABLE '" + cleaned_id + "' ADD COLUMN " + column + " TEXT"
                        db_cursor.execute(add_columns_sql)
                    except Exception as error:
                        if str(error)[:21] != "duplicate column name":
                            logger.primary_logger.error("Checkin Database Error: " + str(error))
        db_connection.commit()
        db_connection.close()
        logger.primary_logger.debug("Check on 'Checkin' Database Complete")
        return True
    except Exception as error:
        logger.primary_logger.error("Checks on 'Checkin' Database Failed: " + str(error))
    return False


def create_table_and_datetime(table_name, db_cursor):
    """ Adds or verifies provided table and DateTime column in the SQLite Database. """
    table_name = get_clean_sql_table_name(table_name)
    try:
        # Create or update table
        db_cursor.execute("CREATE TABLE {tn} ({nf} {ft})".format(tn=table_name, nf=db_v.all_tables_datetime, ft="TEXT"))
        logger.primary_logger.debug("Table '" + table_name + "' - Created")
    except Exception as error:
        logger.primary_logger.debug("SQLite3 Table Check/Creation: " + str(error))


def create_ks_db_info_table(db_type, db_cursor):
    try:
        db_cursor.execute("CREATE TABLE {tn} ({cn} {ct})".format(
            tn=db_v.table_db_info, cn=db_v.db_info_database_type_column, ct="TEXT"
        ))

        sql_execute = "INSERT OR IGNORE INTO " + db_v.table_db_info + \
                      " ('" + db_v.db_info_database_type_column + "') VALUES ('" + db_type + "');"
        db_cursor.execute(sql_execute)
        logger.primary_logger.debug("Table KS DB Info - Created")
    except Exception as error:
        logger.primary_logger.debug("SQLite3 KS DB Info Table Check/Creation: " + str(error))


def check_sql_table_and_column(table_name, column_name, db_cursor, column_type="TEXT"):
    """ Adds or verifies provided table and column in the SQLite Database. """
    table_name = get_clean_sql_table_name(table_name)
    try:
        sql_query = "ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}"
        db_cursor.execute(sql_query.format(tn=table_name, cn=column_name, ct=column_type))
        return True
    except Exception as error:
        if str(error)[:21] != "duplicate column name":
            logger.primary_logger.warning("SQLite3 Column Check Error: " + str(error))
    return False


def validate_sqlite_database(database_location, check_for_table=None):
    """
    If SQLite3 database at provided location is valid, returns True, otherwise False.
    Optional: Add a specific table to look for as a string with check_for_table.
    """
    get_sql_tables = "SELECT name FROM sqlite_master WHERE type='table';"

    if check_for_table is not None:
        get_sql_tables = get_sql_tables[:-1] + " AND name='" + check_for_table + "';"

    sql_db_tables = sql_execute_get_data(get_sql_tables, sql_database_location=database_location)

    if len(sql_db_tables) > 0:
        return True
    return False


def run_database_integrity_check(sqlite_database_location, quick=True):
    try:
        db_connection = sqlite3.connect(sqlite_database_location)
        db_cursor = db_connection.cursor()

        if quick:
            integrity_check_fetch = db_cursor.execute("PRAGMA quick_check;").fetchall()
        else:
            integrity_check_fetch = db_cursor.execute("PRAGMA integrity_check;").fetchall()

        db_connection.commit()
        db_connection.close()

        log_msg1 = " - Full Integrity Check ran on "
        if quick:
            log_msg1 = " - Quick Integrity Check ran on "
        integrity_msg = sql_fetch_items_to_text(integrity_check_fetch)
        logger.primary_logger.info(log_msg1 + sqlite_database_location + ": " + integrity_msg)
    except Exception as error:
        log_msg = "SQLite3 Database Integrity Check Error on " + sqlite_database_location + ": "
        logger.primary_logger.error(log_msg + str(error))


def get_sqlite_tables_in_list(database_location):
    """ Returns a list of SQLite3 database table names. """
    get_sqlite_tables_query = "SELECT name FROM sqlite_master WHERE type='table';"
    sqlite_tables_list = sql_execute_get_data(get_sqlite_tables_query, sql_database_location=database_location)
    final_list = []
    for entry in sqlite_tables_list:
        entry = get_sql_element(entry)
        if not _ks_system_table(entry):
            final_list.append(entry)
    return final_list


def get_one_db_entry(table_name, column_name, order="DESC", database=file_locations.sensor_database):
    """
    Returns the last entry from the provided column in the provided table. Skips blank and null entries.

    Default Options: order="DESC", database=file_locations.sensor_database.
    """
    sql_query = "SELECT " + column_name + " FROM '" + table_name + "' WHERE " \
                + column_name + " != '' ORDER BY " + db_v.all_tables_datetime + " " + order + " LIMIT 1;"
    return get_sql_element(sql_execute_get_data(sql_query, sql_database_location=database))


def get_main_db_first_last_date():
    """ Returns First and Last recorded date in the SQL Database as a String. """
    sql_query = "SELECT Min(" + str(db_v.all_tables_datetime) + ") AS First, " + \
                "Max(" + str(db_v.all_tables_datetime) + ") AS Last " + \
                "FROM " + str(db_v.table_interval)

    textbox_db_dates = "Database Access Error: "
    try:
        first_date, last_date = sql_execute_get_data(sql_query)[0]
        first_date = adjust_datetime(first_date, primary_config.utc0_hour_offset)
        last_date = adjust_datetime(last_date, primary_config.utc0_hour_offset)
        textbox_db_dates = str(first_date) + " < -- > " + str(last_date)
    except Exception as error:
        logger.primary_logger.error("Get First & Last DateTime from Interval Recording DB Failed: " + str(error))
        textbox_db_dates += str(error)
    return textbox_db_dates


def get_sql_element(sql_data):
    try:
        for entry1 in sql_data:
            if type(entry1) is list or type(entry1) is tuple:
                for entry2 in entry1:
                    return str(entry2)
            else:
                return str(entry1)
    except Exception as error:
        logger.network_logger.debug("Error extracting data in Sensor Check-ins: " + str(error))
        return "Error"
    return ""


def sql_fetch_items_to_text(sql_query_results):
    return_msg = ""
    for item in sql_query_results:
        for item2 in item:
            return_msg += str(item2) + " | "
    if len(return_msg) > 3:
        return_msg = return_msg[:-3]
    return return_msg


def get_clean_sql_table_name(sql_table):
    sql_table = str(sql_table).strip()
    if sql_table[0].isdigit():
        sql_table = "KS" + sql_table
    if not sql_table.isalnum():
        new_sql_table = ""
        for character in sql_table:
            if character.isalnum():
                new_sql_table += character
        sql_table = new_sql_table
    return sql_table


def _ks_system_table(table_name):
    if table_name == db_v.table_db_info or table_name == db_v.table_ks_info:
        return True
    return False
