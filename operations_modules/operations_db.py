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

from operations_modules import operations_sensors
from operations_modules import operations_logger
import operations_modules.operations_file_locations as file_locations


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

    def __init__(self, installed_sensors):
        self.installed_sensors = installed_sensors
        self.variance = 99999.99

        if installed_sensors.linux_system:
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
            if self.installed_sensors.linux_system:
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
        if self.installed_sensors.linux_system:
            self.sql_sensor_name = operations_sensors.os_sensor_access.get_hostname()
            self.sql_ip = operations_sensors.os_sensor_access.get_ip()


class CreateOtherDataEntry:
    """ Creates a object, holding required data for making a OtherData SQL execute string. """

    def __init__(self):
        self.database_location = file_locations.sensor_database_location
        self.sql_query_start = "INSERT OR IGNORE INTO OtherData ("
        self.sql_query_values_start = ") VALUES ("
        self.sql_query_values_end = ")"

        self.sensor_types = ""
        self.sensor_readings = ""


class CreateDatabaseVariables:
    def __init__(self):
        self.table_interval = "IntervalData"
        self.table_trigger = "TriggerData"
        self.table_other = "OtherData"

        self.other_table_column_user_date_time = "UserDateTime"
        self.other_table_column_notes = "Notes"

        self.sensor_name = "SensorName"
        self.ip = "IP"
        self.sensor_uptime = "SensorUpTime"
        self.system_temperature = "SystemTemp"
        self.env_temperature = "EnvironmentTemp"
        self.env_temperature_offset = "EnvTempOffset"
        self.pressure = "Pressure"
        self.humidity = "Humidity"
        self.lumen = "Lumen"
        self.red = "Red"
        self.orange = "Orange"
        self.yellow = "Yellow"
        self.green = "Green"
        self.blue = "Blue"
        self.violet = "Violet"
        self.acc_x = "Acc_X"
        self.acc_y = "Acc_Y"
        self.acc_z = "Acc_Z"
        self.mag_x = "Mag_X"
        self.mag_y = "Mag_Y"
        self.mag_z = "Mag_Z"
        self.gyro_x = "Gyro_X"
        self.gyro_y = "Gyro_Y"
        self.gyro_z = "Gyro_Z"

    def get_sensor_columns_list(self):
        sensor_sql_columns = [self.sensor_name,
                              self.ip,
                              self.sensor_uptime,
                              self.system_temperature,
                              self.env_temperature,
                              self.env_temperature_offset,
                              self.pressure,
                              self.humidity,
                              self.lumen,
                              self.red,
                              self.orange,
                              self.yellow,
                              self.green,
                              self.blue,
                              self.violet,
                              self.acc_x,
                              self.acc_y,
                              self.acc_z,
                              self.mag_x,
                              self.mag_y,
                              self.mag_z,
                              self.gyro_x,
                              self.gyro_y,
                              self.gyro_z]
        return sensor_sql_columns

    def get_other_columns_list(self):
        other_sql_columns = [self.other_table_column_user_date_time,
                             self.other_table_column_notes]
        return other_sql_columns


def write_to_sql_database(sql_execute):
    """ Executes provided string with SQLite3.  Used to write sensor readings to the SQL Database. """
    operations_logger.primary_logger.debug("SQL String to execute: " + str(sql_execute))

    try:
        db_connection = sqlite3.connect(file_locations.sensor_database_location)
        db_cursor = db_connection.cursor()
        db_cursor.execute(sql_execute)
        db_connection.commit()
        db_connection.close()
        operations_logger.primary_logger.debug("SQL Write to DataBase OK - " + file_locations.sensor_database_location)
    except Exception as error:
        operations_logger.primary_logger.error("SQL Write to DataBase Failed - " + str(error))
