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


class CreateCheckinConfiguration(CreateGeneralConfiguration):
    """ Creates the Checkin Configuration object and loads settings from file (by default). """

    def __init__(self, load_from_file=True):
        CreateGeneralConfiguration.__init__(self, file_locations.checkin_configuration, load_from_file=load_from_file)
        self.config_file_header = "Enable = 1 & Disable = 0"
        self.valid_setting_count = 4
        self.config_settings_names = [
            "Enable Check-Ins Server", "Count Sensors Checked-In the past X Days", "Offset Date Stamp by X Hours",
            "Delete sensors with checkin older then X Days"
        ]

        self.enable_checkin_recording = 0
        self.count_contact_days = 7.0
        self.hour_offset = 0.0
        self.delete_sensors_older_days = 365.0

        self.update_configuration_settings_list()
        if load_from_file:
            self._init_config_variables()
            self._update_variables_from_settings_list()

    def set_config_with_str(self, config_file_text):
        super().set_config_with_str(config_file_text)
        self._update_variables_from_settings_list()

    def update_with_html_request(self, html_request, skip_all_but_delete_setting=False):
        """ Updates the Checkin configuration based on provided HTML configuration data. """
        logger.network_logger.debug("Starting HTML Checkin Configuration Update Check")

        if not skip_all_but_delete_setting:
            self.enable_checkin_recording = 0
            if html_request.form.get("enable_checkin") is not None:
                self.enable_checkin_recording = 1
            if html_request.form.get("contact_in_past_days") is not None:
                self.count_contact_days = float(html_request.form.get("contact_in_past_days"))
            if html_request.form.get("checkin_hour_offset") is not None:
                self.hour_offset = float(html_request.form.get("checkin_hour_offset"))
        if html_request.form.get("delete_sensors_older_days") is not None:
            self.delete_sensors_older_days = float(html_request.form.get("delete_sensors_older_days"))
        self.update_configuration_settings_list()

    def update_configuration_settings_list(self):
        """ Set's config_settings variable list based on current settings. """

        self.config_settings = [
            str(self.enable_checkin_recording), str(self.count_contact_days), str(self.hour_offset),
            str(self.delete_sensors_older_days)
        ]

    def _update_variables_from_settings_list(self):
        try:
            self.enable_checkin_recording = int(self.config_settings[0])
            self.count_contact_days = float(self.config_settings[1])
            self.hour_offset = float(self.config_settings[2])
            self.delete_sensors_older_days = float(self.config_settings[3])
        except Exception as error:
            logger.primary_logger.debug("Checkin Config: " + str(error))
            self.update_configuration_settings_list()
            if self.load_from_file:
                logger.primary_logger.info("Saving Checkin Configuration.")
                self.save_config_to_file()
