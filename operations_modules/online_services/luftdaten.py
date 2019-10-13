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
import os
from time import sleep
from operations_modules import logger
from operations_modules import file_locations
from operations_modules import app_generic_functions
from operations_modules import software_version
from operations_modules import app_config_access
from operations_modules.app_validation_checks import valid_sensor_reading
from sensor_modules import sensor_access

# Luftdaten URL
luftdaten_url = "https://api.luftdaten.info/v1/push-sensor-data/"
madavi_url = "https://api-rrd.madavi.de/data.php"


class CreateLuftdatenConfig:
    """ Creates a Luftdaten Configuration object. """

    def __init__(self):
        sw_version_text_list = software_version.version.split(".")
        sw_version_text = str(sw_version_text_list[0]) + "." + str(sw_version_text_list[1])
        self.return_software_version = "Kootnet Sensors " + sw_version_text

        self.luftdaten_enabled = 0
        self.interval_seconds = 180
        self.station_id = self._get_cpu_serial()

        self.bad_load = False

    def get_configuration_str(self):
        """ Returns Luftdaten settings ready to be written to the configuration file. """
        config_str = "Enable = 1 & Disable = 0\n" + \
                     str(self.luftdaten_enabled) + " = Enable Luftdaten\n" + \
                     str(self.interval_seconds) + " = Send to Server in Seconds"
        return config_str

    def update_luftdaten_html(self, html_request):
        """ Updates & Writes Luftdaten settings based on provided HTML request. """
        if html_request.form.get("enable_luftdaten") is not None:
            self.luftdaten_enabled = 1
        else:
            self.luftdaten_enabled = 0
        if html_request.form.get("station_interval") is not None:
            self.interval_seconds = float(html_request.form.get("station_interval"))
        self.write_config_to_file()

    def update_settings_from_file(self, file_content=None, skip_write=False):
        """
        Updates Luftdaten settings based on saved configuration file.  Creates Default file if missing.
        """
        if os.path.isfile(file_locations.luftdaten_config) or skip_write:
            if file_content is None:
                loaded_configuration_raw = app_generic_functions.get_file_content(file_locations.luftdaten_config)
            else:
                loaded_configuration_raw = file_content
            configuration_lines = loaded_configuration_raw.split("\n")

            try:
                if int(configuration_lines[1][0]):
                    self.luftdaten_enabled = 1
                else:
                    self.luftdaten_enabled = 0
                try:
                    self.interval_seconds = float(configuration_lines[2].split("=")[0].strip())
                except Exception as error:
                    logger.primary_logger.warning("Luftdaten - Interval Error from file: " + str(error))
                    self.interval_seconds = 300
            except Exception as error:
                if not skip_write:
                    self.write_config_to_file()
                    log_msg = "Luftdaten - Problem loading Configuration file, using 1 or more Defaults: " + str(error)
                    logger.primary_logger.warning(log_msg)
                else:
                    self.bad_load = True
        else:
            if not skip_write:
                logger.primary_logger.info("Luftdaten - Configuration file not found: Saving Default")
                self.write_config_to_file()

    def write_config_to_file(self):
        """ Writes current Luftdaten settings to file. """
        config_str = self.get_configuration_str()
        app_generic_functions.write_file_to_disk(file_locations.luftdaten_config, config_str)

    def start_luftdaten(self):
        """ Sends compatible sensor readings to Luftdaten every X seconds based on set Interval. """
        while True:
            no_sensors = True
            try:
                if app_config_access.installed_sensors.pimoroni_bmp280 or \
                        app_config_access.installed_sensors.pimoroni_enviro:
                    no_sensors = False
                    self._bmp280()
                if app_config_access.installed_sensors.pimoroni_bme680 or \
                        app_config_access.installed_sensors.pimoroni_enviroplus:
                    no_sensors = False
                    self._bme280()
                if app_config_access.installed_sensors.pimoroni_pms5003:
                    no_sensors = False
                    self._pms5003()
            except Exception as error:
                logger.network_logger.error("Luftdaten - Error Processing Data")
                logger.network_logger.debug("Luftdaten - Detailed Error: " + str(error))

            if no_sensors:
                message = "Luftdaten - No further updates will be attempted: No Compatible Sensors"
                logger.network_logger.warning(message)
                while True:
                    sleep(3600)
            sleep(self.interval_seconds)

    # extracts serial from cpuinfo
    @staticmethod
    def _get_cpu_serial():
        try:
            with open('/proc/cpuinfo', 'r') as f:
                for line in f:
                    if line[0:6] == 'Serial':
                        return line.split(":")[1].strip()
        except Exception as error:
            logger.primary_logger.error("Luftdaten - Unable to get CPU Serial: " + str(error))
            return "35505FFFF"

    def _bmp280(self):
        temperature = float(self._get_temperature())
        pressure = float(sensor_access.get_pressure()) * 100.0

        headers = {"X-PIN": "3",
                   "X-Sensor": "raspi-" + self.station_id,
                   "Content-Type": "application/json",
                   "cache-control": "no-cache"}

        post_reply = requests.post(url=luftdaten_url,
                                   json={"software_version": self.return_software_version, "sensordatavalues": [
                                       {"value_type": "temperature", "value": str(temperature)},
                                       {"value_type": "pressure", "value": str(pressure)}]},
                                   headers=headers)
        if post_reply.ok:
            logger.network_logger.debug("Luftdaten - BMP280 OK - Status Code: " + str(post_reply.status_code))
        else:
            logger.network_logger.warning("Luftdaten - BMP280 Failed - Status Code: " + str(post_reply.status_code))

    def _bme280(self):
        temperature = self._get_temperature()
        pressure = sensor_access.get_pressure() * 100

        headers = {"X-PIN": "11",
                   "X-Sensor": "raspi-" + self.station_id,
                   "Content-Type": "application/json",
                   "cache-control": "no-cache"}

        post_reply = requests.post(url=luftdaten_url,
                                   json={"software_version": self.return_software_version, "sensordatavalues": [
                                       {"value_type": "temperature", "value": str(temperature)},
                                       {"value_type": "pressure", "value": str(pressure)},
                                       {"value_type": "humidity", "value": str(sensor_access.get_humidity())}]},
                                   headers=headers)
        if post_reply.ok:
            logger.network_logger.debug("Luftdaten - BME280 OK - Status Code: " + str(post_reply.status_code))
        else:
            log_msg = "Luftdaten - BME280 Failed - Status Code: " + str(post_reply.status_code) + " : "
            logger.network_logger.warning(log_msg + str(post_reply.text))

    def _pms5003(self):
        pm10_reading = str(sensor_access.get_particulate_matter_10())
        pm25_reading = str(sensor_access.get_particulate_matter_2_5())
        headers = {"X-PIN": "1",
                   "X-Sensor": "raspi-" + self.station_id,
                   "Content-Type": "application/json",
                   "cache-control": "no-cache"}

        post_reply = requests.post(url=luftdaten_url,
                                   json={"software_version": self.return_software_version, "sensordatavalues": [
                                       {"value_type": "P1", "value": pm10_reading},
                                       {"value_type": "P2", "value": pm25_reading}]},
                                   headers=headers)
        if post_reply.ok:
            logger.network_logger.debug("Luftdaten - PMS5003 OK - Status Code: " + str(post_reply.status_code))
        else:
            logger.network_logger.warning("Luftdaten - PMS5003 Failed - Status Code: " + str(post_reply.status_code))

    @staticmethod
    def _get_temperature():
        try:
            temp_c = sensor_access.get_sensor_temperature()
            if valid_sensor_reading(temp_c) and app_config_access.current_config.enable_custom_temp:
                temp_c = temp_c + app_config_access.current_config.temperature_offset
            return temp_c
        except Exception as error:
            logger.network_logger.warning("Luftdaten - Get Temperature Failed, returning 0.0: " + str(error))
            return 0.0
