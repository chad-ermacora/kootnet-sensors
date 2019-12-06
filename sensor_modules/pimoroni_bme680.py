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
from operations_modules import app_config_access

round_decimal_to = 5
readings_update_threshold_sec = 0.25
pause_sensor_during_access_sec = 0.05
gas_keep_alive_update_sec = 1


class CreateBME680:
    """ Creates Function access to the Pimoroni BME680. """

    def __init__(self):
        self.pause_sensor_access = False
        self.readings_last_updated = time.time()

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
            self._update_sensor_readings()
            time.sleep(gas_keep_alive_update_sec)

    def _update_sensor_readings(self):
        if (time.time() - self.readings_last_updated) > readings_update_threshold_sec:
            update_readings = True
            while self.pause_sensor_access:
                update_readings = False
                time.sleep(pause_sensor_during_access_sec)
            if update_readings:
                self.pause_sensor_access = True
                try:
                    self.sensor.get_sensor_data()
                    self.readings_last_updated = time.time()
                except Exception as error:
                    logger.sensors_logger.error("Pimoroni BME680 Sensor Update - Failed: " + str(error))
                    time.sleep(1)
                self.pause_sensor_access = False

    def temperature(self):
        """ Returns Temperature as a Float. """
        self._update_sensor_readings()
        try:
            temp_var = float(self.sensor.data.temperature)
        except Exception as error:
            temp_var = 0.0
            logger.sensors_logger.error("Pimoroni BME680 Temperature - Failed: " + str(error))
        return round(temp_var, round_decimal_to)

    def pressure(self):
        """ Returns Pressure as a Integer. """
        self._update_sensor_readings()
        try:
            pressure_hpa = self.sensor.data.pressure
        except Exception as error:
            pressure_hpa = 0
            logger.sensors_logger.error("Pimoroni BME680 Pressure - Failed: " + str(error))
        return int(pressure_hpa)

    def humidity(self):
        """ Returns Humidity as a Float. """
        self._update_sensor_readings()
        try:
            var_humidity = self.sensor.data.humidity
        except Exception as error:
            var_humidity = 0.0
            logger.sensors_logger.error("Pimoroni BME680 Humidity - Failed: " + str(error))
        return round(var_humidity, round_decimal_to)

    def gas_resistance_index(self):
        """ Returns Gas Resistance Index as a float in kΩ. """
        self._update_sensor_readings()
        try:
            gas_var = round(self.sensor.data.gas_resistance / 1000, round_decimal_to)
        except Exception as error:
            gas_var = 0.0
            logger.sensors_logger.error("Pimoroni BME680 GAS Resistance - Failed: " + str(error))
        return gas_var
