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


class CreateIntervalDatabaseData:
    """ Creates a object, holding required data for making a Interval SQL execute string. """

    def __init__(self):
        self.database_location = file_locations.sensor_database_location
        self.sql_query_start = "INSERT OR IGNORE INTO IntervalData ("
        self.sql_query_values_start = ") VALUES ("
        self.sql_query_values_end = ")"

        self.sensor_types = ""
        self.sensor_readings = ""


class CreateOtherDataEntry:
    """ Creates a object, holding required data for making a OtherData SQL execute string. """

    def __init__(self):
        self.database_location = file_locations.sensor_database_location
        self.sql_query_start = "INSERT OR IGNORE INTO OtherData ("
        self.sql_query_values_start = ") VALUES ("
        self.sql_query_values_end = ")"

        self.sensor_types = ""
        self.sensor_readings = ""


def write_to_sql_database(sql_query):
    """ Executes provided string with SQLite3.  Used to write sensor readings to the SQL Database. """
    logger.primary_logger.debug("SQL String to execute: " + str(sql_query))

    try:
        db_connection = sqlite3.connect(file_locations.sensor_database_location)
        db_cursor = db_connection.cursor()
        db_cursor.execute(sql_query)
        db_connection.commit()
        db_connection.close()
        logger.primary_logger.debug("SQL Write to DataBase OK - " + file_locations.sensor_database_location)
    except Exception as error:
        logger.primary_logger.error("SQL Write to DataBase Failed - " + str(error))


def sql_execute_get_data(sql_query):
    try:
        database_connection = sqlite3.connect(file_locations.sensor_database_location)
        sqlite_database = database_connection.cursor()
        sqlite_database.execute(sql_query)
        sql_column_data = sqlite_database.fetchall()
        sqlite_database.close()
        database_connection.close()
    except Exception as error:
        logger.primary_logger.error("SQL Execute Get Data Error: " + str(error))
        sql_column_data = []

    return sql_column_data


def sql_execute(sql_query):
    try:
        database_connection = sqlite3.connect(file_locations.sensor_database_location)
        sqlite_database = database_connection.cursor()
        sqlite_database.execute(sql_query)
        database_connection.commit()
        sqlite_database.close()
        database_connection.close()
    except Exception as error:
        logger.primary_logger.error("SQL Execute Error: " + str(error))
