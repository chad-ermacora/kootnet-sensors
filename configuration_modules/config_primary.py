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
from operations_modules import logger
from operations_modules import file_locations
from operations_modules.app_generic_functions import CreateGeneralConfiguration
from operations_modules import app_cached_variables


class CreatePrimaryConfiguration(CreateGeneralConfiguration):
    """ Creates the Primary Configuration object and loads settings from file (by default). """

    def __init__(self, load_from_file=True):
        CreateGeneralConfiguration.__init__(self, file_locations.primary_config, load_from_file=load_from_file)
        self.config_file_header = "Enable = 1 & Disable = 0"
        self.valid_setting_count = 9
        self.config_settings_names = [
            "HTTPS Port Number (Default is 10065)", "Enable Debug Logging", "Enable Custom Temperature Offset",
            "Current Temperature Offset", "Enable Temperature Compensation Factor", "Temperature Compensation Factor",
            "Enable Sensor Check-Ins", "Checkin URL", "Checkin Every X Hours"
        ]

        self.enable_checkin = 1
        self.sensor_id = app_cached_variables.tmp_sensor_id
        self.checkin_wait_in_hours = 24
        self.checkin_url = "server.dragonwarz.net:10065"

        self.enable_debug_logging = 0

        self.enable_custom_temp = 0
        self.temperature_offset = 0.0
        self.enable_temperature_comp_factor = 0
        self.temperature_comp_factor = 0.0

        self.flask_http_ip = ""
        self.web_portal_port = 10065

        self.update_configuration_settings_list()
        if load_from_file:
            self._init_config_variables()
            self._update_variables_from_settings_list()

    def set_config_with_str(self, config_file_text):
        super().set_config_with_str(config_file_text)
        self._update_variables_from_settings_list()

    def update_with_html_request(self, html_request):
        """ Updates the primary configuration based on provided HTML configuration data. """
        logger.network_logger.debug("Starting HTML Primary Configuration Update Check")

        self.enable_debug_logging = 0
        self.enable_custom_temp = 0
        self.enable_temperature_comp_factor = 0
        self.enable_checkin = 0

        if html_request.form.get("debug_logging") is not None:
            self.enable_debug_logging = 1
            logger.set_logging_level(debug_enabled=True)
        else:
            logger.set_logging_level(debug_enabled=False)

        if html_request.form.get("enable_custom_temp_offset") is not None:
            new_temp = float(html_request.form.get("custom_temperature_offset"))
            self.enable_custom_temp = 1
            self.temperature_offset = new_temp

        if html_request.form.get("enable_custom_temp_comp") is not None:
            new_temp_comp = float(html_request.form.get("custom_temperature_comp"))
            self.enable_temperature_comp_factor = 1
            self.temperature_comp_factor = new_temp_comp

        if html_request.form.get("ip_web_port") is not None:
            self.web_portal_port = int(html_request.form.get("ip_web_port"))

        if html_request.form.get("enable_checkin") is not None:
            self.enable_checkin = 1
        if html_request.form.get("checkin_hours") is not None:
            self.checkin_wait_in_hours = float(html_request.form.get("checkin_hours"))
        if html_request.form.get("checkin_address") is not None:
            self.checkin_url = str(html_request.form.get("checkin_address")).strip()
            if ":" not in self.checkin_url:
                self.checkin_url = self.checkin_url + ":10065"
        self.update_configuration_settings_list()

    def update_configuration_settings_list(self):
        """ Set's config_settings variable list based on current settings. """
        self.config_settings = [
            str(self.web_portal_port), str(self.enable_debug_logging), str(self.enable_custom_temp),
            str(self.temperature_offset), str(self.enable_temperature_comp_factor), str(self.temperature_comp_factor),
            str(self.enable_checkin), str(self.checkin_url), str(self.checkin_wait_in_hours)
        ]

    def _update_variables_from_settings_list(self):
        try:
            self.web_portal_port = int(self.config_settings[0])
            self.enable_debug_logging = int(self.config_settings[1])
            self.enable_custom_temp = int(self.config_settings[2])
            self.temperature_offset = float(self.config_settings[3])
            self.enable_temperature_comp_factor = int(self.config_settings[4])
            self.temperature_comp_factor = float(self.config_settings[5])
            self.enable_checkin = int(self.config_settings[6])
            self.checkin_url = self.config_settings[7].strip()
            self.checkin_wait_in_hours = float(self.config_settings[8].strip())
        except Exception as error:
            if self.load_from_file:
                logger.primary_logger.debug("Primary Config: " + str(error))
            self.update_configuration_settings_list()
            if self.load_from_file:
                logger.primary_logger.info("Saving Primary Configuration.")
                self.save_config_to_file()
