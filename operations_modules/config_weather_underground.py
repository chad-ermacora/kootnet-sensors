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
from operations_modules import file_locations, logger
from operations_modules.app_generic_functions import CreateGeneralConfiguration


class CreateWeatherUndergroundConfiguration(CreateGeneralConfiguration):
    """ Creates the Weather Underground Configuration object and loads settings from file (by default). """

    def __init__(self, load_from_file=True):
        CreateGeneralConfiguration.__init__(self, file_locations.weather_underground_config)
        self.config_file_header = "Enable = 1 & Disable = 0"
        self.valid_setting_count = 6
        self.config_settings_names = ["Enable Weather Underground", "Send to Server in Seconds",
                                      "Sensor is Outdoors", "Weather Underground Station ID",
                                      "Weather Underground Station Key", "Enable Rapid Fire Updates"]

        self.weather_underground_enabled = 0
        self.interval_seconds = 900.0
        self.outdoor_sensor = 1
        self.station_id = "NA"
        self.station_key = "NA"
        self.wu_rapid_fire_enabled = 0

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

        self._update_configuration_settings_list()
        if load_from_file:
            self._init_config_variables()
            self._update_variables_from_settings_list()

    def set_config_with_str(self, config_file_text):
        super().set_config_with_str(config_file_text)
        self._update_variables_from_settings_list()

    def update_with_html_request(self, html_request):
        """ Updates the Weather Underground configuration based on provided HTML configuration data. """
        logger.network_logger.debug("Starting HTML Primary Configuration Update Check")
        self.weather_underground_enabled = 0
        if html_request.form.get("enable_weather_underground") is not None:
            self.weather_underground_enabled = 1
            self.wu_rapid_fire_enabled = 0
            if html_request.form.get("enable_wu_rapid_fire") is not None:
                self.wu_rapid_fire_enabled = 1

            self.outdoor_sensor = 0
            if html_request.form.get("weather_underground_outdoor") is not None:
                self.outdoor_sensor = 1

            if html_request.form.get("weather_underground_interval") is not None:
                self.interval_seconds = float(html_request.form.get("weather_underground_interval"))
                if self.interval_seconds < 10.0:
                    self.interval_seconds = 10.0

            self.station_id = "NA"
            if html_request.form.get("station_id") is not None:
                self.station_id = str(html_request.form.get("station_id")).strip()

            self.station_key = ""
            if html_request.form.get("station_key") is not None and html_request.form.get("station_key") is not "":
                self.station_key = str(html_request.form.get("station_key")).strip()
        self._update_configuration_settings_list()

    def _update_configuration_settings_list(self):
        """ Set's config_settings variable list based on current settings. """
        self.config_settings = [str(self.weather_underground_enabled), str(self.interval_seconds),
                                str(self.outdoor_sensor), str(self.station_id),
                                str(self.station_key), str(self.wu_rapid_fire_enabled)]

    def _update_variables_from_settings_list(self):
        if self.valid_setting_count == len(self.config_settings):
            try:
                self.weather_underground_enabled = int(self.config_settings[0])
                self.interval_seconds = float(self.config_settings[1])
                self.outdoor_sensor = int(self.config_settings[2])
                self.station_id = str(self.config_settings[3])
                self.station_key = str(self.config_settings[4])
                self.wu_rapid_fire_enabled = int(self.config_settings[5])
            except Exception as error:
                log_msg = "Invalid Settings detected for " + self.config_file_location + ": "
                logger.primary_logger.warning(log_msg + str(error))
        else:
            log_msg = "Invalid number of setting for "
            logger.primary_logger.warning(log_msg + str(self.config_file_location))
