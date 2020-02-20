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
from operations_modules import software_version
from operations_modules.app_generic_functions import CreateGeneralConfiguration


class CreateLuftdatenConfiguration(CreateGeneralConfiguration):
    """ Creates the Luftdaten Configuration object and loads settings from file (by default). """

    def __init__(self, load_from_file=True):
        CreateGeneralConfiguration.__init__(self, file_locations.luftdaten_config)
        self.config_file_header = "Enable = 1 & Disable = 0"
        self.valid_setting_count = 2
        self.config_settings_names = ["Enable Luftdaten", "Send to Server in Seconds"]

        self.luftdaten_url = "https://api.luftdaten.info/v1/push-sensor-data/"
        self.madavi_url = "https://api-rrd.madavi.de/data.php"

        self.return_software_version = "Kootnet Sensors "

        self.luftdaten_enabled = 0
        self.interval_seconds = 180
        self.station_id = self._get_cpu_serial()

        self._update_configuration_settings_list()
        if load_from_file:
            sw_version_text_list = software_version.version.split(".")
            sw_version_text = str(sw_version_text_list[0]) + "." + str(sw_version_text_list[1])
            self.return_software_version += sw_version_text
            self._init_config_variables()
            self._update_variables_from_settings_list()

    def set_config_with_str(self, config_file_text):
        super().set_config_with_str(config_file_text)
        self._update_variables_from_settings_list()

    def update_with_html_request(self, html_request):
        """ Updates the Luftdaten configuration based on provided HTML configuration data. """
        logger.network_logger.debug("Starting Luftdaten Configuration Update Check")
        self.luftdaten_enabled = 0
        if html_request.form.get("enable_luftdaten") is not None:
            self.luftdaten_enabled = 1

        if html_request.form.get("station_interval") is not None:
            self.interval_seconds = float(html_request.form.get("station_interval"))
            if self.interval_seconds < 10.0:
                self.interval_seconds = 10.0
        self._update_configuration_settings_list()

    def set_settings_for_test1(self):
        self.luftdaten_enabled = 0
        self.interval_seconds = 9663.09
        self._update_configuration_settings_list()

    def set_settings_for_test2(self):
        self.luftdaten_enabled = 1
        self.interval_seconds = 55712.21
        self._update_configuration_settings_list()

    def _update_configuration_settings_list(self):
        """ Set's config_settings variable list based on current settings. """
        self.config_settings = [str(self.luftdaten_enabled), str(self.interval_seconds)]

    def _update_variables_from_settings_list(self):
        if self.valid_setting_count == len(self.config_settings):
            try:
                self.luftdaten_enabled = int(self.config_settings[0])
                self.interval_seconds = float(self.config_settings[1])
            except Exception as error:
                log_msg = "Invalid Settings detected for " + self.config_file_location + ": "
                logger.primary_logger.warning(log_msg + str(error))
        else:
            log_msg = "Invalid number of setting for "
            logger.primary_logger.warning(log_msg + str(self.config_file_location))

    @staticmethod
    def _get_cpu_serial():
        """ Returns Raspberry Pi CPU Serial number. """
        try:
            with open('/proc/cpuinfo', 'r') as f:
                for line in f:
                    if line[0:6] == 'Serial':
                        return line.split(":")[1].strip()
        except Exception as error:
            logger.primary_logger.error("Luftdaten - Unable to get CPU Serial: " + str(error))
            return "35505FFFF"
