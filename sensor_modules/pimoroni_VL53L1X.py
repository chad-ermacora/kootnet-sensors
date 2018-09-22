# -*- coding: utf-8 -*-
"""
This module is for the Pimoroni VL53L1X Time of Flight
It Retrieves & Returns Sensor data to be written to the DB

VL53L1X Time of Flight (ToF) sensor (datasheet)
4-400cm range (27° field of view)
Up to 50Hz ranging frequency
+/- 25mm accuracy (+/- 20mm in the dark)
I2C interface (address 0x29)
3.3V or 5V compatible
Reverse polarity protection

pip install smbus2 vl53l1x

Created on Sat Aug 25 08:53:56 2018

@author: OO-Dragon
"""
import VL53L1X
import logging
from logging.handlers import RotatingFileHandler

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


def distance_from_sensor():
    try:
        time_of_flight = VL53L1X.VL53L1X(i2c_bus=1, i2c_address=0x29)
        # Initialise the i2c bus and configure the sensor
        time_of_flight.open()
        # Start ranging, 1 = Short Range, 2 = Medium Range, 3 = Long Range
        time_of_flight.start_ranging(2)
        distance_in_mm = time_of_flight.get_distance()
        time_of_flight.stop_ranging()
        logger.debug("Pimoroni VL53L1X Distance Sensor - OK")
    except Exception as error:
        logger.error("Pimoroni VL53L1X Distance Sensor - Failed - " + str(error))
        distance_in_mm = 0

    return distance_in_mm
