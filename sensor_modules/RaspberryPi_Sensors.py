"""
This module is for the Raspberry Pi System
It Retrieves System & Sensor data

Tested on the RP3B+ & RPWZ

Created on Sat Aug 25 08:53:56 2018

@author: OO-Dragon
"""
import logging
from logging.handlers import RotatingFileHandler
from gpiozero import CPUTemperature

logger = logging.getLogger(__name__)

logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(funcName)s:  %(message)s', '%Y-%m-%d %H:%M:%S')

file_handler = RotatingFileHandler('/home/pi/config/logs/Sensors_log.txt', maxBytes=256000, backupCount=5)
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)

round_decimal_to = 5


def cpu_temperature():
    try:
        cpu = CPUTemperature()
        cpu_temp_c = float(cpu.temperature)
        logger.debug("Raspberry Pi CPU Temperature Sensor - OK")
    except Exception as error:
        cpu_temp_c = 0.00000
        logger.error("Raspberry Pi CPU Temperature Sensor - Failed - " + str(error))

    return round(cpu_temp_c, round_decimal_to)
