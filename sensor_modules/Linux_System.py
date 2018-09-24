"""
This module is for the Raspberry Pi System
It Retrieves System & Sensor data

Tested on the RP3B+ & RPWZ

Created on Sat Aug 25 08:53:56 2018

@author: OO-Dragon
"""
import os
import socket
import logging
from logging.handlers import RotatingFileHandler
from time import strftime

logger = logging.getLogger(__name__)

logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(funcName)s:  %(message)s', '%Y-%m-%d %H:%M:%S')

file_handler = RotatingFileHandler('/home/pi/KootNetSensors/logs/Sensors_log.txt', maxBytes=256000, backupCount=5)
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)

primary_database_location = "/home/pi/KootNetSensors/data/SensorIntervalDatabase.sqlite"
motion_database_location = "/home/pi/KootNetSensors/data/SensorTriggerDatabase.sqlite"

round_decimal_to = 2


def get_primary_db_size():
    try:
        db_size_mb = os.path.getsize(primary_database_location) / 1024000
        logger.debug("Linux System Interval Database Size - OK")
    except Exception as error:
        logger.error("Linux System Interval Database Size - Failed - " + str(error))
        db_size_mb = 0.0

    return round(db_size_mb, round_decimal_to)


def get_motion_db_size():
    try:
        db_size_mb = os.path.getsize(motion_database_location) / 1024000
        logger.debug("Linux System Trigger Database Size - OK")
    except Exception as error:
        logger.error("Linux System Trigger Database Size - Failed - " + str(error))
        db_size_mb = 0.0

    return round(db_size_mb, round_decimal_to)


def get_hostname():
    try:
        hostname = str(socket.gethostname())
        logger.debug("Linux System Sensor Name - OK")
    except Exception as error:
        logger.error("Linux System Sensor Name - Failed - " + str(error))
        hostname = "HostFailed"

    return hostname


def get_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_address = (s.getsockname()[0])
        s.close()
        logger.debug("Linux System Sensor IP - OK")
    except Exception as error:
        logger.error("Linux System Sensor IP - Failed - " + str(error))
        ip_address = "0.0.0.0"

    return ip_address


def get_uptime():
    try:
        with open('/proc/uptime', 'r') as f:
            uptime_seconds = float(f.readline().split()[0])
            uptime_min = int(uptime_seconds / 60)
        logger.debug("Linux System Sensor Up Time - OK")
    except Exception as error:
        logger.error("Linux System Sensor Up Time - Failed - " + str(error))
        uptime_min = 0

    return uptime_min


def get_sys_datetime():
    logger.debug("Linux System Sensor Date Time - OK")
    return strftime("%Y-%m-%d %H:%M")
