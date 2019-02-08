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

from operations_modules import operations_logger
from operations_modules.operations_file_locations import sensor_database_location

round_decimal_to = 2


class CreateLinuxSystem:
    """ Creates Function access to Linux System Information. """

    @staticmethod
    def get_hostname():
        try:
            hostname = str(socket.gethostname())
            operations_logger.sensors_logger.debug("Linux System Sensor Name - OK")
        except Exception as error:
            operations_logger.sensors_logger.error("Linux System Sensor Name - Failed - " + str(error))
            hostname = "HostFailed"
        return hostname

    @staticmethod
    def get_ip():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip_address = (s.getsockname()[0])
            s.close()
            operations_logger.sensors_logger.debug("Linux System Sensor IP - OK")
        except Exception as error:
            operations_logger.sensors_logger.warning("Linux System Sensor IP - Failed - " + str(error))
            ip_address = "0.0.0.0"
        return ip_address

    @staticmethod
    def get_uptime():
        try:
            with open('/proc/uptime', 'r') as f:
                uptime_seconds = float(f.readline().split()[0])
                uptime_min = int(uptime_seconds / 60)
            operations_logger.sensors_logger.debug("Linux System Sensor Up Time - OK")
        except Exception as error:
            operations_logger.sensors_logger.error("Linux System Sensor Up Time - Failed - " + str(error))
            uptime_min = 0

        return uptime_min

    @staticmethod
    def get_sys_datetime():
        operations_logger.sensors_logger.debug("Linux System Sensor Date Time - OK")
        return strftime("%Y-%m-%d %H:%M")

    @staticmethod
    def get_sql_db_size():
        try:
            db_size_mb = os.path.getsize(sensor_database_location) / 1024000
            operations_logger.sensors_logger.debug("Linux System Interval Database Size - OK")
        except Exception as error:
            operations_logger.sensors_logger.error("Linux System Interval Database Size - Failed - " + str(error))
            db_size_mb = 0.0
        return round(db_size_mb, round_decimal_to)
