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
import time
from threading import Thread
from operations_modules import logger
from configuration_modules import app_config_access

round_decimal_to = 5
# Update readings in seconds
sleep_between_readings_seconds = 1


class CreateBME680:
    """ Creates Function access to the Pimoroni BME680. """

    def __init__(self):
        self.temperature_var = 0.0
        self.pressure_var = 0.0
        self.humidity_var = 0.0
        self.gas_resistance_var = 0.0

        try:
            bme680_import = __import__("sensor_modules.drivers.bme680", fromlist=["BME680"])
            self.sensor = bme680_import.BME680()
            self.sensor.set_humidity_oversample(bme680_import.OS_2X)
            self.sensor.set_filter(bme680_import.FILTER_SIZE_3)
            self.sensor.set_gas_status(bme680_import.ENABLE_GAS_MEAS)
            self.sensor.set_gas_heater_temperature(320)
            self.sensor.set_gas_heater_duration(150)
            self.sensor.select_gas_heater_profile(0)

            self.sensor.get_sensor_data()

            self.thread_readings_updater = Thread(target=self._readings_updater)
            self.thread_readings_updater.daemon = True
            self.thread_readings_updater.start()
            logger.sensors_logger.debug("Pimoroni BME680 Initialization - OK")
        except Exception as error:
            logger.sensors_logger.error("Pimoroni BME680 Initialization - Failed: " + str(error))
            app_config_access.installed_sensors.pimoroni_bme680 = 0
            app_config_access.installed_sensors.update_configuration_settings_list()

    def _readings_updater(self):
        logger.sensors_logger.debug("Pimoroni BME680 readings updater started")
        while True:
            try:
                self.sensor.get_sensor_data()
                self.temperature_var = float(self.sensor.data.temperature)
                self.pressure_var = float(self.sensor.data.pressure)
                self.humidity_var = float(self.sensor.data.humidity)
                self.gas_resistance_var = float(self.sensor.data.gas_resistance) / 1000
            except Exception as error:
                logger.sensors_logger.error("Pimoroni BME680 Readings Update Failed: " + str(error))
                self.temperature_var = 0.0
                self.pressure_var = 0.0
                self.humidity_var = 0.0
                self.gas_resistance_var = 0.0
            time.sleep(sleep_between_readings_seconds)

    def temperature(self):
        """ Returns Temperature as a Float. """
        return round(self.temperature_var, round_decimal_to)

    def pressure(self):
        """ Returns Pressure as a Float. """
        return round(self.pressure_var, round_decimal_to)

    def humidity(self):
        """ Returns Humidity as a Float. """
        return round(self.humidity_var, round_decimal_to)

    def gas_resistance_index(self):
        """ Returns Gas Resistance Index as a float in kΩ. """
        return round(self.gas_resistance_var, round_decimal_to)
