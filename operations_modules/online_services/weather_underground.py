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
from operations_modules.app_generic_functions import get_file_content, write_file_to_disk
from operations_modules.app_validation_checks import valid_sensor_reading
from operations_modules import software_version
from operations_modules import app_config_access

# Weather Underground URL Variables
wu_main_url_start = "https://weatherstation.wunderground.com/weatherstation/updateweatherstation.php?"
wu_rapid_fire_url_start = "https://rtupdate.wunderground.com/weatherstation/updateweatherstation.php?"
wu_rapid_fire_url_end = "&realtime=1&rtfreq="

wu_id = "ID="
wu_key = "&PASSWORD="
wu_utc_datetime = "&dateutc=now"
wu_software_version = "&softwaretype=Kootnet%20Sensors%20"
wu_action = "&action=updateraw"


class CreateWeatherUndergroundConfig:
    """ Creates a Weather Underground Configuration object. """

    def __init__(self):
        self.sensor_access = None

        self.weather_underground_enabled = 0
        self.wu_rapid_fire_enabled = 0
        self.interval_seconds = 900
        self.outdoor_sensor = 1
        self.station_id = "NA"
        self.station_key = "NA"

        self.bad_config_load = False

    def get_configuration_str(self):
        """ Returns Weather Underground settings ready to be written to the configuration file. """
        online_services_config_str = "Enable = 1 & Disable = 0\n" + \
                                     str(self.weather_underground_enabled) + " = Enable Weather Underground\n" + \
                                     str(self.interval_seconds) + " = Send to Server in Seconds\n" + \
                                     str(self.outdoor_sensor) + " = Sensor is Outdoors\n" + \
                                     str(self.station_id) + " = Weather Underground Station ID\n" + \
                                     str(self.station_key) + " = Weather Underground Station Key\n" + \
                                     str(self.wu_rapid_fire_enabled) + " = Enable Rapid Fire Updates"

        return online_services_config_str

    def update_weather_underground_html(self, html_request, skip_write=True):
        """ Updates & Writes Weather Underground settings based on provided HTML request. """
        if html_request.form.get("enable_weather_underground") is not None:
            self.weather_underground_enabled = 1
            if html_request.form.get("enable_wu_rapid_fire") is not None:
                self.wu_rapid_fire_enabled = 1
            else:
                self.wu_rapid_fire_enabled = 0
            if html_request.form.get("weather_underground_outdoor") is not None:
                self.outdoor_sensor = 1
            else:
                self.outdoor_sensor = 0
        else:
            self.weather_underground_enabled = 0

        if html_request.form.get("weather_underground_interval") is not None:
            self.interval_seconds = float(html_request.form.get("weather_underground_interval"))
        if html_request.form.get("station_id") is not None:
            self.station_id = html_request.form.get("station_id").strip()
        if html_request.form.get("station_key") is not None and html_request.form.get("station_key") is not "":
            self.station_key = html_request.form.get("station_key").strip()

        if not skip_write:
            self.write_config_to_file()

    def update_settings_from_file(self, file_content=None, skip_write=False):
        """
        Updates Weather Underground settings based on saved configuration file.  Creates Default file if missing.
        """
        if os.path.isfile(file_locations.weather_underground_config) or skip_write:
            if file_content is None:
                loaded_configuration_raw = get_file_content(file_locations.weather_underground_config)
            else:
                loaded_configuration_raw = file_content

            configuration_lines = loaded_configuration_raw.split("\n")
            try:
                if int(configuration_lines[1][0]):
                    self.weather_underground_enabled = 1
                else:
                    self.weather_underground_enabled = 0

                if int(configuration_lines[3][0]):
                    self.outdoor_sensor = 1
                else:
                    self.outdoor_sensor = 0
                try:
                    self.interval_seconds = float(configuration_lines[2].split("=")[0].strip())
                except Exception as error:
                    logger.primary_logger.warning("Weather Underground Interval Error from file - " + str(error))
                    self.interval_seconds = 300

                self.station_id = configuration_lines[4].split("=")[0].strip()
                self.station_key = configuration_lines[5].split("=")[0].strip()

                if int(configuration_lines[6][0]):
                    self.wu_rapid_fire_enabled = 1
                else:
                    self.wu_rapid_fire_enabled = 0
            except Exception as error:
                if not skip_write:
                    self.write_config_to_file()
                    logger.primary_logger.warning("Problem loading Online Services Configuration file - " +
                                                  "Using 1 or more Defaults: " + str(error))
                else:
                    self.bad_config_load = True
        else:
            if not skip_write:
                logger.primary_logger.info("Weather Underground Configuration file not found - Saving Default")
                self.write_config_to_file()

    def write_config_to_file(self):
        """ Writes current Weather Underground settings to file. """
        config_str = self.get_configuration_str()
        write_file_to_disk(file_locations.weather_underground_config, config_str)

    def start_weather_underground(self):
        """ Sends compatible sensor readings to Weather Underground every X seconds based on set Interval. """
        if not app_config_access.wu_thread_running:
            app_config_access.wu_thread_running = True
            # Sleep 5 seconds before starting
            # So it doesn't try to access the sensors at the same time as the recording services on boot
            sleep(5)
            while True:
                sensor_readings = self.get_weather_underground_readings()
                sw_version_text_list = software_version.version.split(".")
                sw_version_text = str(sw_version_text_list[0]) + "." + str(sw_version_text_list[1])
                if sensor_readings:
                    if self.wu_rapid_fire_enabled:
                        url = wu_rapid_fire_url_start
                    else:
                        url = wu_main_url_start
                    try:
                        url += wu_id + self.station_id + \
                               wu_key + self.station_key + \
                               wu_utc_datetime + \
                               sensor_readings + \
                               wu_software_version + sw_version_text + \
                               wu_action

                        if self.wu_rapid_fire_enabled:
                            url += wu_rapid_fire_url_end + str(self.interval_seconds)

                        # logger.network_logger.debug("New Weather Underground URL: " + url)
                        html_get_response = requests.get(url=url)

                        if html_get_response.status_code == 200:
                            logger.network_logger.debug("Sensors sent to Weather Underground OK")
                        elif html_get_response.status_code == 401:
                            logger.network_logger.error("Weather Underground: Bad Station ID or Key")
                        elif html_get_response.status_code == 400:
                            logger.network_logger.error("Weather Underground: Invalid Options")
                        else:
                            status_code = str(html_get_response.status_code)
                            response_text = str(html_get_response.text)
                            log_msg = "Weather Underground Unknown Error " + status_code + ": " + response_text
                            logger.network_logger.error(log_msg)

                    except Exception as error:
                        logger.network_logger.error("Error sending data to Weather Underground")
                        logger.network_logger.debug("Weather Underground Error: " + str(error))
                else:
                    logger.network_logger.warning("Weather Underground not Updated - No Compatible Sensors")
                    while True:
                        sleep(3600)
                sleep(self.interval_seconds)

    def get_weather_underground_readings(self):
        """
        Returns supported sensor readings for Weather Underground in URL format.
        Example:  &tempf=59.56&humidity=15.65
        """
        round_decimal_to = 5
        return_readings_str = ""

        temp_c = self.sensor_access.get_sensor_temperature()
        if app_config_access.current_config.enable_custom_temp:
            temp_c = temp_c + app_config_access.current_config.temperature_offset

        if valid_sensor_reading(temp_c):
            try:
                temperature_f = (float(temp_c) * (9.0 / 5.0)) + 32.0
                if self.outdoor_sensor:
                    return_readings_str += "&tempf=" + str(round(temperature_f, round_decimal_to))
                else:
                    return_readings_str += "&indoortempf=" + str(round(temperature_f, round_decimal_to))
            except Exception as error:
                log_msg = "Unable to calculate Temperature into fahrenheit for Weather Underground: " + str(error)
                logger.sensors_logger.error(log_msg)

        humidity = self.sensor_access.get_humidity()
        if valid_sensor_reading(humidity):
            if self.outdoor_sensor:
                return_readings_str += "&humidity=" + str(round(humidity, round_decimal_to))
            else:
                return_readings_str += "&indoorhumidity=" + str(round(humidity, round_decimal_to))

        out_door_dew_point = self.sensor_access.get_dew_point()
        if valid_sensor_reading(out_door_dew_point) and self.outdoor_sensor:
            try:
                dew_point_f = (float(out_door_dew_point) * (9.0 / 5.0)) + 32.0
                return_readings_str += "&dewptf=" + str(round(dew_point_f, round_decimal_to))
            except Exception as error:
                log_msg = "Unable to calculate Dew Point into fahrenheit for Weather Underground: " + str(error)
                logger.sensors_logger.error(log_msg)

        pressure_hpa = self.sensor_access.get_pressure()
        if valid_sensor_reading(pressure_hpa):
            try:
                baromin = float(pressure_hpa) * 0.029529983071445
                return_readings_str += "&baromin=" + str(round(baromin, round_decimal_to))
            except Exception as error:
                logger.sensors_logger.error("Unable to calculate Pressure inhg for Weather Underground: " + str(error))

        ultra_violet_index = self.sensor_access.get_ultra_violet_index()
        if valid_sensor_reading(ultra_violet_index):
            return_readings_str += "&UV=" + str(round(ultra_violet_index, round_decimal_to))

        pm_2_5 = self.sensor_access.get_particulate_matter_2_5()
        if valid_sensor_reading(pm_2_5):
            return_readings_str += "&AqPM2.5=" + str(round(pm_2_5, round_decimal_to))

        pm_10 = self.sensor_access.get_particulate_matter_10()
        if valid_sensor_reading(pm_10):
            return_readings_str += "&AqPM10=" + str(round(pm_10, round_decimal_to))
        return return_readings_str
