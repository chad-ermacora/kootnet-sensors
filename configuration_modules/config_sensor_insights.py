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


class CreateSensorInsightsConfiguration(CreateGeneralConfiguration):
    """ Creates the Sensor Insights Configuration object and loads settings from file (by default). """

    def __init__(self, load_from_file=True, config_file_location=None):
        if config_file_location is None:
            config_file_location = file_locations.sensor_insights_config
        CreateGeneralConfiguration.__init__(self, config_file_location, load_from_file=load_from_file)
        self.config_file_header = "Sensor Insights Configuration. Enable = 1 and Disable = 0"
        self.valid_setting_count = 4
        self.config_settings_names = [
            "Use All Recorded Data", "Manual Start Date Range", "Manual End Date Range",
            "Number of Insights to display per sensor"
        ]

        self.use_all_recorded_data = 1
        self.start_date_range = "2012-01-01T00:00"
        self.end_date_range = "2222-01-01T00:00:00"
        self.insights_per_sensor = 10

        self.update_configuration_settings_list()
        if load_from_file:
            self._init_config_variables()
            self.update_variables_from_settings_list()

    def set_config_with_str(self, config_file_text):
        super().set_config_with_str(config_file_text)
        self.update_variables_from_settings_list()

    def update_with_html_request(self, html_request):
        """ Updates the Sensor Insights configuration based on provided HTML configuration data. """
        logger.network_logger.debug("Starting HTML Sensor Insights Configuration Update Check")
        self.use_all_recorded_data = 0

        if html_request.form.get("number_of_insights") is not None:
            self.insights_per_sensor = int(html_request.form.get("number_of_insights"))

        if html_request.form.get("use_all_recorded_data") is not None:
            self.use_all_recorded_data = 1
        else:
            # The datetime format should look like "2019-01-01T00:00"
            if html_request.form.get("insights_datetime_start") is not None:
                self.start_date_range = str(html_request.form.get("insights_datetime_start"))
            if html_request.form.get("insights_datetime_end") is not None:
                self.end_date_range = str(html_request.form.get("insights_datetime_end"))
        self.update_configuration_settings_list()

    def update_configuration_settings_list(self):
        """ Set's config_settings variable list based on current settings. """
        self.config_settings = [
            str(self.use_all_recorded_data), str(self.start_date_range), str(self.end_date_range),
            str(self.insights_per_sensor)
        ]

    def update_variables_from_settings_list(self):
        try:
            self.use_all_recorded_data = int(self.config_settings[0].strip())
            self.start_date_range = self.config_settings[1].strip()
            self.end_date_range = self.config_settings[2].strip()
            self.insights_per_sensor = int(self.config_settings[3].strip())
        except Exception as error:
            if self.load_from_file:
                logger.primary_logger.debug("Sensor Insights Config: " + str(error))
            self.update_configuration_settings_list()
            if self.load_from_file:
                logger.primary_logger.info("Saving Sensor Insights Configuration.")
                self.save_config_to_file()
