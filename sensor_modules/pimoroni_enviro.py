""""
This module is for the Pimoroni Enviro pHAT
It Retrieves & Returns Sensor data to be written to the DB

BMP280 temperature/pressure sensor
TCS3472 light and rgb colour sensor
Two LEDs for illumination
LSM303D accelerometer/magnetometer sensor
ADS1015 4-channel 3.3v, analog to digital sensor (ADC)

pip3 install envirophat

Created on Sat Aug 25 08:53:56 2018

@author: OO-Dragon
"""
import logging
from logging.handlers import RotatingFileHandler
# 'leds' could also be added to turn the 2x LED lights on and off
from envirophat import light, weather, motion

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
        env_temp = float(weather.temperature())
        logger.debug("Pimoroni Enviro Temperature - OK")
    except Exception as error:
        logger.error("Pimoroni Enviro Temperature - Failed - " + str(error))
        env_temp = 0

    return round(env_temp, round_decimal_to)


def pressure():
    try:
        pressure_hpa = weather.pressure(unit='hPa')
        logger.debug("Pimoroni Enviro Pressure - OK")
    except Exception as error:
        logger.error("Pimoroni Enviro Pressure - Failed - " + str(error))
        pressure_hpa = 0

    return int(pressure_hpa)


def lumen():
    try:
        var_lumen = light.light()
        logger.debug("Pimoroni Enviro Lumen - OK")
    except Exception as error:
        logger.error("Pimoroni Enviro Lumen - Failed - " + str(error))
        var_lumen = 0

    return int(var_lumen)


def rgb():
    try:
        rgb_red, rgb_green, rgb_blue = light.rgb()
        logger.debug("Pimoroni Enviro RGB - OK")
    except Exception as error:
        logger.error("Pimoroni Enviro RGB - Failed - " + str(error))
        rgb_red, rgb_green, rgb_blue = 0, 0, 0

    return round(rgb_red, round_decimal_to), round(rgb_green, round_decimal_to), round(rgb_blue, round_decimal_to)


def magnetometer_xyz():
    try:
        mag_x, mag_y, mag_z = motion.magnetometer()
        logger.debug("Pimoroni Enviro Magnetometer XYZ - OK")
    except Exception as error:
        mag_x, mag_y, mag_z = 0, 0, 0
        logger.error("Pimoroni Enviro Magnetometer XYZ - Failed - " + str(error))

    return round(mag_x, round_decimal_to), round(mag_y, round_decimal_to), round(mag_z, round_decimal_to)


def accelerometer_xyz():
    try:
        acc_x, acc_y, acc_z = motion.accelerometer()
        logger.debug("Pimoroni Enviro Accelerometer XYZ - OK")
    except Exception as error:
        logger.error("Pimoroni Enviro Accelerometer XYZ - Failed - " + str(error))
        acc_x, acc_y, acc_z = 0, 0, 0

    return round(acc_x, round_decimal_to), round(acc_y, round_decimal_to), round(acc_z, round_decimal_to)
