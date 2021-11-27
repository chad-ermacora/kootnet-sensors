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


class CreateSensorOffsetsConfiguration(CreateGeneralConfiguration):
    """ Creates the Sensor Offsets Configuration object and loads settings from file (by default). """

    def __init__(self, load_from_file=True):
        CreateGeneralConfiguration.__init__(self, file_locations.sensor_offsets_config, load_from_file=load_from_file)
        self.config_file_header = "Enable = 1 and Disable = 0"
        self.valid_setting_count = 4
        self.config_settings_names = [
            "Enable Temperature Offset", "Temperature Offset", "Enable Temperature Correction Factor",
            "Temperature Correction Factor"
        ]

        self.enable_temp_offset = 0
        self.temperature_offset = 0.0
        self.enable_temperature_comp_factor = 0
        self.temperature_comp_factor = 0.0

        self.update_configuration_settings_list()
        if load_from_file:
            self._init_config_variables()
            self._update_variables_from_settings_list()

    def set_config_with_str(self, config_file_text):
        super().set_config_with_str(config_file_text)
        self._update_variables_from_settings_list()

    def update_with_html_request(self, html_request):
        """ Updates the Sensor Offsets configuration based on provided HTML configuration data. """
        logger.network_logger.debug("Starting HTML Sensor Offsets Configuration Update Check")

        self.enable_temp_offset = 0
        self.enable_temperature_comp_factor = 0

        if html_request.form.get("enable_custom_temp_offset") is not None:
            self.enable_temp_offset = 1
        if html_request.form.get("custom_temperature_offset") is not None:
            new_temp = float(html_request.form.get("custom_temperature_offset"))
            self.temperature_offset = new_temp

        if html_request.form.get("enable_custom_temp_comp") is not None:
            self.enable_temperature_comp_factor = 1
        if html_request.form.get("custom_temperature_comp") is not None:
            new_temp_comp = float(html_request.form.get("custom_temperature_comp"))
            self.temperature_comp_factor = new_temp_comp
        self.update_configuration_settings_list()

    def update_configuration_settings_list(self):
        """ Set's config_settings variable list based on current settings. """

        self.config_settings = [
            str(self.enable_temp_offset), str(self.temperature_offset), str(self.enable_temperature_comp_factor),
            str(self.temperature_comp_factor)
        ]

    def _update_variables_from_settings_list(self):
        try:
            self.enable_temp_offset = int(self.config_settings[0].strip())
            self.temperature_offset = float(self.config_settings[1].strip())
            self.enable_temperature_comp_factor = int(self.config_settings[2].strip())
            self.temperature_comp_factor = float(self.config_settings[3].strip())

        except Exception as error:
            if self.load_from_file:
                logger.primary_logger.debug("Sensor Offsets Config: " + str(error))
            self.update_configuration_settings_list()
            if self.load_from_file:
                logger.primary_logger.info("Saving Sensor Offsets Configuration.")
                self.save_config_to_file()
