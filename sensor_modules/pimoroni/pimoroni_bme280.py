"""
This module is for the Pimoroni BME280
It Retrieves & Returns Sensor data to be written to the DB

Bosch BME280 temperature, pressure, humidity sensor
I2C interface, with address select via cuttable ADDR trace (0x76 or 0x77)
3.3V or 5V compatible
Reverse polarity protection
Raspberry Pi-compatible pinout (pins 1, 3, 5, 7, 9)
Compatible with all models of Raspberry Pi, and Arduino

Created on Tue July 1 06:40:56 2019

@author: OO-Dragon
"""
import time
from operations_modules import logger
from configuration_modules import app_config_access

round_decimal_to = 5
pause_sensor_during_access_sec = 0.02


class CreateBME280:
    """ Creates Function access to the Pimoroni BME280. """

    def __init__(self):
        self.sensor_in_use = False
        try:
            bme280_import = __import__("sensor_modules.drivers.bme280", fromlist=["BME280"])
            self.smbus_import = __import__("sensor_modules.drivers.smbus2.smbus2", fromlist=["SMBus"])
            self.bme280 = bme280_import.BME280(i2c_dev=self.smbus_import.SMBus(1))
            self.bme280.get_temperature()
            logger.sensors_logger.debug("Pimoroni BME280 Initialization - OK")
        except Exception as error:
            logger.sensors_logger.error("Pimoroni BME280 Initialization - Failed: " + str(error))
            app_config_access.installed_sensors.pimoroni_bme280 = 0
            app_config_access.installed_sensors.update_configuration_settings_list()

    def temperature(self):
        """ Returns Temperature as a Float. """
        while self.sensor_in_use:
            time.sleep(pause_sensor_during_access_sec)
        self.sensor_in_use = True
        try:
            temp_var = self.bme280.get_temperature()
            temp_var = round(temp_var, round_decimal_to)
        except Exception as error:
            temp_var = 0.0
            logger.sensors_logger.error("Pimoroni BME280 Temperature - Failed: " + str(error))
        self.sensor_in_use = False
        return temp_var

    def pressure(self):
        """ Returns Pressure as a Integer. """
        while self.sensor_in_use:
            time.sleep(pause_sensor_during_access_sec)
        self.sensor_in_use = True
        try:
            pressure_hpa = self.bme280.get_pressure()
            pressure_hpa = round(float(pressure_hpa), round_decimal_to)
        except Exception as error:
            pressure_hpa = 0.0
            logger.sensors_logger.error("Pimoroni BME280 Pressure - Failed: " + str(error))
        self.sensor_in_use = False
        return pressure_hpa

    def humidity(self):
        """ Returns Humidity as a Float. """
        while self.sensor_in_use:
            time.sleep(pause_sensor_during_access_sec)
        self.sensor_in_use = True
        try:
            humidity = self.bme280.get_humidity()
            humidity = round(float(humidity), round_decimal_to)
        except Exception as error:
            humidity = 0.0
            logger.sensors_logger.error("Pimoroni BME280 Humidity - Failed: " + str(error))
        self.sensor_in_use = False
        return humidity
