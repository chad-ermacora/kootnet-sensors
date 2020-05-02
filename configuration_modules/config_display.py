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
from operations_modules.app_cached_variables import CreateDisplaySensorsVariables


class CreateDisplayConfiguration(CreateGeneralConfiguration):
    """ Creates the Primary Configuration object and loads settings from file (by default). """

    def __init__(self, load_from_file=True):
        CreateGeneralConfiguration.__init__(self, file_locations.display_config, load_from_file=load_from_file)
        self.config_file_header = "Enable = 1 & Disable = 0"
        self.valid_setting_count = 1
        self.config_settings_names = ["Enable Display"]

        self.display_variables = CreateDisplaySensorsVariables()

        self.minutes_between_display = 60
        self.display_type = self.display_variables.display_type_numerical


        self._update_configuration_settings_list()
        if load_from_file:
            self._init_config_variables()
            self._update_variables_from_settings_list()

    def set_config_with_str(self, config_file_text):
        super().set_config_with_str(config_file_text)
        self._update_variables_from_settings_list()

    def update_with_html_request(self, html_request):
        """ Updates the Display configuration based on provided HTML configuration data. """
        logger.network_logger.debug("Starting HTML Display Configuration Update Check")

        self.minutes_between_display = 60
        if html_request.form.get("display_interval_delay_min") is not None:
            try:
                new_minutes = html_request.form.get("display_interval_delay_min")
                if type(new_minutes) is int:
                    print("Interval is a int")
                    self.minutes_between_display = new_minutes
            except Exception as error:
                logger.network_logger.error("Error setting Display delay minutes: " + str(error))
                self.minutes_between_display = 60

        self._update_configuration_settings_list()

    def _update_configuration_settings_list(self):
        """ Set's config_settings variable list based on current settings. """
        self.config_settings = [str(self.enable_debug_logging), str(self.enable_display),
                                str(self.enable_interval_recording), str(self.enable_trigger_recording),
                                str(self.sleep_duration_interval), str(self.enable_custom_temp),
                                str(self.temperature_offset), str(self.web_portal_port)]

    def _update_variables_from_settings_list(self):
        bad_load = 0
        try:
            self.enable_debug_logging = int(self.config_settings[0])
            self.enable_display = int(self.config_settings[1])
            self.enable_interval_recording = int(self.config_settings[2])
            self.enable_trigger_recording = int(self.config_settings[3])
            self.sleep_duration_interval = float(self.config_settings[4])
            self.enable_custom_temp = int(self.config_settings[5])
            self.temperature_offset = float(self.config_settings[6])
        except Exception as error:
            if self.load_from_file:
                log_msg = "Invalid Settings detected for " + self.config_file_location + ": "
                logger.primary_logger.error(log_msg + str(error))
            bad_load += 100

        if bad_load < 99:
            try:
                self.web_portal_port = int(self.config_settings[7])
            except Exception as error:
                if self.load_from_file:
                    logger.primary_logger.error("HTTPS Web Portal port number not found, using default.")
                    logger.primary_logger.debug(str(error))
                bad_load += 1

        if bad_load:
            self._update_configuration_settings_list()
            if self.load_from_file:
                logger.primary_logger.info("Saving Primary Configuration.")
                self.save_config_to_file()
