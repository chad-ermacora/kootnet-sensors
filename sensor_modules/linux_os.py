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

round_decimal_to = 2


class CreateLinuxSystem:
    """ Creates Function access to Linux System Information. """

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
    def get_sys_datetime():
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
