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
from operations_modules.app_generic_classes import CreateGeneralConfiguration


class CreateURLConfiguration(CreateGeneralConfiguration):
    """ Creates the URL Configuration object and loads settings from file (by default). """

    def __init__(self, load_from_file=True):
        CreateGeneralConfiguration.__init__(self, file_locations.urls_configuration, load_from_file=load_from_file)
        self.config_file_header = "Enable = 1 and Disable = 0"
        self.valid_setting_count = 2
        self.config_settings_names = [
            "Update Server", "Checkin Server"
        ]

        self.url_update_server = "https://kootenay-networks.com/installers/"
        self.url_checkin_server = "server.dragonwarz.net"

        self.update_configuration_settings_list()
        if load_from_file:
            self._init_config_variables()
            self._update_variables_from_settings_list()

    def set_config_with_str(self, config_file_text):
        super().set_config_with_str(config_file_text)
        self._update_variables_from_settings_list()

    def update_with_html_request(self, html_request):
        """ Updates the URL configuration based on provided HTML configuration data. """
        logger.network_logger.debug("Starting HTML URL Configuration Update Check")

        if html_request.form.get("update_server_address") is not None:
            self.url_update_server = self.ensure_http_in_url(html_request.form.get("update_server_address"))
            if self.url_update_server[-1] != "/":
                self.url_update_server += "/"

        if html_request.form.get("checkin_address") is not None:
            self.url_checkin_server = html_request.form.get("checkin_address")
        self.update_configuration_settings_list()

    def update_configuration_settings_list(self):
        """ Set's config_settings variable list based on current settings. """

        self.config_settings = [
            str(self.url_update_server), str(self.url_checkin_server)
        ]

    def _update_variables_from_settings_list(self):
        try:
            self.url_update_server = self.config_settings[0].strip()
            self.url_checkin_server = self.config_settings[1].strip()

        except Exception as error:
            if self.load_from_file:
                logger.primary_logger.debug("URLs Config: " + str(error))
            self.update_configuration_settings_list()
            if self.load_from_file:
                logger.primary_logger.info("Saving URLs Configuration.")
                self.save_config_to_file()

    @staticmethod
    def ensure_http_in_url(url_address):
        url_address = url_address.strip()
        if "http" not in url_address.lower():
            url_address = "https://" + url_address
        return url_address

    def reset_urls_to_default(self):
        self.__init__(load_from_file=False)
        self.save_config_to_file()
