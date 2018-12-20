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

from operations_modules import operations_logger
from operations_modules.operations_config import sensor_database_location


class CreateIntervalDatabaseData:
    """ Creates a object, holding required data for making a Interval SQL execute string. """

    def __init__(self):
        self.database_location = sensor_database_location
        self.sql_query_start = "INSERT OR IGNORE INTO IntervalData ("
        self.sql_query_values_start = ") VALUES ("
        self.sql_query_values_end = ")"

        self.sensor_types = ""
        self.sensor_readings = ""


class CreateTriggerDatabaseData:
    """ Creates a object, holding required data for making a Trigger SQL execute string. """

    def __init__(self):
        self.database_location = sensor_database_location
        self.sql_query_start = "INSERT OR IGNORE INTO TriggerData ("
        self.sql_query_values_start = ") VALUES ("
        self.sql_query_values_end = ")"

        self.sensor_types = ""
        self.sensor_readings = ""


class CreateOtherDataEntry:
    """ Creates a object, holding required data for making a OtherData SQL execute string. """

    def __init__(self):
        self.database_location = sensor_database_location
        self.sql_query_start = "INSERT OR IGNORE INTO OtherData ("
        self.sql_query_values_start = ") VALUES ("
        self.sql_query_values_end = ")"

        self.sensor_types = ""
        self.sensor_readings = ""


def write_to_sql_database(sql_execute):
    """ Executes provided string with SQLite3.  Used to write sensor readings to the SQL Database. """
    operations_logger.primary_logger.debug("SQL String to execute: " + str(sql_execute))

    try:
        db_connection = sqlite3.connect(sensor_database_location)
        db_cursor = db_connection.cursor()
        db_cursor.execute(sql_execute)
        db_connection.commit()
        db_connection.close()
        operations_logger.primary_logger.debug("SQL Write to DataBase - OK - " + sensor_database_location)
    except Exception as error:
        operations_logger.primary_logger.error("SQL Write to DataBase - Failed - " + str(error))
