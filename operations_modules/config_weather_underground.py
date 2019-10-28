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
import os
from operations_modules import file_locations, logger
from operations_modules.app_generic_functions import get_file_content, write_file_to_disk


class CreateWeatherUndergroundConfig:
    """ Creates a Weather Underground Configuration object. """

    def __init__(self):
        self.weather_underground_enabled = 0
        self.wu_rapid_fire_enabled = 0
        self.interval_seconds = 900
        self.outdoor_sensor = 1
        self.station_id = "NA"
        self.station_key = "NA"

        # Weather Underground URL Variables
        self.wu_main_url_start = "https://weatherstation.wunderground.com/weatherstation/updateweatherstation.php?"
        self.wu_rapid_fire_url_start = "https://rtupdate.wunderground.com/weatherstation/updateweatherstation.php?"
        self.wu_rapid_fire_url_end = "&realtime=1&rtfreq="

        self.wu_id = "ID="
        self.wu_key = "&PASSWORD="
        self.wu_utc_datetime = "&dateutc=now"
        self.wu_software_version = "&softwaretype=Kootnet%20Sensors%20"
        self.wu_action = "&action=updateraw"

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
                    logger.primary_logger.warning("Weather Underground - Interval Error from file: " + str(error))
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
                    log_msg = "Weather Underground - Problem loading Configuration file, using 1 or more Defaults: "
                    logger.primary_logger.warning(log_msg + str(error))
                else:
                    self.bad_config_load = True
        else:
            if not skip_write:
                logger.primary_logger.info("Weather Underground - Configuration file not found: Saving Default")
                self.write_config_to_file()

    def write_config_to_file(self):
        """ Writes current Weather Underground settings to file. """
        config_str = self.get_configuration_str()
        write_file_to_disk(file_locations.weather_underground_config, config_str)
