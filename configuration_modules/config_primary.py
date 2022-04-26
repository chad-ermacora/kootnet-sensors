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
import re
from operations_modules import logger
from operations_modules import file_locations
from operations_modules.app_generic_classes import CreateGeneralConfiguration
from operations_modules import app_cached_variables
from operations_modules.app_validation_checks import hostname_is_valid


class CreatePrimaryConfiguration(CreateGeneralConfiguration):
    """ Creates the Primary Configuration object and loads settings from file (by default). """

    def __init__(self, load_from_file=True):
        CreateGeneralConfiguration.__init__(self, file_locations.primary_config, load_from_file=load_from_file)
        self.config_file_header = "Enable = 1 and Disable = 0"
        self.valid_setting_count = 3
        self.config_settings_names = [
            "HTTPS port number (Default is 10065)", "Enable debug logging",
            "DateTime offset in hours (Program uses UTC 0)"
        ]

        self.demo_mode = False
        self.sensor_id = app_cached_variables.tmp_sensor_id
        self.flask_http_ip = ""
        self.web_portal_port_changed = 0

        self.enable_debug_logging = 0
        self.utc0_hour_offset = 0.0
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
        logger.debug_enabled = 0
        old_port = self.web_portal_port

        if html_request.form.get("debug_logging") is not None:
            self.enable_debug_logging = 1
            logger.debug_enabled = 1
        logger.set_logging_level()

        hostname = sanitize_text(html_request.form.get("ip_hostname"))
        if hostname_is_valid(hostname) and hostname != app_cached_variables.hostname:
            if app_cached_variables.running_with_root:
                app_cached_variables.hostname = hostname
                os.system("hostnamectl set-hostname " + hostname)

        if html_request.form.get("program_hour_offset") is not None:
            self.utc0_hour_offset = float(html_request.form.get("program_hour_offset"))
        if html_request.form.get("ip_web_port") is not None:
            self.web_portal_port = int(html_request.form.get("ip_web_port"))
            if old_port != self.web_portal_port:
                self.web_portal_port_changed = 1
        self.update_configuration_settings_list()

    def update_configuration_settings_list(self):
        """ Set's config_settings variable list based on current settings. """

        self.config_settings = [
            str(self.web_portal_port), str(self.enable_debug_logging), str(self.utc0_hour_offset)
        ]

    def _update_variables_from_settings_list(self):
        try:
            self.web_portal_port = int(self.config_settings[0])
            self.enable_debug_logging = int(self.config_settings[1])
            self.utc0_hour_offset = float(self.config_settings[2].strip())
        except Exception as error:
            if self.load_from_file:
                logger.primary_logger.debug("Primary Config: " + str(error))
            self.update_configuration_settings_list()
            if self.load_from_file:
                logger.primary_logger.info("Saving Primary Configuration.")
                self.save_config_to_file()


def sanitize_text(text_variable):
    text_variable = str(text_variable)
    final_db_name = ""
    for letter in text_variable:
        if re.match("^[A-Za-z0-9_.-]*$", letter):
            final_db_name += letter
    while ".." in final_db_name:
        final_db_name = final_db_name.replace("..", ".")
    if final_db_name == "":
        final_db_name = "No_Name"
    return final_db_name
