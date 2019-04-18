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
from operations_modules import sensors
from operations_modules import configuration_main


class CreateIntervalDatabaseData:
    """ Creates a object, holding required data for making a Interval SQL execute string. """

    def __init__(self):
        self.database_location = file_locations.sensor_database_location
        self.sql_query_start = "INSERT OR IGNORE INTO IntervalData ("
        self.sql_query_values_start = ") VALUES ("
        self.sql_query_values_end = ")"

        self.sensor_types = ""
        self.sensor_readings = ""


class CreateTriggerDatabaseData:
    """ Creates a object, holding required data for making a Trigger SQL execute string. """

    def __init__(self):
        self.variance = 99999.99

        if configuration_main.installed_sensors.linux_system:
            self.sql_columns_str = "DateTime,SensorName,IP,"
        else:
            self.sql_columns_str = "DateTime,"

        self.sql_sensor_name = ""
        self.sql_ip = ""

        self.sql_query_start = "INSERT OR IGNORE INTO TriggerData ("
        self.sql_query_values_start = ") VALUES ("
        self.sql_query_values_end = ")"

        self.sql_readings1 = []
        self.sql_readings1_datetime = []

        self.sql_readings2 = []
        self.sql_readings2_datetime = []

    def get_sql_write_str(self):
        self._update_sql_name_and_ip()

        sql_execute_commands_list = []

        count = 0
        for reading in self.sql_readings1:
            if configuration_main.installed_sensors.linux_system:
                sql_execute_readings1 = "'" + self.sql_readings1_datetime[count] + "','" + \
                                        self.sql_sensor_name + "','" + self.sql_ip + "',"
                sql_execute_readings2 = "'" + self.sql_readings2_datetime[count] + "','" + \
                                        self.sql_sensor_name + "','" + self.sql_ip + "',"
            else:
                sql_execute_readings1 = "'" + self.sql_readings1_datetime[count] + "',"
                sql_execute_readings2 = "'" + self.sql_readings2_datetime[count] + "',"

            sql_execute_readings1 += "'" + str(reading) + "'"
            sql_execute_readings2 += "'" + str(self.sql_readings2[count]) + "'"
            count += 1

            sql_execute1 = (self.sql_query_start + self.sql_columns_str + self.sql_query_values_start +
                            sql_execute_readings1 + self.sql_query_values_end)

            sql_execute2 = (self.sql_query_start + self.sql_columns_str + self.sql_query_values_start +
                            sql_execute_readings2 + self.sql_query_values_end)

            sql_execute_commands_list.append(sql_execute1)
            sql_execute_commands_list.append(sql_execute2)

        return sql_execute_commands_list

    def _update_sql_name_and_ip(self):
        if configuration_main.installed_sensors.linux_system:
            self.sql_sensor_name = sensors.os_sensor_access.get_hostname()
            self.sql_ip = sensors.os_sensor_access.get_ip()


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
