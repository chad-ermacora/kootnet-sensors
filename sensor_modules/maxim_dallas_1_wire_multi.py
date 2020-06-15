"""
This module is for the Maxim/Dallas DS18S20 / DS1822 / DS18B20 / DS28EA00 / DS1825/MAX31850K
It Retrieves & Returns Sensor data to be written to the DB

Using Python module W1ThermSensor to interact with all the sensors mentioned above
Defaults to sending Celsius but can be changed with the following

Unit.DEGREES_C
Unit.DEGREES_F
Unit.KELVIN
Eg. temperature = sensor.get_temperature(Unit.KELVIN)

pip3 install w1thermsensor

Created on Tue June 15 12:53:56 2020

@author: OO-Dragon
"""
import time
from operations_modules import logger
from configuration_modules import app_config_access

round_decimal_to = 5
pause_sensor_during_access_sec = 0.02


class CreateW1ThermSenor:
    """ Creates Function access to W1ThermSensor. """

    def __init__(self):
        self.sensor_in_use = False
        try:
            w1thermsensor_import = __import__("sensor_modules.drivers.w1thermsensor", fromlist=["W1ThermSensor"])
            self.w1thermsensor = w1thermsensor_import.W1ThermSensor()
            self.w1thermsensor.get_temperature()
            logger.sensors_logger.debug("W1ThermSensor Initialization - OK")
        except Exception as error:
            logger.sensors_logger.error("W1ThermSensor Initialization - Failed: " + str(error))
            app_config_access.installed_sensors.w1_therm_sensor = 0

    def temperature(self):
        """ Returns Temperature as a Float. """
        while self.sensor_in_use:
            time.sleep(pause_sensor_during_access_sec)
        self.sensor_in_use = True
        try:
            temp_var = self.w1thermsensor.get_temperature()
        except Exception as error:
            temp_var = 0.0
            logger.sensors_logger.error("W1ThermSensor Temperature - Failed: " + str(error))
        self.sensor_in_use = False
        return round(temp_var, round_decimal_to)
