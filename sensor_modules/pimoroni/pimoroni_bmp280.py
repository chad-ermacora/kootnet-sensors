"""
This module is for the Pimoroni BMP280
It Retrieves & Returns Sensor data to be written to the DB

Bosch BMP280 temperature, pressure, altitude sensor
I2C interface, with address select via ADDR cuttable trace (0x76 or 0x77)
3.3V or 5V compatible
Reverse polarity protection
Raspberry Pi-compatible pinout (pins 1, 3, 5, 7, 9)
Compatible with Raspberry Pi 3B+, 3, 2, B+, A+,

pip3 install bmp280

Created on Tue June 25 10:53:56 2019

@author: OO-Dragon
"""
import time
from operations_modules import logger
from configuration_modules import app_config_access

round_decimal_to = 5
pause_sensor_during_access_sec = 0.02


class CreateBMP280:
    """ Creates Function access to the Pimoroni BMP280. """

    def __init__(self):
        self.sensor_in_use = False
        try:
            bmp280_import = __import__("sensor_modules.drivers.bmp280", fromlist=["BMP280"])
            smbus2_import = __import__("smbus2", fromlist=["SMBus"])
            bus = smbus2_import.SMBus(1)
            self.bmp280 = bmp280_import.BMP280(i2c_dev=bus)
            self.bmp280.get_temperature()
            logger.sensors_logger.debug("Pimoroni BMP280 Initialization - OK")
        except Exception as error:
            logger.sensors_logger.error("Pimoroni BMP280 Initialization - Failed: " + str(error))
            app_config_access.installed_sensors.pimoroni_bmp280 = 0
            app_config_access.installed_sensors.update_configuration_settings_list()

    def temperature(self):
        """ Returns Temperature as a Float. """
        while self.sensor_in_use:
            time.sleep(pause_sensor_during_access_sec)
        self.sensor_in_use = True
        try:
            temp_var = self.bmp280.get_temperature()
        except Exception as error:
            temp_var = 0.0
            logger.sensors_logger.error("Pimoroni BMP280 Temperature - Failed: " + str(error))
        self.sensor_in_use = False
        return round(temp_var, round_decimal_to)

    def pressure(self):
        """ Returns Pressure as a Integer. """
        while self.sensor_in_use:
            time.sleep(pause_sensor_during_access_sec)
        self.sensor_in_use = True
        try:
            pressure_hpa = self.bmp280.get_pressure()
        except Exception as error:
            pressure_hpa = 0.0
            logger.sensors_logger.error("Pimoroni BMP280 Pressure - Failed: " + str(error))
        self.sensor_in_use = False
        return pressure_hpa

    def altitude(self):
        """ Returns Altitude in meters? as a float. """
        while self.sensor_in_use:
            time.sleep(pause_sensor_during_access_sec)
        self.sensor_in_use = True
        try:
            altitude_var = self.bmp280.get_altitude()
            altitude_var = round(altitude_var, round_decimal_to)
        except Exception as error:
            altitude_var = 0.0
            logger.sensors_logger.error("Pimoroni BMP280 Altitude - Failed: " + str(error))
        self.sensor_in_use = False
        return altitude_var
