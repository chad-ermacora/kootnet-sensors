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
from operations_modules import logger, file_locations, app_generic_functions


class CreateOpenSenseMapConfig:
    """ Creates a Open Sense Map Configuration object. """

    def __init__(self):
        # Weather Underground URL Variables
        self.open_sense_map_main_url_start = "https://api.opensensemap.org/boxes"
        self.open_sense_map_login_url = "https://api.opensensemap.org/users/sign-in"

        self.open_sense_map_enabled = 0
        self.sense_box_id = ""
        self.interval_seconds = 900.0

        self.temperature_id = ""
        self.pressure_id = ""
        self.altitude_id = ""
        self.humidity_id = ""
        self.gas_voc_id = ""
        self.gas_oxidised_id = ""
        self.gas_reduced_id = ""
        self.gas_nh3_id = ""
        self.pm1_id = ""
        self.pm2_5_id = ""
        self.pm10_id = ""

        self.lumen_id = ""
        self.red_id = ""
        self.orange_id = ""
        self.yellow_id = ""
        self.green_id = ""
        self.blue_id = ""
        self.violet_id = ""

        self.ultra_violet_index_id = ""
        self.ultra_violet_a_id = ""
        self.ultra_violet_b_id = ""

        self.bad_load = False

    def get_configuration_str(self):
        """ Returns Open Sense Map settings ready to be written to the configuration file. """
        config_str = "Enable = 1 & Disable = 0\n" + \
                     str(self.open_sense_map_enabled) + " = Enable Open Sense Map\n" + \
                     str(self.sense_box_id) + " = SenseBox ID\n" + \
                     str(self.interval_seconds) + " = Send to Server in Seconds\n" + \
                     str(self.temperature_id) + " = Temperature Sensor ID\n" + \
                     str(self.pressure_id) + " = Pressure Sensor ID\n" + \
                     str(self.altitude_id) + " = Altitude Sensor ID\n" + \
                     str(self.humidity_id) + " = Humidity Sensor ID\n" + \
                     str(self.gas_voc_id) + " = Gas VOC Sensor ID\n" + \
                     str(self.gas_nh3_id) + " = Gas NH3 Sensor ID\n" + \
                     str(self.gas_oxidised_id) + " = Gas Oxidised Sensor ID\n" + \
                     str(self.gas_reduced_id) + " = Gas Reduced Sensor ID\n" + \
                     str(self.pm1_id) + " = PM 1.0 Sensor ID\n" + \
                     str(self.pm2_5_id) + " = PM 2.5 Sensor ID\n" + \
                     str(self.pm10_id) + " = PM 10 Sensor ID\n" + \
                     str(self.lumen_id) + " = Lumen Sensor ID\n" + \
                     str(self.red_id) + " = Red Sensor ID\n" + \
                     str(self.orange_id) + " = Orange Sensor ID\n" + \
                     str(self.yellow_id) + " = Yellow Sensor ID\n" + \
                     str(self.green_id) + " = Green Sensor ID\n" + \
                     str(self.blue_id) + " = Blue Sensor ID\n" + \
                     str(self.violet_id) + " = Violet Sensor ID\n" + \
                     str(self.ultra_violet_index_id) + " = Ultra Violet Index Sensor ID\n" + \
                     str(self.ultra_violet_a_id) + " = Ultra Violet A Sensor ID\n" + \
                     str(self.ultra_violet_b_id) + " = Ultra Violet B Sensor ID"

        return config_str

    def update_open_sense_map_html(self, html_request):
        """ Updates & Writes Open Sense Map settings based on provided HTML request. """
        if html_request.form.get("enable_open_sense_map") is not None:
            self.open_sense_map_enabled = 1
        else:
            self.open_sense_map_enabled = 0

        if html_request.form.get("osm_station_id") is not None:
            self.sense_box_id = html_request.form.get("osm_station_id").strip()
        else:
            self.sense_box_id = ""

        if html_request.form.get("osm_interval") is not None:
            try:
                self.interval_seconds = float(html_request.form.get("osm_interval").strip())
            except Exception as error:
                logger.primary_logger.warning("Open Sense Map - Invalid Interval: " + str(error))
                self.interval_seconds = 900.0
        else:
            self.interval_seconds = 900.0

        if html_request.form.get("env_temp_id") is not None:
            self.temperature_id = html_request.form.get("env_temp_id").strip()
        else:
            self.temperature_id = ""
        if html_request.form.get("pressure_id") is not None:
            self.pressure_id = html_request.form.get("pressure_id").strip()
        else:
            self.pressure_id = ""
        if html_request.form.get("altitude_id") is not None:
            self.altitude_id = html_request.form.get("altitude_id").strip()
        else:
            self.altitude_id = ""
        if html_request.form.get("humidity_id") is not None:
            self.humidity_id = html_request.form.get("humidity_id").strip()
        else:
            self.humidity_id = ""
        if html_request.form.get("gas_index_id") is not None:
            self.gas_voc_id = html_request.form.get("gas_index_id").strip()
        else:
            self.gas_voc_id = ""
        if html_request.form.get("gas_nh3_id") is not None:
            self.gas_nh3_id = html_request.form.get("gas_nh3_id").strip()
        else:
            self.gas_nh3_id = ""
        if html_request.form.get("gas_oxidising_id") is not None:
            self.gas_oxidised_id = html_request.form.get("gas_oxidising_id").strip()
        else:
            self.gas_oxidised_id = ""
        if html_request.form.get("gas_reducing_id") is not None:
            self.gas_reduced_id = html_request.form.get("gas_reducing_id").strip()
        else:
            self.gas_reduced_id = ""
        if html_request.form.get("pm1_id") is not None:
            self.pm1_id = html_request.form.get("pm1_id").strip()
        else:
            self.pm1_id = ""
        if html_request.form.get("pm2_5_id") is not None:
            self.pm2_5_id = html_request.form.get("pm2_5_id").strip()
        else:
            self.pm2_5_id = ""
        if html_request.form.get("pm10_id") is not None:
            self.pm10_id = html_request.form.get("pm10_id").strip()
        else:
            self.pm10_id = ""
        if html_request.form.get("lumen_id") is not None:
            self.lumen_id = html_request.form.get("lumen_id").strip()
        else:
            self.lumen_id = ""
        if html_request.form.get("red_id") is not None:
            self.red_id = html_request.form.get("red_id").strip()
        else:
            self.red_id = ""
        if html_request.form.get("orange_id") is not None:
            self.orange_id = html_request.form.get("orange_id").strip()
        else:
            self.orange_id = ""
        if html_request.form.get("yellow_id") is not None:
            self.yellow_id = html_request.form.get("yellow_id").strip()
        else:
            self.yellow_id = ""
        if html_request.form.get("green_id") is not None:
            self.green_id = html_request.form.get("green_id").strip()
        else:
            self.green_id = ""
        if html_request.form.get("blue_id") is not None:
            self.blue_id = html_request.form.get("blue_id").strip()
        else:
            self.blue_id = ""
        if html_request.form.get("violet_id") is not None:
            self.violet_id = html_request.form.get("violet_id").strip()
        else:
            self.violet_id = ""
        if html_request.form.get("uv_index_id") is not None:
            self.ultra_violet_index_id = html_request.form.get("uv_index_id").strip()
        else:
            self.ultra_violet_index_id = ""
        if html_request.form.get("uv_a_id") is not None:
            self.ultra_violet_a_id = html_request.form.get("uv_a_id").strip()
        else:
            self.ultra_violet_a_id = ""
        if html_request.form.get("uv_b_id") is not None:
            self.ultra_violet_b_id = html_request.form.get("uv_b_id").strip()
        else:
            self.ultra_violet_b_id = ""
        self.write_config_to_file()

    def update_settings_from_file(self, file_content=None, skip_write=False):
        """ Updates Open Sense Map settings based on saved configuration file.  Creates Default file if missing. """
        if os.path.isfile(file_locations.osm_config) or skip_write:
            if file_content is None:
                loaded_configuration_raw = app_generic_functions.get_file_content(file_locations.osm_config)
            else:
                loaded_configuration_raw = file_content
            configuration_lines = loaded_configuration_raw.split("\n")
            try:
                if int(configuration_lines[1][0]):
                    self.open_sense_map_enabled = 1
                else:
                    self.open_sense_map_enabled = 0

                self.sense_box_id = configuration_lines[2].split("=")[0].strip()

                try:
                    self.interval_seconds = float(configuration_lines[3].split("=")[0].strip())
                except Exception as error:
                    logger.primary_logger.warning("Open Sense Map - Interval Error from file: " + str(error))
                    self.interval_seconds = 900.0

                self.temperature_id = configuration_lines[4].split("=")[0].strip()
                self.pressure_id = configuration_lines[5].split("=")[0].strip()
                self.altitude_id = configuration_lines[6].split("=")[0].strip()
                self.humidity_id = configuration_lines[7].split("=")[0].strip()
                self.gas_voc_id = configuration_lines[8].split("=")[0].strip()
                self.gas_nh3_id = configuration_lines[9].split("=")[0].strip()
                self.gas_oxidised_id = configuration_lines[10].split("=")[0].strip()
                self.gas_reduced_id = configuration_lines[11].split("=")[0].strip()
                self.pm1_id = configuration_lines[12].split("=")[0].strip()
                self.pm2_5_id = configuration_lines[13].split("=")[0].strip()
                self.pm10_id = configuration_lines[14].split("=")[0].strip()
                self.lumen_id = configuration_lines[15].split("=")[0].strip()
                self.red_id = configuration_lines[16].split("=")[0].strip()
                self.orange_id = configuration_lines[17].split("=")[0].strip()
                self.yellow_id = configuration_lines[18].split("=")[0].strip()
                self.green_id = configuration_lines[19].split("=")[0].strip()
                self.blue_id = configuration_lines[20].split("=")[0].strip()
                self.violet_id = configuration_lines[21].split("=")[0].strip()
                self.ultra_violet_index_id = configuration_lines[22].split("=")[0].strip()
                self.ultra_violet_a_id = configuration_lines[23].split("=")[0].strip()
                self.ultra_violet_b_id = configuration_lines[24].split("=")[0].strip()
            except Exception as error:
                if not skip_write:
                    log_msg = "Open Sense Map - Problem loading Configuration file, using 1 or more Defaults: "
                    logger.primary_logger.warning(log_msg + str(error))
                    self.write_config_to_file()
                else:
                    self.bad_load = True
        else:
            if not skip_write:
                logger.primary_logger.info("Open Sense Map - Configuration file not found: Saving Default")
                self.write_config_to_file()

    def write_config_to_file(self):
        """ Writes current Open Sense Map settings to file. """
        config_str = self.get_configuration_str()
        app_generic_functions.write_file_to_disk(file_locations.osm_config, config_str)
