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


class CreateOpenSenseMapConfiguration(CreateGeneralConfiguration):
    """ Creates the Open Sense Map Configuration object and loads settings from file (by default). """

    def __init__(self, load_from_file=True):
        CreateGeneralConfiguration.__init__(self, file_locations.osm_config, load_from_file=load_from_file)
        self.config_file_header = "Enable = 1 & Disable = 0"
        self.valid_setting_count = 25
        self.config_settings_names = ["Enable Open Sense Map", "SenseBox ID", "Send to Server in Seconds",
                                      "Temperature Sensor ID", "Pressure Sensor ID", "Altitude Sensor ID",
                                      "Humidity Sensor ID", "Gas VOC Sensor ID", "Gas NH3 Sensor ID",
                                      "Gas Oxidised Sensor ID", "Gas Reduced Sensor ID", "PM 1.0 Sensor ID",
                                      "PM 2.5 Sensor ID", "PM 4 Sensor ID", "PM 10 Sensor ID", "Lumen Sensor ID",
                                      "Red Sensor ID", "Orange Sensor ID", "Yellow Sensor ID", "Green Sensor ID",
                                      "Blue Sensor ID", "Violet Sensor ID", "Ultra Violet Index Sensor ID",
                                      "Ultra Violet A Sensor ID", "Ultra Violet B Sensor ID"]

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
        self.pm4_id = ""
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

        self.update_configuration_settings_list()
        if load_from_file:
            self._init_config_variables()
            self._update_variables_from_settings_list()

    def set_config_with_str(self, config_file_text):
        super().set_config_with_str(config_file_text)
        self._update_variables_from_settings_list()

    def update_with_html_request(self, html_request):
        """ Updates the Open Sense Map configuration based on provided HTML configuration data. """
        logger.network_logger.debug("Starting Open Sense Map Configuration Update Check")
        self.open_sense_map_enabled = 0
        if html_request.form.get("enable_open_sense_map") is not None:
            self.open_sense_map_enabled = 1
        if html_request.form.get("osm_station_id") is not None:
            self.sense_box_id = html_request.form.get("osm_station_id").strip()
        if html_request.form.get("osm_interval") is not None:
            try:
                self.interval_seconds = float(html_request.form.get("osm_interval").strip())
            except Exception as error:
                logger.primary_logger.warning("Open Sense Map - Invalid Interval: " + str(error))
                self.interval_seconds = 900.0
        if html_request.form.get("env_temp_id") is not None:
            self.temperature_id = html_request.form.get("env_temp_id").strip()
        if html_request.form.get("pressure_id") is not None:
            self.pressure_id = html_request.form.get("pressure_id").strip()
        if html_request.form.get("altitude_id") is not None:
            self.altitude_id = html_request.form.get("altitude_id").strip()
        if html_request.form.get("humidity_id") is not None:
            self.humidity_id = html_request.form.get("humidity_id").strip()
        if html_request.form.get("gas_index_id") is not None:
            self.gas_voc_id = html_request.form.get("gas_index_id").strip()
        if html_request.form.get("gas_nh3_id") is not None:
            self.gas_nh3_id = html_request.form.get("gas_nh3_id").strip()
        if html_request.form.get("gas_oxidising_id") is not None:
            self.gas_oxidised_id = html_request.form.get("gas_oxidising_id").strip()
        if html_request.form.get("gas_reducing_id") is not None:
            self.gas_reduced_id = html_request.form.get("gas_reducing_id").strip()
        if html_request.form.get("pm1_id") is not None:
            self.pm1_id = html_request.form.get("pm1_id").strip()
        if html_request.form.get("pm2_5_id") is not None:
            self.pm2_5_id = html_request.form.get("pm2_5_id").strip()
        if html_request.form.get("pm4_id") is not None:
            self.pm4_id = html_request.form.get("pm4_id").strip()
        if html_request.form.get("pm10_id") is not None:
            self.pm10_id = html_request.form.get("pm10_id").strip()
        if html_request.form.get("lumen_id") is not None:
            self.lumen_id = html_request.form.get("lumen_id").strip()
        if html_request.form.get("red_id") is not None:
            self.red_id = html_request.form.get("red_id").strip()
        if html_request.form.get("orange_id") is not None:
            self.orange_id = html_request.form.get("orange_id").strip()
        if html_request.form.get("yellow_id") is not None:
            self.yellow_id = html_request.form.get("yellow_id").strip()
        if html_request.form.get("green_id") is not None:
            self.green_id = html_request.form.get("green_id").strip()
        if html_request.form.get("blue_id") is not None:
            self.blue_id = html_request.form.get("blue_id").strip()
        if html_request.form.get("violet_id") is not None:
            self.violet_id = html_request.form.get("violet_id").strip()
        if html_request.form.get("uv_index_id") is not None:
            self.ultra_violet_index_id = html_request.form.get("uv_index_id").strip()
        if html_request.form.get("uv_a_id") is not None:
            self.ultra_violet_a_id = html_request.form.get("uv_a_id").strip()
        if html_request.form.get("uv_b_id") is not None:
            self.ultra_violet_b_id = html_request.form.get("uv_b_id").strip()
        self.update_configuration_settings_list()
        self.load_from_file = True

    def update_configuration_settings_list(self):
        """ Set's config_settings variable list based on current settings. """
        self.config_settings = [str(self.open_sense_map_enabled), str(self.sense_box_id), str(self.interval_seconds),
                                str(self.temperature_id), str(self.pressure_id), str(self.altitude_id),
                                str(self.humidity_id), str(self.gas_voc_id), str(self.gas_nh3_id),
                                str(self.gas_oxidised_id), str(self.gas_reduced_id), str(self.pm1_id),
                                str(self.pm2_5_id), str(self.pm4_id), str(self.pm10_id), str(self.lumen_id),
                                str(self.red_id), str(self.orange_id), str(self.yellow_id), str(self.green_id),
                                str(self.blue_id), str(self.violet_id), str(self.ultra_violet_index_id),
                                str(self.ultra_violet_a_id), str(self.ultra_violet_b_id)]

    def _update_variables_from_settings_list(self):
        try:
            self.open_sense_map_enabled = int(self.config_settings[0])
            self.sense_box_id = str(self.config_settings[1])
            self.interval_seconds = float(self.config_settings[2])
            self.temperature_id = str(self.config_settings[3])
            self.pressure_id = str(self.config_settings[4])
            self.altitude_id = str(self.config_settings[5])
            self.humidity_id = str(self.config_settings[6])
            self.gas_voc_id = str(self.config_settings[7])
            self.gas_nh3_id = str(self.config_settings[8])
            self.gas_oxidised_id = str(self.config_settings[9])
            self.gas_reduced_id = str(self.config_settings[10])
            self.pm1_id = str(self.config_settings[11])
            self.pm2_5_id = str(self.config_settings[12])
            self.pm4_id = str(self.config_settings[13])
            self.pm10_id = str(self.config_settings[14])
            self.lumen_id = str(self.config_settings[15])
            self.red_id = str(self.config_settings[16])
            self.orange_id = str(self.config_settings[17])
            self.yellow_id = str(self.config_settings[18])
            self.green_id = str(self.config_settings[19])
            self.blue_id = str(self.config_settings[20])
            self.violet_id = str(self.config_settings[21])
            self.ultra_violet_index_id = str(self.config_settings[22])
            self.ultra_violet_a_id = str(self.config_settings[23])
            self.ultra_violet_b_id = str(self.config_settings[24])
        except Exception as error:
            logger.primary_logger.debug("Open Sense Map Config: " + str(error))
            self.update_configuration_settings_list()
            if self.load_from_file:
                logger.primary_logger.info("Saving Open Sense Map Configuration.")
                self.save_config_to_file()
