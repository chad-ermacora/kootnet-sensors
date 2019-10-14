"""
This module is for the Raspberry Pi System
It Retrieves System & Sensor data

Tested on the RP3B+ & RPWZ

Created on Sat Aug 25 08:53:56 2018

@author: OO-Dragon
"""
import os
import socket
import psutil
from time import strftime
from operations_modules import logger
from operations_modules import file_locations
from operations_modules import app_generic_functions
from operations_modules import app_config_access
from operations_modules import sqlite_database
from operations_modules.sqlite_database import CreateDatabaseVariables

round_decimal_to = 2


class CreateLinuxSystem:
    """ Creates Function access to Linux System Information. """

    def __init__(self):
        self.database_variables = CreateDatabaseVariables()
        logger.sensors_logger.debug("Linux System Module Initialization - OK")

    @staticmethod
    def get_os_name_version():
        """ Returns sensors Operating System Name and Version. """
        try:
            os_release_content_lines = app_generic_functions.get_file_content("/etc/os-release").split("\n")
            os_release_name = ""
            for line in os_release_content_lines:
                name_and_value = line.split("=")
                if name_and_value[0].strip() == "PRETTY_NAME":
                    os_release_name = name_and_value[1].strip()[1:-1]
            return os_release_name
        except Exception as error:
            logger.sensors_logger.error("Linux System - Unable to get Raspbian OS Version: " + str(error))
            return "Error retrieving OS information"

    @staticmethod
    def get_hostname():
        """ Returns System HostName as a String. """
        try:
            hostname = str(socket.gethostname())
        except Exception as error:
            logger.sensors_logger.error("Linux System -  Sensor Name - Failed: " + str(error))
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
        except Exception as error:
            logger.sensors_logger.warning("Linux System - Sensor IP - Failed: " + str(error))
            ip_address = "0.0.0.0"
        return ip_address

    @staticmethod
    def get_uptime_raw():
        """ Returns System Uptime in minutes as a Integer. """
        try:
            with open('/proc/uptime', 'r') as f:
                uptime_seconds = float(f.readline().split()[0])
                uptime_min = int(uptime_seconds / 60)
        except Exception as error:
            logger.sensors_logger.error("Linux System - Sensor Up Time - Failed: " + str(error))
            uptime_min = 0
        return uptime_min

    def get_uptime_str(self):
        """ Returns System UpTime as a human readable String. """
        if app_config_access.current_platform == "Linux":
            var_minutes = self.get_uptime_raw()
            str_day_hour_min = ""
            try:
                uptime_days = int(float(var_minutes) // 1440)
                uptime_hours = int((float(var_minutes) % 1440) // 60)
                uptime_min = int(float(var_minutes) % 60)
                if uptime_days:
                    if uptime_days > 1:
                        str_day_hour_min = str(uptime_days) + " Days, "
                    else:
                        str_day_hour_min = str(uptime_days) + " Day, "
                if uptime_hours:
                    if uptime_hours > 1:
                        str_day_hour_min += str(uptime_hours) + " Hours & "
                    else:
                        str_day_hour_min += str(uptime_hours) + " Hour & "
                str_day_hour_min += str(uptime_min) + " Min"

            except Exception as error:
                logger.sensors_logger.error("Linux System - Unable to convert DateTime to String: " + str(error))
                str_day_hour_min = var_minutes
            return str_day_hour_min

    @staticmethod
    def get_sys_datetime_str():
        """ Returns System DateTime in format YYYY-MM-DD HH:MM as a String. """
        return strftime("%Y-%m-%d %H:%M - %Z")

    @staticmethod
    def get_memory_usage_percent():
        """ Returns sensor RAM usage as a %. """
        try:
            mem = psutil.virtual_memory()
            return_mem = mem[2]
        except Exception as error:
            logger.sensors_logger.error("Linux System - Get Memory Usage Error: " + str(error))
            return_mem = "Error"
        return return_mem

    @staticmethod
    def get_disk_usage_gb():
        """ Returns sensor root disk usage as GB's as a string. """
        try:
            used_disk_space = psutil.disk_usage("/")[2]
            return str(round(used_disk_space / (2 ** 30), 2))
        except Exception as error:
            logger.sensors_logger.error("Linux System - Get Disk Usage in GB Error: " + str(error))
            return "Error"

    @staticmethod
    def get_disk_usage_percent():
        """ Returns sensor root disk usage as a % as a string. """
        try:
            drive_information = psutil.disk_usage("/")
            return_disk_usage = str(drive_information[3])
        except Exception as error:
            logger.sensors_logger.error("Linux System - Get Disk Usage % Error: " + str(error))
            return_disk_usage = "Error"
        return return_disk_usage

    @staticmethod
    def get_sql_db_size():
        """ Returns Sensor SQLite DB Size in MB as a Float. """
        try:
            db_size_mb = os.path.getsize(file_locations.sensor_database) / 1_000_000
        except Exception as error:
            logger.sensors_logger.error("Linux System - Interval Database Size Failed: " + str(error))
            db_size_mb = 0.0
        return round(db_size_mb, round_decimal_to)

    def get_db_notes_count(self):
        """ Returns the number of notes stored in the database as a str. """
        sql_query = "SELECT count(" + \
                    str(self.database_variables.other_table_column_notes) + \
                    ") FROM " + \
                    str(self.database_variables.table_other)

        number_of_notes = str(sqlite_database.sql_execute_get_data(sql_query))

        if len(number_of_notes) > 5:
            return_notes_count = number_of_notes[2:-3]
        else:
            logger.sensors_logger.error("Linux System - Unable to get SQLite Database Notes count")
            return_notes_count = "Error"
        return return_notes_count

    def get_db_first_last_date(self):
        """ Returns the first and last date stored in the database as a string. """
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
            logger.sensors_logger.error("Linux System - Database get First & Last DateTime Failed: " + str(error))
            db_datetime_column_list = ["---Error--", "--Error----"]

        if len(db_datetime_column_list) == 2:
            textbox_db_dates = db_datetime_column_list[0][3:-5] + " || " + db_datetime_column_list[1][2:-7]
        else:
            textbox_db_dates = "DataBase Error"
        return textbox_db_dates

    def get_sensor_reboot_count(self):
        """
        Returns the number of times the sensor has rebooted as a str.
        Reboot count is calculated by uptime values stored in the Database.
        """
        sql_query = "SELECT " + str(self.database_variables.sensor_uptime) + \
                    " FROM " + str(self.database_variables.table_interval) + \
                    " WHERE length(" + str(self.database_variables.sensor_uptime) + \
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
        debug_message = "Linux System - " + str(len(sql_column_data)) + " entries in DB reboot column retrieved"
        logger.sensors_logger.debug(debug_message)
        return str(reboot_count)
