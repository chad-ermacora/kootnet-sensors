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
from os import geteuid
from subprocess import check_output
from operations_modules import logger
from operations_modules import file_locations
from operations_modules.app_generic_functions import CreateGeneralConfiguration


class CreateInstalledSensorsConfiguration(CreateGeneralConfiguration):
    """ Creates the Primary Configuration object and loads settings from file (by default). """

    def __init__(self, load_from_file=True):
        installed_sensors_config = file_locations.installed_sensors_config
        CreateGeneralConfiguration.__init__(self, installed_sensors_config, load_from_file=load_from_file)
        self.config_file_header = "Enable = 1 & Disable = 0"
        self.valid_setting_count = 22
        self.config_settings_names = ["Gnu/Linux", "Raspberry Pi", "Raspberry Pi Sense HAT", "Pimoroni BH1745",
                                      "Pimoroni AS7262", "Pimoroni MCP9600", "Pimoroni BMP280", "Pimoroni BME680",
                                      "Pimoroni EnviroPHAT", "Pimoroni Enviro+", "Pimoroni SGP30", "Pimoroni PMS5003",
                                      "Pimoroni MSA301", "Pimoroni LSM303D", "Pimoroni ICM20948", "Pimoroni VL53L1X",
                                      "Pimoroni LTR-559", "Pimoroni VEML6075", "Pimoroni 11x7 LED Matrix",
                                      "Pimoroni 10.96'' SPI Colour LCD (160x80)",
                                      "Pimoroni 1.12'' Mono OLED (128x128, white/black)", "Kootnet Dummy Sensors"]

        self.no_sensors = True

        self.kootnet_dummy_sensor = 0

        self.linux_system = 1
        self.raspberry_pi = 0

        self.raspberry_pi_sense_hat = 0
        self.pimoroni_bh1745 = 0
        self.pimoroni_as7262 = 0
        self.pimoroni_mcp9600 = 0
        self.pimoroni_bmp280 = 0
        self.pimoroni_bme680 = 0
        self.pimoroni_enviro = 0
        self.pimoroni_enviroplus = 0
        self.pimoroni_sgp30 = 0
        self.pimoroni_pms5003 = 0
        self.pimoroni_msa301 = 0
        self.pimoroni_lsm303d = 0
        self.pimoroni_icm20948 = 0
        self.pimoroni_vl53l1x = 0
        self.pimoroni_ltr_559 = 0
        self.pimoroni_veml6075 = 0

        self.pimoroni_matrix_11x7 = 0
        self.pimoroni_st7735 = 0
        self.pimoroni_mono_oled_luma = 0

        self.update_configuration_settings_list()
        if load_from_file:
            self._init_config_variables()
            self._update_variables_from_settings_list()

    def set_config_with_str(self, config_file_text):
        super().set_config_with_str(config_file_text)
        self._update_variables_from_settings_list()

    def update_with_html_request(self, html_request):
        """ Updates the Installed Sensors configuration based on provided HTML configuration data. """
        logger.network_logger.debug("Starting HTML Installed Sensors Update Check")
        self.__init__(load_from_file=False)
        try:
            if html_request.form.get("linux_system") is not None:
                self.linux_system = 1
            if html_request.form.get("raspberry_pi") is not None:
                self.raspberry_pi = 1
            if html_request.form.get("raspberry_pi_sense_hat") is not None:
                self.raspberry_pi_sense_hat = 1
            if html_request.form.get("pimoroni_bh1745") is not None:
                self.pimoroni_bh1745 = 1
            if html_request.form.get("pimoroni_as7262") is not None:
                self.pimoroni_as7262 = 1
            if html_request.form.get("pimoroni_mcp9600") is not None:
                self.pimoroni_mcp9600 = 1
            if html_request.form.get("pimoroni_bmp280") is not None:
                self.pimoroni_bmp280 = 1
            if html_request.form.get("pimoroni_bme680") is not None:
                self.pimoroni_bme680 = 1
            if html_request.form.get("pimoroni_enviro") is not None:
                self.pimoroni_enviro = 1
            if html_request.form.get("pimoroni_enviroplus") is not None:
                self.pimoroni_enviroplus = 1
            if html_request.form.get("pimoroni_sgp30") is not None:
                self.pimoroni_sgp30 = 1
            if html_request.form.get("pimoroni_pms5003") is not None:
                self.pimoroni_pms5003 = 1
            if html_request.form.get("pimoroni_msa301") is not None:
                self.pimoroni_msa301 = 1
            if html_request.form.get("pimoroni_lsm303d") is not None:
                self.pimoroni_lsm303d = 1
            if html_request.form.get("pimoroni_icm20948") is not None:
                self.pimoroni_icm20948 = 1
            if html_request.form.get("pimoroni_vl53l1x") is not None:
                self.pimoroni_vl53l1x = 1
            if html_request.form.get("pimoroni_ltr_559") is not None:
                self.pimoroni_ltr_559 = 1
            if html_request.form.get("pimoroni_veml6075") is not None:
                self.pimoroni_veml6075 = 1
            if html_request.form.get("pimoroni_matrix_11x7") is not None:
                self.pimoroni_matrix_11x7 = 1
            if html_request.form.get("pimoroni_st7735") is not None:
                self.pimoroni_st7735 = 1
            if html_request.form.get("pimoroni_mono_oled_luma") is not None:
                self.pimoroni_mono_oled_luma = 1
            if html_request.form.get("kootnet_dummy_sensor") is not None:
                self.kootnet_dummy_sensor = 1
        except Exception as error:
            logger.network_logger.warning("Installed Sensors Configuration Error: " + str(error))
        self.update_configuration_settings_list()
        self.load_from_file = True

    def get_installed_names_str(self):
        """ Returns Installed Sensors as a String. """
        logger.primary_logger.debug("Returning Installed Sensors as a string for " + str(self.config_file_location))
        new_file_content = ""
        for setting, setting_name in zip(self.config_settings, self.config_settings_names):
            if int(setting):
                if self.config_settings_names[1] == setting_name:
                    new_file_content += self.get_raspberry_pi_model() + " || "
                else:
                    new_file_content += str(setting_name) + " || "
        if len(new_file_content) > 4:
            if geteuid():
                return new_file_content[:-4] + " || Hardware Sensors Disabled - Not running with root"
            return new_file_content[:-4]
        return "N/A"

    def _update_variables_from_settings_list(self):
        bad_load = 0
        try:
            self.linux_system = int(self.config_settings[0])
            self.raspberry_pi = int(self.config_settings[1])
            self.raspberry_pi_sense_hat = int(self.config_settings[2])
            self.pimoroni_bh1745 = int(self.config_settings[3])
            self.pimoroni_as7262 = int(self.config_settings[4])
            self.pimoroni_mcp9600 = int(self.config_settings[5])
            self.pimoroni_bmp280 = int(self.config_settings[6])
            self.pimoroni_bme680 = int(self.config_settings[7])
            self.pimoroni_enviro = int(self.config_settings[8])
            self.pimoroni_enviroplus = int(self.config_settings[9])
            self.pimoroni_sgp30 = int(self.config_settings[10])
            self.pimoroni_pms5003 = int(self.config_settings[11])
            self.pimoroni_msa301 = int(self.config_settings[12])
            self.pimoroni_lsm303d = int(self.config_settings[13])
            self.pimoroni_icm20948 = int(self.config_settings[14])
            self.pimoroni_vl53l1x = int(self.config_settings[15])
            self.pimoroni_ltr_559 = int(self.config_settings[16])
            self.pimoroni_veml6075 = int(self.config_settings[17])
            self.pimoroni_matrix_11x7 = int(self.config_settings[18])
            self.pimoroni_st7735 = int(self.config_settings[19])
            self.pimoroni_mono_oled_luma = int(self.config_settings[20])
            self.kootnet_dummy_sensor = int(self.config_settings[21])
            for sensor in self.config_settings:
                if sensor:
                    self.no_sensors = False
                    break
        except Exception as error:
            log_msg = "Invalid Settings detected for " + self.config_file_location + ": "
            logger.primary_logger.error(log_msg + str(error))
            bad_load += 100

        if bad_load < 99:
            # Add new Settings here.
            pass

        if bad_load:
            self.update_configuration_settings_list()
            if self.load_from_file:
                logger.primary_logger.info("Saving Installed Sensors.")
                self.save_config_to_file()

    def update_configuration_settings_list(self):
        """ Set's config_settings variable list based on current settings. """
        self.config_settings = [str(self.linux_system), str(self.raspberry_pi), str(self.raspberry_pi_sense_hat),
                                str(self.pimoroni_bh1745), str(self.pimoroni_as7262), str(self.pimoroni_mcp9600),
                                str(self.pimoroni_bmp280), str(self.pimoroni_bme680), str(self.pimoroni_enviro),
                                str(self.pimoroni_enviroplus), str(self.pimoroni_sgp30), str(self.pimoroni_pms5003),
                                str(self.pimoroni_msa301), str(self.pimoroni_lsm303d), str(self.pimoroni_icm20948),
                                str(self.pimoroni_vl53l1x), str(self.pimoroni_ltr_559), str(self.pimoroni_veml6075),
                                str(self.pimoroni_matrix_11x7), str(self.pimoroni_st7735),
                                str(self.pimoroni_mono_oled_luma), str(self.kootnet_dummy_sensor)]

    def get_raspberry_pi_model(self):
        """ Returns the local Raspberry Pi model. """
        if self.raspberry_pi and os.path.isfile("/proc/device-tree/model"):
            try:
                pi_version = str(check_output("cat /proc/device-tree/model", shell=True))[2:-5]
                logger.primary_logger.debug("Pi Version: " + str(pi_version))
                if str(pi_version)[:12] == "Raspberry Pi":
                    return str(pi_version)
            except Exception as error:
                logger.primary_logger.warning("Unable to get Raspberry Pi Model: " + str(error))
        return "Raspberry Pi"
