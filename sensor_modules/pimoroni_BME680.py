"""
This module is for the Pimoroni BME680
It Retrieves & Returns Sensor data to be written to the DB

Bosch BME680 temperature, pressure, humidity, air quality sensor
I2C interface, with address select via ADDR solder bridge (0x76 or 0x77)
3.3V or 5V compatible
Reverse polarity protection
Raspberry Pi-compatible pinout (pins 1, 3, 5, 7, 9)

pip3 install bme680

Created on Sat Aug 25 08:53:56 2018

@author: OO-Dragon
"""
import bme680
import logging
from logging.handlers import RotatingFileHandler

logger = logging.getLogger(__name__)

logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(funcName)s:  %(message)s', '%Y-%m-%d %H:%M:%S')

file_handler = RotatingFileHandler('/home/pi/KootNetSensors/logs/Sensors_log.txt', maxBytes=256000, backupCount=5)
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)

round_decimal_to = 5


def temperature():
    try:
        sensor = bme680.BME680()
        sensor.set_temperature_oversample(bme680.OS_8X)
        sensor.set_filter(bme680.FILTER_SIZE_3)

        sensor.get_sensor_data()

        temp_var = float(sensor.data.temperature)
        logger.debug("Pimoroni BME680 Temperature - OK")
    except Exception as error:
        temp_var = 0
        logger.error("Pimoroni BME680 Temperature - Failed - " + str(error))

    return round(temp_var, round_decimal_to)


def pressure():
    try:
        sensor = bme680.BME680()
        sensor.set_pressure_oversample(bme680.OS_4X)
        sensor.set_filter(bme680.FILTER_SIZE_3)

        sensor.get_sensor_data()

        pressure_hpa = sensor.data.pressure
        logger.debug("Pimoroni BME680 Pressure - OK")
    except Exception as error:
        pressure_hpa = 0
        logger.error("Pimoroni BME680 Pressure - Failed - " + str(error))

    return int(pressure_hpa)


def humidity():
    try:
        sensor = bme680.BME680()
        sensor.set_humidity_oversample(bme680.OS_2X)
        sensor.set_filter(bme680.FILTER_SIZE_3)

        sensor.get_sensor_data()
        var_humidity = sensor.data.humidity

        logger.debug("Pimoroni BME680 Humidity - OK")
    except Exception as error:
        var_humidity = 0
        logger.error("Pimoroni BME680 Humidity - Failed - " + str(error))

    return round(var_humidity, round_decimal_to)


def gas_resistance():
    try:
        sensor = bme680.BME680()
        sensor.set_filter(bme680.FILTER_SIZE_3)
        sensor.set_gas_status(bme680.ENABLE_GAS_MEAS)
        sensor.set_gas_heater_temperature(320)
        sensor.set_gas_heater_duration(150)
        sensor.select_gas_heater_profile(0)

        sensor.get_sensor_data()
        gas_var = sensor.data.gas_resistance

        logger.debug("Pimoroni BME680 GAS Resistance - OK")
    except Exception as error:
        gas_var = 0
        logger.error("Pimoroni BME680 GAS Resistance - Failed - " + str(error))

    return gas_var
