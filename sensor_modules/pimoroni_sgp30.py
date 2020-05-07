"""
This module is for the Pimoroni SGP30
It Retrieves & Returns Sensor data to be written to the DB

Sensiron SGP30 TVOC and eCO2 sensor
TVOC sensing from 0-60,000 ppb (parts per billion)
CO2 sensing from 400 to 60,000 ppm (parts per million)
1Hz sampling rate
I2C interface(address 0x58)
3.3V or 5V compatible
Reverse polarity protection
Raspberry Pi-compatible pinout (pins 1, 3, 5, 7, 9)

pip3 install sgp30

Created on Mon Jan 20 11:48:56 2020

@author: OO-Dragon
"""
import time
from threading import Thread
from operations_modules import logger
from operations_modules import app_config_access

round_decimal_to = 5
pause_sensor_during_access_sec = 0.1
gas_keep_alive_update_sec = 1


class CreateSGP30:
    """ Creates Function access to the Pimoroni SGP30. """

    def __init__(self):
        self.sensor_in_use = False
        try:
            sgp30_import = __import__("sensor_modules.drivers.sgp30", fromlist=["SGP30"])
            self.sensor = sgp30_import.SGP30()
            self.sensor_in_use = True
            self.sensor.start_measurement()
            self.sensor_in_use = False
            self.thread_gas_keep_alive = Thread(target=self._gas_readings_keep_alive)
            self.thread_gas_keep_alive.daemon = True
            self.thread_gas_keep_alive.start()
            logger.sensors_logger.debug("Pimoroni SGP30 Initialization - OK")
        except Exception as error:
            logger.sensors_logger.error("Pimoroni SGP30 Initialization - Failed: " + str(error))
            app_config_access.installed_sensors.pimoroni_sgp30 = 0

    def _gas_readings_keep_alive(self):
        logger.sensors_logger.debug("Pimoroni SGP30 Gas keep alive started")
        while True:
            while self.sensor_in_use:
                time.sleep(pause_sensor_during_access_sec)
            self.sensor_in_use = True
            self.sensor.get_air_quality()
            self.sensor_in_use = False
            time.sleep(gas_keep_alive_update_sec)

    def gas_resistance_index(self):
        """ Returns Gas Resistance Index as a float in kΩ. """
        while self.sensor_in_use:
            time.sleep(pause_sensor_during_access_sec)
        self.sensor_in_use = True
        eco2, tvoc = self.sensor.get_air_quality()
        self.sensor_in_use = False
        try:
            gas_var = round(tvoc / 1000, round_decimal_to)
        except Exception as error:
            gas_var = 0.0
            logger.sensors_logger.error("Pimoroni SGP30 GAS Resistance - Failed: " + str(error))
        return gas_var

    def gas_e_co2(self):
        """ Returns Equivalent CO2 as a float in kΩ? """
        while self.sensor_in_use:
            time.sleep(pause_sensor_during_access_sec)
        self.sensor_in_use = True
        eco2, tvoc = self.sensor.get_air_quality()
        self.sensor_in_use = False
        try:
            gas_var = round(eco2 / 1000, round_decimal_to)
        except Exception as error:
            gas_var = 0.0
            logger.sensors_logger.error("Pimoroni SGP30 E-CO2 Resistance - Failed: " + str(error))
        return gas_var
