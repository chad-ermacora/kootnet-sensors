"""
    KootNet Sensors is a collection of programs and scripts to deploy,
    interact with, and collect readings from various Sensors.
    Copyright (C) 2018  Chad Ermacora  chad.ermacora@gmail.com

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
import requests
from time import sleep
from operations_modules import logger
from operations_modules.app_generic_functions import CreateMonitoredThread
from operations_modules import app_cached_variables
from configuration_modules.app_config_access import installed_sensors, luftdaten_config
from sensor_modules import sensor_access

database_variables = app_cached_variables.database_variables


def start_luftdaten_server():
    if luftdaten_config.luftdaten_enabled:
        text_name = "Luftdaten"
        app_cached_variables.luftdaten_thread = CreateMonitoredThread(_luftdaten_server, thread_name=text_name)
    else:
        logger.primary_logger.debug("Luftdaten Disabled in Configuration")


def _luftdaten_server():
    """ Sends compatible sensor readings to Luftdaten every X seconds based on set Interval. """
    app_cached_variables.restart_luftdaten_thread = False
    while not app_cached_variables.restart_luftdaten_thread:
        no_sensors = True
        try:
            if installed_sensors.pimoroni_bmp280 or installed_sensors.pimoroni_enviro:
                no_sensors = False
                _bmp280()
            if installed_sensors.pimoroni_bme680 or installed_sensors.pimoroni_enviroplus:
                no_sensors = False
                _bme280()
            if installed_sensors.pimoroni_pms5003 or installed_sensors.sensirion_sps30:
                no_sensors = False
                _pms5003()
        except Exception as error:
            logger.network_logger.error("Luftdaten - Error Processing Data")
            logger.network_logger.debug("Luftdaten - Detailed Error: " + str(error))

        if no_sensors:
            logger.primary_logger.error("Luftdaten - No Compatible Sensors: No further attempts will be made")
            while not app_cached_variables.restart_luftdaten_thread:
                sleep(5)

        sleep_fraction_interval = 5
        sleep_total = 0
        while sleep_total < luftdaten_config.interval_seconds and not app_cached_variables.restart_luftdaten_thread:
            sleep(sleep_fraction_interval)
            sleep_total += sleep_fraction_interval


def _bmp280():
    try:
        temperature = sensor_access.get_environment_temperature()
        if temperature is not None:
            temperature = temperature[database_variables.env_temperature]
        pressure = sensor_access.get_pressure()
        if pressure is not None:
            pressure = pressure[database_variables.pressure] * 100.0

        headers = {"X-PIN": "3",
                   "X-Sensor": "raspi-" + luftdaten_config.station_id,
                   "Content-Type": "application/json",
                   "cache-control": "no-cache"}

        post_reply = requests.post(url=luftdaten_config.luftdaten_url,
                                   json={"software_version": luftdaten_config.return_software_version, "sensordatavalues": [
                                       {"value_type": "temperature", "value": str(temperature)},
                                       {"value_type": "pressure", "value": str(pressure)}]},
                                   headers=headers)
        if post_reply.ok:
            logger.network_logger.debug("Luftdaten - BMP280 OK - Status Code: " + str(post_reply.status_code))
        else:
            logger.network_logger.warning("Luftdaten - BMP280 Failed - Status Code: " + str(post_reply.status_code))
    except Exception as error:
        logger.network_logger.warning("Luftdaten - BMP280 Failed: " + str(error))


def _bme280():
    try:
        temperature = sensor_access.get_environment_temperature()
        if temperature is not None:
            temperature = temperature[database_variables.env_temperature]
        pressure = sensor_access.get_pressure()
        if pressure is not None:
            pressure = pressure[database_variables.pressure] * 100

        humidity = sensor_access.get_humidity()
        if humidity is not None:
            humidity = humidity[database_variables.humidity]

        headers = {"X-PIN": "11",
                   "X-Sensor": "raspi-" + luftdaten_config.station_id,
                   "Content-Type": "application/json",
                   "cache-control": "no-cache"}

        post_reply = requests.post(url=luftdaten_config.luftdaten_url,
                                   json={"software_version": luftdaten_config.return_software_version,
                                         "sensordatavalues": [
                                             {"value_type": "temperature", "value": str(temperature)},
                                             {"value_type": "pressure", "value": str(pressure)},
                                             {"value_type": "humidity", "value": str(humidity)}]},
                                   headers=headers)
        if post_reply.ok:
            logger.network_logger.debug("Luftdaten - BME280 OK - Status Code: " + str(post_reply.status_code))
        else:
            log_msg = "Luftdaten - BME280 Failed - Status Code: " + str(post_reply.status_code) + " : "
            logger.network_logger.warning(log_msg + str(post_reply.text))
    except Exception as error:
        logger.network_logger.warning("Luftdaten - BME280 Failed: " + str(error))


def _pms5003():
    try:
        pm_readings = sensor_access.get_particulate_matter()
        pm10_reading = 0.0
        pm25_reading = 0.0
        if pm_readings is not None:
            if database_variables.particulate_matter_10 in pm_readings:
                pm10_reading = pm_readings[database_variables.particulate_matter_10]
            if database_variables.particulate_matter_2_5 in pm_readings:
                pm25_reading = pm_readings[database_variables.particulate_matter_2_5]
            headers = {"X-PIN": "1",
                       "X-Sensor": "raspi-" + luftdaten_config.station_id,
                       "Content-Type": "application/json",
                       "cache-control": "no-cache"}

            post_reply = requests.post(url=luftdaten_config.luftdaten_url,
                                       json={"software_version": luftdaten_config.return_software_version,
                                             "sensordatavalues": [{"value_type": "P1", "value": str(pm10_reading)},
                                                                  {"value_type": "P2", "value": str(pm25_reading)}]},
                                       headers=headers)
            if post_reply.ok:
                logger.network_logger.debug("Luftdaten - PMS5003 OK - Status Code: " + str(post_reply.status_code))
            else:
                logger.network_logger.warning("Luftdaten - PMS5003 Failed - Status Code: " + str(post_reply.status_code))
    except Exception as error:
        logger.network_logger.warning("Luftdaten - PMS5003 Failed: " + str(error))
