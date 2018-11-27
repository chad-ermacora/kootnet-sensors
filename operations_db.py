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

import operations_logger
from operations_config import sensor_database_location


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


def check_database_structure():
    """ Checks and if necessary creates or updates both SQL tables and columns. """
    try:
        db_connection = sqlite3.connect(sensor_database_location)
        db_cursor = db_connection.cursor()

        # Create or update Interval table & columns
        try:
            db_cursor.execute('CREATE TABLE {tn} ({nf} {ft})'.format(tn='IntervalData',
                                                                     nf='DateTime',
                                                                     ft='TEXT'))
            operations_logger.primary_logger.debug("Table 'IntervalData' - Created")
        except Exception as error:
            operations_logger.primary_logger.debug("Table 'IntervalData' - " + str(error))

        try:
            db_cursor.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}".format(tn='IntervalData',
                                                                               cn='SensorName',
                                                                               ct='TEXT'))
            operations_logger.primary_logger.debug("COLUMN 'SensorName' - Created")
        except Exception as error:
            operations_logger.primary_logger.debug("COLUMN 'SensorName' - " + str(error))

        try:
            db_cursor.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}".format(tn='IntervalData',
                                                                               cn='IP',
                                                                               ct='TEXT'))
            operations_logger.primary_logger.debug("COLUMN 'IP' - Created")
        except Exception as error:
            operations_logger.primary_logger.debug("COLUMN 'IP' - " + str(error))

        try:
            db_cursor.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}".format(tn='IntervalData',
                                                                               cn='SensorUpTime',
                                                                               ct='TEXT'))
            operations_logger.primary_logger.debug("COLUMN 'SensorUpTime' - Created")
        except Exception as error:
            operations_logger.primary_logger.debug("COLUMN 'SensorUpTime' - " + str(error))

        try:
            db_cursor.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}".format(tn='IntervalData',
                                                                               cn='SystemTemp',
                                                                               ct='TEXT'))
            operations_logger.primary_logger.debug("COLUMN 'SystemTemp' -  Created")
        except Exception as error:
            operations_logger.primary_logger.debug("COLUMN 'SystemTemp' - " + str(error))

        try:
            db_cursor.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}".format(tn='IntervalData',
                                                                               cn='EnvironmentTemp',
                                                                               ct='TEXT'))
            operations_logger.primary_logger.debug("COLUMN 'EnvironmentTemp' - Created")
        except Exception as error:
            operations_logger.primary_logger.debug("COLUMN 'EnvironmentTemp' - " + str(error))

        try:
            db_cursor.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}".format(tn='IntervalData',
                                                                               cn='EnvTempOffset',
                                                                               ct='TEXT'))
            operations_logger.primary_logger.debug("COLUMN 'EnvTempOffset' - Created")
        except Exception as error:
            operations_logger.primary_logger.debug("COLUMN 'EnvTempOffset' - " + str(error))

        try:
            db_cursor.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}".format(tn='IntervalData',
                                                                               cn='Pressure',
                                                                               ct='TEXT'))
            operations_logger.primary_logger.debug("COLUMN 'Pressure' - Created")
        except Exception as error:
            operations_logger.primary_logger.debug("COLUMN 'Pressure' - " + str(error))

        try:
            db_cursor.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}".format(tn='IntervalData',
                                                                               cn='Humidity',
                                                                               ct='TEXT'))
            operations_logger.primary_logger.debug("COLUMN 'Humidity' - Created")
        except Exception as error:
            operations_logger.primary_logger.debug("COLUMN 'Humidity' - " + str(error))

        try:
            db_cursor.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}".format(tn='IntervalData',
                                                                               cn='Lumen',
                                                                               ct='TEXT'))
            operations_logger.primary_logger.debug("COLUMN 'Lumen' - Created")
        except Exception as error:
            operations_logger.primary_logger.debug("COLUMN 'Lumen' - " + str(error))

        try:
            db_cursor.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}".format(tn='IntervalData',
                                                                               cn='Red',
                                                                               ct='TEXT'))
            operations_logger.primary_logger.debug("COLUMN 'Red' - Created")
        except Exception as error:
            operations_logger.primary_logger.debug("COLUMN 'Red' - " + str(error))

        try:
            db_cursor.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}".format(tn='IntervalData',
                                                                               cn='Green',
                                                                               ct='TEXT'))
            operations_logger.primary_logger.debug("COLUMN 'Green' - Created")
        except Exception as error:
            operations_logger.primary_logger.debug("COLUMN 'Green' - " + str(error))

        try:
            db_cursor.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}".format(tn='IntervalData',
                                                                               cn='Blue',
                                                                               ct='TEXT'))
            operations_logger.primary_logger.debug("COLUMN 'Blue' - Created")
        except Exception as error:
            operations_logger.primary_logger.debug("COLUMN 'Blue' - " + str(error))

        # Create or update Trigger table & columns
        try:
            db_cursor.execute('CREATE TABLE {tn} ({nf} {ft})'.format(tn='TriggerData',
                                                                     nf='DateTime',
                                                                     ft='TEXT'))
            operations_logger.primary_logger.debug("Table 'TriggerData' - Created")
        except Exception as error:
            operations_logger.primary_logger.debug("Table 'TriggerData' - " + str(error))

        try:
            db_cursor.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}".format(tn='TriggerData',
                                                                               cn='SensorName',
                                                                               ct='TEXT'))
            operations_logger.primary_logger.debug("Column 'SensorName' - Created")
        except Exception as error:
            operations_logger.primary_logger.debug("Column 'SensorName' - " + str(error))

        try:
            db_cursor.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}".format(tn='TriggerData',
                                                                               cn='IP',
                                                                               ct='TEXT'))
            operations_logger.primary_logger.debug("Column 'IP' - Created")
        except Exception as error:
            operations_logger.primary_logger.debug("Column 'IP' - " + str(error))

        try:
            db_cursor.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}".format(tn='TriggerData',
                                                                               cn='Acc_X',
                                                                               ct='TEXT'))
            operations_logger.primary_logger.debug("Column 'acc_X' - Created")
        except Exception as error:
            operations_logger.primary_logger.debug("Column 'acc_X' - " + str(error))

        try:
            db_cursor.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}".format(tn='TriggerData',
                                                                               cn='Acc_Y',
                                                                               ct='TEXT'))
            operations_logger.primary_logger.debug("Column 'acc_Y' - Created")
        except Exception as error:
            operations_logger.primary_logger.debug("Column 'acc_Y' - " + str(error))

        try:
            db_cursor.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}".format(tn='TriggerData',
                                                                               cn='Acc_Z',
                                                                               ct='TEXT'))
            operations_logger.primary_logger.debug("Column 'acc_Z' - Created")
        except Exception as error:
            operations_logger.primary_logger.debug("Column 'acc_Z' - " + str(error))

        try:
            db_cursor.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}".format(tn='TriggerData',
                                                                               cn='Mag_X',
                                                                               ct='TEXT'))
            operations_logger.primary_logger.debug("COLUMN 'mg_X' - Created")
        except Exception as error:
            operations_logger.primary_logger.debug("COLUMN 'mg_X' - " + str(error))

        try:
            db_cursor.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}".format(tn='TriggerData',
                                                                               cn='Mag_Y',
                                                                               ct='TEXT'))
            operations_logger.primary_logger.debug("COLUMN 'mg_Y' - Created")
        except Exception as error:
            operations_logger.primary_logger.debug("COLUMN 'mg_Y' - " + str(error))

        try:
            db_cursor.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}".format(tn='TriggerData',
                                                                               cn='Mag_Z',
                                                                               ct='TEXT'))
            operations_logger.primary_logger.debug("COLUMN 'mg_Z' - Created")
        except Exception as error:
            operations_logger.primary_logger.debug("COLUMN 'mg_Z' - " + str(error))

        try:
            db_cursor.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}".format(tn='TriggerData',
                                                                               cn='Gyro_X',
                                                                               ct='TEXT'))
            operations_logger.primary_logger.debug("COLUMN 'Gyro_X' - Created")
        except Exception as error:
            operations_logger.primary_logger.debug("COLUMN 'Gyro_X' - " + str(error))

        try:
            db_cursor.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}".format(tn='TriggerData',
                                                                               cn='Gyro_Y',
                                                                               ct='TEXT'))
            operations_logger.primary_logger.debug("COLUMN 'Gyro_Y' - Created")
        except Exception as error:
            operations_logger.primary_logger.debug("COLUMN 'Gyro_Y' - " + str(error))

        try:
            db_cursor.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}".format(tn='TriggerData',
                                                                               cn='Gyro_Z',
                                                                               ct='TEXT'))
            operations_logger.primary_logger.debug("COLUMN 'Gyro_Z' - Created")
        except Exception as error:
            operations_logger.primary_logger.debug("COLUMN 'Gyro_Z' - " + str(error))

        # Create or update OtherData table & columns
        try:
            db_cursor.execute('CREATE TABLE {tn} ({nf} {ft})'.format(tn='OtherData',
                                                                     nf='DateTime',
                                                                     ft='TEXT'))
            operations_logger.primary_logger.debug("Table 'OtherData' - Created")
        except Exception as error:
            operations_logger.primary_logger.debug("Table 'OtherData' - " + str(error))

        try:
            db_cursor.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}".format(tn='OtherData',
                                                                               cn='Notes',
                                                                               ct='TEXT'))
            operations_logger.primary_logger.debug("COLUMN 'Notes' - Created")
        except Exception as error:
            operations_logger.primary_logger.debug("COLUMN 'Notes' - " + str(error))

        db_connection.commit()
        db_connection.close()
    except Exception as error:
        operations_logger.primary_logger.error("DB Connection Failed: " + str(error))


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
