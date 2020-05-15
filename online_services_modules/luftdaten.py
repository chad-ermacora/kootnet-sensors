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
from operations_modules.app_config_access import installed_sensors, luftdaten_config
from sensor_modules import sensor_access


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
            if installed_sensors.pimoroni_pms5003:
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
    temperature = float(sensor_access.get_sensor_temperature())
    pressure = float(sensor_access.get_pressure()) * 100.0

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


def _bme280():
    temperature = sensor_access.get_sensor_temperature()
    pressure = sensor_access.get_pressure() * 100

    headers = {"X-PIN": "11",
               "X-Sensor": "raspi-" + luftdaten_config.station_id,
               "Content-Type": "application/json",
               "cache-control": "no-cache"}

    post_reply = requests.post(url=luftdaten_config.luftdaten_url,
                               json={"software_version": luftdaten_config.return_software_version, "sensordatavalues": [
                                   {"value_type": "temperature", "value": str(temperature)},
                                   {"value_type": "pressure", "value": str(pressure)},
                                   {"value_type": "humidity", "value": str(sensor_access.get_humidity())}]},
                               headers=headers)
    if post_reply.ok:
        logger.network_logger.debug("Luftdaten - BME280 OK - Status Code: " + str(post_reply.status_code))
    else:
        log_msg = "Luftdaten - BME280 Failed - Status Code: " + str(post_reply.status_code) + " : "
        logger.network_logger.warning(log_msg + str(post_reply.text))


def _pms5003():
    pm_readings = sensor_access.get_particulate_matter(return_as_dictionary=True)
    pm10_reading = ""
    pm25_reading = ""
    if pm_readings != app_cached_variables.no_sensor_present:
        if app_cached_variables.database_variables.particulate_matter_10 in pm_readings:
            pm10_reading = str(pm_readings[app_cached_variables.database_variables.particulate_matter_10])
        if app_cached_variables.database_variables.particulate_matter_2_5 in pm_readings:
            pm25_reading = str(pm_readings[app_cached_variables.database_variables.particulate_matter_2_5])
    headers = {"X-PIN": "1",
               "X-Sensor": "raspi-" + luftdaten_config.station_id,
               "Content-Type": "application/json",
               "cache-control": "no-cache"}

    post_reply = requests.post(url=luftdaten_config.luftdaten_url,
                               json={"software_version": luftdaten_config.return_software_version, "sensordatavalues": [
                                   {"value_type": "P1", "value": pm10_reading},
                                   {"value_type": "P2", "value": pm25_reading}]},
                               headers=headers)
    if post_reply.ok:
        logger.network_logger.debug("Luftdaten - PMS5003 OK - Status Code: " + str(post_reply.status_code))
    else:
        logger.network_logger.warning("Luftdaten - PMS5003 Failed - Status Code: " + str(post_reply.status_code))
