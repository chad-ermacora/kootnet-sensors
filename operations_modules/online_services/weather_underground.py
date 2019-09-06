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
    def __init__(self, sensor_access):
        self.sensor_access = sensor_access

        self.weather_underground_enabled = 0
        self.wu_rapid_fire_enabled = 0
        self.interval_seconds = 900
        self.outdoor_sensor = 1
        self.station_id = "NA"
        self.station_key = "NA"
        self._update_settings_from_file()

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

    def update_weather_underground_html(self, html_request):
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

        self.write_config_to_file()

    def _update_settings_from_file(self):
        """
        Updates Weather Underground settings based on saved configuration file.  Creates Default file if missing.
        """
        if os.path.isfile(file_locations.weather_underground_config):
            loaded_configuration_raw = app_generic_functions.get_file_content(file_locations.weather_underground_config)
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
                self.write_config_to_file()
                logger.primary_logger.warning("Problem loading Online Services Configuration file - " +
                                              "Using 1 or more Defaults: " + str(error))
        else:
            logger.primary_logger.warning("No Online Service configuration file found - Saving Default")
            self.write_config_to_file()

    def write_config_to_file(self):
        """ Writes current Weather Underground settings to file. """
        config_str = self.get_configuration_str()
        app_generic_functions.write_file_to_disk(file_locations.weather_underground_config, config_str)

    def start_weather_underground(self):
        """ Sends compatible sensor readings to Weather Underground every X seconds based on set Interval. """
        if not app_config_access.wu_thread_running:
            app_config_access.wu_thread_running = True
            # Sleep 5 seconds before starting
            # So it doesn't try to access the sensors at the same time as the recording services on boot
            sleep(5)
            while True:
                sensor_readings = self.sensor_access.get_weather_underground_readings(self.outdoor_sensor)
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

                        # logger.network_logger.debug("New Underground URL: " + url)
                        html_get_response = requests.get(url=url)

                        if html_get_response.status_code == 200:
                            logger.network_logger.debug("Sensors sent to Weather Underground OK")
                        elif html_get_response.status_code == 401:
                            logger.network_logger.error(
                                "Failed to send update to Weather Underground: Bad Station ID or Key")
                        elif html_get_response.status_code == 400:
                            logger.network_logger.error("Failed to send update to Weather Underground: Invalid Options")
                        else:
                            logger.network_logger.error("Failed to send update to Weather Underground: Unknown Error " +
                                                        str(html_get_response))
                    except Exception as error:
                        logger.network_logger.error("Error sending data to Weather Underground: " + str(error))
                else:
                    logger.network_logger.warning("Weather Underground not Updated - " +
                                                  "No Compatible Sensors Selected in Installed Sensors Configuration")
                    while True:
                        sleep(3600)
                sleep(self.interval_seconds)
