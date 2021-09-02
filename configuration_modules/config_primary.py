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
        self.config_file_header = "Enable = 1 and Disable = 0"
        self.valid_setting_count = 11
        self.config_settings_names = [
            "HTTPS port number (Default is 10065)", "Enable debug logging", "Enable temperature offset",
            "Temperature offset", "Enable temperature compensation factor", "Temperature compensation factor",
            "DateTime offset in hours (Program uses UTC 0)", "Enable Automatic Major version upgrades",
            "Enable Automatic Minor version upgrades", "Enable Automatic Developmental version upgrades",
            "Delay in Hours between Automatic Upgrade Checks"
        ]

        self.sensor_id = app_cached_variables.tmp_sensor_id

        self.enable_debug_logging = 0
        self.utc0_hour_offset = 0.0

        self.enable_custom_temp = 0
        self.temperature_offset = 0.0
        self.enable_temperature_comp_factor = 0
        self.temperature_comp_factor = 0.0

        self.flask_http_ip = ""
        self.web_portal_port = 10065

        self.enable_automatic_upgrades_major = 0
        self.enable_automatic_upgrades_minor = 0
        self.enable_automatic_upgrades_developmental = 0
        self.automatic_upgrade_delay_hours = 6

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
        self.enable_automatic_upgrades_major = 0
        self.enable_automatic_upgrades_minor = 0
        self.enable_automatic_upgrades_developmental = 0
        self.enable_custom_temp = 0
        self.enable_temperature_comp_factor = 0

        if html_request.form.get("debug_logging") is not None:
            self.enable_debug_logging = 1
            logger.set_logging_level(debug_enabled=True)
        else:
            logger.set_logging_level(debug_enabled=False)

        if html_request.form.get("program_hour_offset") is not None:
            self.utc0_hour_offset = float(html_request.form.get("program_hour_offset"))

        if html_request.form.get("auto_upgrade_delay_hours") is not None:
            try:
                new_hours = float(html_request.form.get("auto_upgrade_delay_hours"))
                if new_hours < 0.25:
                    new_hours = 0.25
            except Exception as error:
                logger.network_logger.warning("Automatic Software Upgrades - New Delay Setting Error: " + str(error))
                new_hours = 6
            self.automatic_upgrade_delay_hours = new_hours

        if html_request.form.get("enable_stable_major_auto_upgrades") is not None:
            self.enable_automatic_upgrades_major = 1
        if html_request.form.get("enable_stable_minor_auto_upgrades") is not None:
            self.enable_automatic_upgrades_minor = 1
        if html_request.form.get("enable_dev_auto_upgrades") is not None:
            self.enable_automatic_upgrades_developmental = 1

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
        self.update_configuration_settings_list()

    def update_configuration_settings_list(self):
        """ Set's config_settings variable list based on current settings. """

        self.config_settings = [
            str(self.web_portal_port), str(self.enable_debug_logging), str(self.enable_custom_temp),
            str(self.temperature_offset), str(self.enable_temperature_comp_factor), str(self.temperature_comp_factor),
            str(self.utc0_hour_offset), str(self.enable_automatic_upgrades_major),
            str(self.enable_automatic_upgrades_minor), str(self.enable_automatic_upgrades_developmental),
            str(self.automatic_upgrade_delay_hours)
        ]

    def _update_variables_from_settings_list(self):
        try:
            self.web_portal_port = int(self.config_settings[0])
            self.enable_debug_logging = int(self.config_settings[1])
            self.enable_custom_temp = int(self.config_settings[2])
            self.temperature_offset = float(self.config_settings[3])
            self.enable_temperature_comp_factor = int(self.config_settings[4])
            self.temperature_comp_factor = float(self.config_settings[5])
            self.utc0_hour_offset = float(self.config_settings[6].strip())
            self.enable_automatic_upgrades_major = int(self.config_settings[7])
            self.enable_automatic_upgrades_minor = int(self.config_settings[8])
            self.enable_automatic_upgrades_developmental = int(self.config_settings[9])
            self.automatic_upgrade_delay_hours = float(self.config_settings[10])
        except Exception as error:
            if self.load_from_file:
                logger.primary_logger.debug("Primary Config: " + str(error))
            self.update_configuration_settings_list()
            if self.load_from_file:
                logger.primary_logger.info("Saving Primary Configuration.")
                self.save_config_to_file()
