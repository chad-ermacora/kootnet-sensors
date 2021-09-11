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
from configuration_modules import app_config_access

round_decimal_to = 5
# Update readings in seconds
sleep_between_readings_seconds = 1


class CreateSGP30:
    """ Creates Function access to the Pimoroni SGP30. """

    def __init__(self):
        self.gas_resistance_var = 0.0
        self.e_co2_var = 0.0
        self.sensor_latency = 0.0

        try:
            sgp30_import = __import__("sensor_modules.drivers.sgp30", fromlist=["SGP30"])
            self.sensor = sgp30_import.SGP30()
            self.thread_readings_updater = Thread(target=self._readings_updater)
            self.thread_readings_updater.daemon = True
            self.thread_readings_updater.start()
            logger.sensors_logger.debug("Pimoroni SGP30 Initialization - OK")
        except Exception as error:
            logger.sensors_logger.error("Pimoroni SGP30 Initialization - Failed: " + str(error))
            app_config_access.installed_sensors.pimoroni_sgp30 = 0
            app_config_access.installed_sensors.update_configuration_settings_list()

    def _readings_updater(self):
        thread_measurement_updater = Thread(target=self.sensor.start_measurement)
        thread_measurement_updater.daemon = True
        thread_measurement_updater.start()
        logger.sensors_logger.debug("Pimoroni SGP30 readings updater started")

        while True:
            try:
                start_time = time.time()
                eco2, tvoc = self.sensor.get_air_quality()
                end_time = time.time()
                self.sensor_latency = float(end_time - start_time)
                self.gas_resistance_var = tvoc
                self.e_co2_var = eco2
            except Exception as error:
                logger.sensors_logger.error("Pimoroni SGP30 Readings Update Failed: " + str(error))
                self.gas_resistance_var = 0.0
                self.e_co2_var = 0.0
            time.sleep(sleep_between_readings_seconds)

    def gas_resistance_index(self):
        """ Returns Gas Resistance Index as a float in kΩ. """
        return round(self.gas_resistance_var, round_decimal_to)

    def gas_e_co2(self):
        """ Returns Equivalent CO2 as a float in kΩ? """
        return round(self.e_co2_var, round_decimal_to)
