"""
This module is for the Raspberry Pi System
It Retrieves System & Sensor data

Tested on the RP3B+ & RPWZ

Created on Sat Aug 25 08:53:56 2018

@author: OO-Dragon
"""
import os
import socket
from time import strftime
from operations_modules import logger
from operations_modules import file_locations
from operations_modules import sqlite_database
from operations_modules.sqlite_database import CreateDatabaseVariables

round_decimal_to = 2


class CreateLinuxSystem:
    """ Creates Function access to Linux System Information. """

    def __init__(self):
        self.database_variables = CreateDatabaseVariables()

    @staticmethod
    def os_version():
        """ Returns System OS Version as a String. """
        try:
            system_os_information = open("/etc/os-release", "r")
            os_version = system_os_information.readline()
            system_os_information.close()
            return str(os_version)[13:-2]
        except Exception as error:
            logger.sensors_logger.error("Unable to get Raspberry model: " + str(error))
            return "Error retrieving OS information"

    @staticmethod
    def get_hostname():
        """ Returns System HostName as a String. """
        try:
            hostname = str(socket.gethostname())
            logger.sensors_logger.debug("Linux System Sensor Name - OK")
        except Exception as error:
            logger.sensors_logger.error("Linux System Sensor Name - Failed - " + str(error))
            hostname = "HostFailed"
        return hostname

    @staticmethod
    def get_ip():
        """ Returns IPv4 Address as a String. """
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip_address = (s.getsockname()[0])
            s.close()
            logger.sensors_logger.debug("Linux System Sensor IP - OK")
        except Exception as error:
            logger.sensors_logger.warning("Linux System Sensor IP - Failed - " + str(error))
            ip_address = "0.0.0.0"
        return ip_address

    @staticmethod
    def get_uptime():
        """ Returns System Uptime in minutes as a Integer. """
        try:
            with open('/proc/uptime', 'r') as f:
                uptime_seconds = float(f.readline().split()[0])
                uptime_min = int(uptime_seconds / 60)
            logger.sensors_logger.debug("Linux System Sensor Up Time - OK")
        except Exception as error:
            logger.sensors_logger.error("Linux System Sensor Up Time - Failed - " + str(error))
            uptime_min = 0

        return uptime_min

    @staticmethod
    def get_sys_datetime_str():
        """ Returns System DateTime in format YYYY-MM-DD HH:MM as a String. """
        logger.sensors_logger.debug("Linux System Sensor Date Time - OK")
        return strftime("%Y-%m-%d %H:%M")

    @staticmethod
    def get_sql_db_size():
        """ Returns Sensor SQLite DB Size in MB as a Float. """
        try:
            db_size_mb = os.path.getsize(file_locations.sensor_database_location) / 1024000
            logger.sensors_logger.debug("Linux System Interval Database Size - OK")
        except Exception as error:
            logger.sensors_logger.error("Linux System Interval Database Size - Failed - " + str(error))
            db_size_mb = 0.0
        return round(db_size_mb, round_decimal_to)

    def get_db_notes_count(self):
        sql_query = "SELECT count(" + \
                    str(self.database_variables.other_table_column_notes) + \
                    ") FROM " + \
                    str(self.database_variables.table_other)

        number_of_notes = str(sqlite_database.sql_execute_get_data(sql_query))

        if len(number_of_notes) > 5:
            return_notes_count = number_of_notes[2:-3]
        else:
            logger.sensors_logger.error("Unable to get SQLite Database Notes count")
            return_notes_count = "Error"

        return return_notes_count

    def get_db_first_last_date(self):
        sql_query = "SELECT Min(" + \
                    str(self.database_variables.all_tables_datetime) + \
                    ") AS First, Max(" + \
                    str(self.database_variables.all_tables_datetime) + \
                    ") AS Last FROM " + \
                    str(self.database_variables.table_interval)

        db_datetime_column = str(sqlite_database.sql_execute_get_data(sql_query))

        try:
            db_datetime_column_list = db_datetime_column.split(",")
        except Exception as error:
            logger.sensors_logger.error("Database get First & Last DateTime - Failed - " + str(error))
            db_datetime_column_list = ["---Error--", "--Error----"]

        if len(db_datetime_column_list) == 2:
            textbox_db_dates = db_datetime_column_list[0][3:-5] + " || " + db_datetime_column_list[1][2:-7]
        else:
            textbox_db_dates = "DataBase Error"

        return textbox_db_dates

    def get_sensor_reboot_count(self):
        sql_query = "SELECT " + \
                    str(self.database_variables.sensor_uptime) + \
                    " FROM " + \
                    str(self.database_variables.table_interval) + \
                    " WHERE length(" + \
                    str(self.database_variables.sensor_uptime) + \
                    ") < 2"

        sql_column_data = sqlite_database.sql_execute_get_data(sql_query)

        reboot_count = 0
        previous_entry = 0
        bad_entries = 0
        for entry in sql_column_data:
            try:
                entry_int = int(str(entry)[2:-3])
            except Exception as error:
                print("Bad SQL Entry in System Uptime column: " + str(entry) + " : " + str(error))
                bad_entries += 1
                entry_int = previous_entry

            if entry_int < previous_entry:
                reboot_count += 1
                previous_entry = entry_int
            else:
                previous_entry = entry_int

        if bad_entries:
            logger.sensors_logger.warning(str(bad_entries) + " bad entries in DB reboot column")

        logger.sensors_logger.debug(str(len(sql_column_data)) + " entries in DB reboot column retrieved")
        return str(reboot_count)
