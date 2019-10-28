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
from operations_modules import software_version, file_locations, app_generic_functions, logger


class CreateLuftdatenConfig:
    """ Creates a Luftdaten Configuration object. """

    def __init__(self):
        # Luftdaten URL
        self.luftdaten_url = "https://api.luftdaten.info/v1/push-sensor-data/"
        self.madavi_url = "https://api-rrd.madavi.de/data.php"

        sw_version_text_list = software_version.version.split(".")
        sw_version_text = str(sw_version_text_list[0]) + "." + str(sw_version_text_list[1])
        self.return_software_version = "Kootnet Sensors " + sw_version_text

        self.luftdaten_enabled = 0
        self.interval_seconds = 180
        self.station_id = self._get_cpu_serial()

        self.bad_load = False

    def get_configuration_str(self):
        """ Returns Luftdaten settings ready to be written to the configuration file. """
        config_str = "Enable = 1 & Disable = 0\n" + \
                     str(self.luftdaten_enabled) + " = Enable Luftdaten\n" + \
                     str(self.interval_seconds) + " = Send to Server in Seconds"
        return config_str

    def update_luftdaten_html(self, html_request):
        """ Updates & Writes Luftdaten settings based on provided HTML request. """
        if html_request.form.get("enable_luftdaten") is not None:
            self.luftdaten_enabled = 1
        else:
            self.luftdaten_enabled = 0
        if html_request.form.get("station_interval") is not None:
            self.interval_seconds = float(html_request.form.get("station_interval"))
        self.write_config_to_file()

    def update_settings_from_file(self, file_content=None, skip_write=False):
        """
        Updates Luftdaten settings based on saved configuration file.  Creates Default file if missing.
        """
        if os.path.isfile(file_locations.luftdaten_config) or skip_write:
            if file_content is None:
                loaded_configuration_raw = app_generic_functions.get_file_content(file_locations.luftdaten_config)
            else:
                loaded_configuration_raw = file_content
            configuration_lines = loaded_configuration_raw.split("\n")

            try:
                if int(configuration_lines[1][0]):
                    self.luftdaten_enabled = 1
                else:
                    self.luftdaten_enabled = 0
                try:
                    self.interval_seconds = float(configuration_lines[2].split("=")[0].strip())
                except Exception as error:
                    logger.primary_logger.warning("Luftdaten - Interval Error from file: " + str(error))
                    self.interval_seconds = 300
            except Exception as error:
                if not skip_write:
                    self.write_config_to_file()
                    log_msg = "Luftdaten - Problem loading Configuration file, using 1 or more Defaults: " + str(error)
                    logger.primary_logger.warning(log_msg)
                else:
                    self.bad_load = True
        else:
            if not skip_write:
                logger.primary_logger.info("Luftdaten - Configuration file not found: Saving Default")
                self.write_config_to_file()

    def write_config_to_file(self):
        """ Writes current Luftdaten settings to file. """
        config_str = self.get_configuration_str()
        app_generic_functions.write_file_to_disk(file_locations.luftdaten_config, config_str)

    # extracts serial from cpuinfo
    @staticmethod
    def _get_cpu_serial():
        try:
            with open('/proc/cpuinfo', 'r') as f:
                for line in f:
                    if line[0:6] == 'Serial':
                        return line.split(":")[1].strip()
        except Exception as error:
            logger.primary_logger.error("Luftdaten - Unable to get CPU Serial: " + str(error))
            return "35505FFFF"
