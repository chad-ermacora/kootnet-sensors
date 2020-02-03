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
from operations_modules.app_generic_functions import CreateGeneralConfiguration, get_file_content


class CreatePrimaryConfiguration(CreateGeneralConfiguration):
    """ Creates the Primary Configuration object and loads settings from file (by default). """

    def __init__(self, load_from_file=True):
        CreateGeneralConfiguration.__init__(self)
        self.config_file_location = file_locations.main_config
        self.config_file_header = "Enable = 1 & Disable = 0"
        self.valid_setting_count = 7
        self.config_settings_names = ["Enable Debug Logging", "Enable Mini Display",
                                      "Interval Recording to SQL Database", "Trigger Recording to SQL Database",
                                      "Recording Interval in Seconds ** Caution **",
                                      "Enable Custom Temperature Offset", "Current Temperature Offset"]
        self.enable_debug_logging = 0
        self.enable_display = 0
        self.enable_interval_recording = 1
        self.enable_trigger_recording = 0
        self.sleep_duration_interval = 300.0
        self.enable_custom_temp = 0
        self.temperature_offset = 0.0

        self._update_configuration_settings_list()
        if load_from_file:
            self._init_config_variables()

    def set_config_with_str(self, config_file_text):
        super().set_config_with_str(config_file_text)
        self._update_variables_from_settings_list()

    def update_with_html_request(self, html_request):
        """ Updates the primary configuration based on provided HTML configuration data. """
        logger.network_logger.debug("Starting HTML Primary Configuration Update Check")
        if html_request.form.get("debug_logging") is not None:
            self.enable_debug_logging = 1
        else:
            self.enable_debug_logging = 0

        if html_request.form.get("enable_display") is not None:
            self.enable_display = 1
        else:
            self.enable_display = 0

        if html_request.form.get("enable_interval_recording") is not None:
            self.enable_interval_recording = 1
        else:
            self.enable_interval_recording = 0
        if html_request.form.get("interval_delay_seconds") is not None:
            new_sleep_duration = float(html_request.form.get("interval_delay_seconds"))
            self.sleep_duration_interval = new_sleep_duration

        if html_request.form.get("enable_trigger_recording") is not None:
            self.enable_trigger_recording = 1
        else:
            self.enable_trigger_recording = 0

        if html_request.form.get("enable_custom_temp_offset") is not None:
            new_temp = float(html_request.form.get("custom_temperature_offset"))
            self.enable_custom_temp = 1
            self.temperature_offset = new_temp
        else:
            self.enable_custom_temp = 0
        self._update_configuration_settings_list()

    def _init_config_variables(self):
        """ Sets configuration settings from file, saves default if missing. """
        try:
            self.set_config_with_str(get_file_content(file_locations.main_config))
        except Exception as error:
            log_msg = "Error setting variables from "
            log_msg2 = "Saving Default Configuration for "
            logger.primary_logger.warning(log_msg + str(self.config_file_location) + " - " + str(error))
            logger.primary_logger.warning(log_msg2 + str(self.config_file_location))
            self.save_config_to_file()

    def _update_configuration_settings_list(self):
        """ Set's config_settings variable list based on current settings. """
        self.config_settings = [str(self.enable_debug_logging), str(self.enable_display),
                                str(self.enable_interval_recording), str(self.enable_trigger_recording),
                                str(self.sleep_duration_interval), str(self.enable_custom_temp),
                                str(self.temperature_offset)]

    def _update_variables_from_settings_list(self):
        if self.valid_setting_count == len(self.config_settings):
            self.enable_debug_logging = int(self.config_settings[0])
            self.enable_display = int(self.config_settings[1])
            self.enable_interval_recording = int(self.config_settings[2])
            self.enable_trigger_recording = int(self.config_settings[3])
            self.sleep_duration_interval = float(self.config_settings[4])
            self.enable_custom_temp = int(self.config_settings[5])
            self.temperature_offset = float(self.config_settings[6])
        else:
            log_msg = "Invalid number of setting for "
            logger.primary_logger.warning(log_msg + str(self.config_file_location))
