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
from time import sleep
from threading import Thread
from operations_modules import logger
from operations_modules import app_config_access

round_decimal_to = 5


class CreateBME680:
    """ Creates Function access to the Pimoroni BME680. """

    def __init__(self):
        self.pause_gas_keep_alive = False
        try:
            self.bme680_import = __import__('bme680')
            self.sensor = self.bme680_import.BME680()
            self.sensor.set_humidity_oversample(self.bme680_import.OS_2X)
            self.sensor.set_filter(self.bme680_import.FILTER_SIZE_3)
            self.sensor.set_gas_status(self.bme680_import.ENABLE_GAS_MEAS)
            self.sensor.set_gas_heater_temperature(320)
            self.sensor.set_gas_heater_duration(150)
            self.sensor.select_gas_heater_profile(0)

            self.sensor.get_sensor_data()

            self.thread_gas_keep_alive = Thread(target=self._gas_readings_keep_alive)
            self.thread_gas_keep_alive.daemon = True
            self.thread_gas_keep_alive.start()
            logger.sensors_logger.debug("Pimoroni BME680 Initialization - OK")
        except Exception as error:
            logger.sensors_logger.error("Pimoroni BME680 Initialization - Failed: " + str(error))
            app_config_access.installed_sensors.pimoroni_bme680 = 0
            app_config_access.installed_sensors.has_env_temperature = 0
            app_config_access.installed_sensors.has_pressure = 0
            app_config_access.installed_sensors.has_humidity = 0
            app_config_access.installed_sensors.has_gas = 0

    def _gas_readings_keep_alive(self):
        logger.sensors_logger.debug("Pimoroni BME680 Gas keep alive started")
        while True:
            if not self.pause_gas_keep_alive:
                self.sensor.get_sensor_data()
            else:
                sleep(1)
            sleep(1)

    def temperature(self):
        """ Returns Temperature as a Float. """
        self.pause_gas_keep_alive = True
        try:
            self.sensor.get_sensor_data()
            temp_var = float(self.sensor.data.temperature)
        except Exception as error:
            temp_var = 0.0
            logger.sensors_logger.error("Pimoroni BME680 Temperature - Failed: " + str(error))

        self.pause_gas_keep_alive = False
        return round(temp_var, round_decimal_to)

    def pressure(self):
        """ Returns Pressure as a Integer. """
        self.pause_gas_keep_alive = True
        try:
            self.sensor.get_sensor_data()
            pressure_hpa = self.sensor.data.pressure
        except Exception as error:
            pressure_hpa = 0
            logger.sensors_logger.error("Pimoroni BME680 Pressure - Failed: " + str(error))

        self.pause_gas_keep_alive = False
        return int(pressure_hpa)

    def humidity(self):
        """ Returns Humidity as a Float. """
        self.pause_gas_keep_alive = True
        try:
            var_humidity = self.sensor.data.humidity
        except Exception as error:
            var_humidity = 0.0
            logger.sensors_logger.error("Pimoroni BME680 Humidity - Failed: " + str(error))

        self.pause_gas_keep_alive = False
        return round(var_humidity, round_decimal_to)

    def gas_resistance_index(self):
        """ Returns Gas Resistance Index as a float in kΩ. """
        self.pause_gas_keep_alive = True
        try:
            self.sensor.get_sensor_data()
            gas_var = round(self.sensor.data.gas_resistance / 1000, round_decimal_to)
        except Exception as error:
            gas_var = 0.0
            logger.sensors_logger.error("Pimoroni BME680 GAS Resistance - Failed: " + str(error))

        self.pause_gas_keep_alive = False
        return gas_var
