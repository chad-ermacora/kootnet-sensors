"""
This module is for the Raspberry Pi Sense HAT
It Retrieves & Returns Sensor data to be written to the DB

8 by 8 rgb LED matrix
five-button joystick
Gyroscope
Accelerometer
Magnetometer
Temperature
Barometric pressure
Humidity

pip3 install sense-hat

Created on Sat Aug 25 08:53:56 2018

@author: OO-Dragon
"""
import logging
from logging.handlers import RotatingFileHandler
from sense_hat import SenseHat

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


def temperature():
    try:
        sense = SenseHat()
        env_temp = float(sense.get_temperature())
        logger.debug("Raspberry Pi Sense HAT Temperature - OK")
    except Exception as error:
        logger.error("Raspberry Pi Sense HAT Temperature - Failed - " + str(error))
        env_temp = 0

    return round(env_temp, round_decimal_to)


def pressure():
    try:
        sense = SenseHat()
        pressure_hpa = sense.get_pressure()
        logger.debug("Raspberry Pi Sense HAT Pressure - OK")
    except Exception as error:
        logger.error("Raspberry Pi Sense HAT Pressure - Failed - " + str(error))
        pressure_hpa = 0

    return int(pressure_hpa)


def humidity():
    try:
        sense = SenseHat()
        var_humidity = sense.get_humidity()
        logger.debug("Raspberry Pi Sense HAT Humidity - OK")
    except Exception as error:
        logger.error("Raspberry Pi Sense HAT Humidity - Failed - " + str(error))
        var_humidity = 0

    return round(var_humidity, round_decimal_to)


def magnetometer_xyz():
    try:
        sense = SenseHat()
        mag_x = sense.get_compass_raw()['x']
        mag_y = sense.get_compass_raw()['y']
        mag_z = sense.get_compass_raw()['z']
        logger.debug("Raspberry Pi Sense HAT Magnetometer XYZ - OK")
    except Exception as error:
        logger.error("Raspberry Pi Sense HAT Magnetometer XYZ - Failed - " + str(error))
        mag_x, mag_y, mag_z = 0, 0, 0

    return round(mag_x, round_decimal_to), round(mag_y, round_decimal_to), round(mag_z, round_decimal_to)


def accelerometer_xyz():
    try:
        sense = SenseHat()
        acc_x = sense.get_accelerometer_raw()['x']
        acc_y = sense.get_accelerometer_raw()['y']
        acc_z = sense.get_accelerometer_raw()['z']
        logger.debug("Raspberry Pi Sense HAT Accelerometer XYZ - OK")
    except Exception as error:
        logger.error("Raspberry Pi Sense HAT Accelerometer XYZ - Failed - " + str(error))
        acc_x, acc_y, acc_z = 0, 0, 0

    return round(acc_x, round_decimal_to), round(acc_y, round_decimal_to), round(acc_z, round_decimal_to)


def gyroscope_xyz():
    try:
        sense = SenseHat()
        gyro_x = sense.get_gyroscope_raw()['x']
        gyro_y = sense.get_gyroscope_raw()['y']
        gyro_z = sense.get_gyroscope_raw()['z']
        logger.error("Raspberry Pi Sense HAT Gyroscope XYZ - OK")
    except Exception as error:
        logger.error("Raspberry Pi Sense HAT Gyroscope XYZ - Failed - " + str(error))
        gyro_x, gyro_y, gyro_z = 0, 0, 0

    return round(gyro_x, round_decimal_to), round(gyro_y, round_decimal_to), round(gyro_z, round_decimal_to)
