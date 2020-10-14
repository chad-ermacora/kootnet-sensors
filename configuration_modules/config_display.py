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


class CreateDisplayConfiguration(CreateGeneralConfiguration):
    """ Creates the Display Configuration object and loads settings from file (by default). """

    def __init__(self, load_from_file=True):
        CreateGeneralConfiguration.__init__(self, file_locations.display_config, load_from_file=load_from_file)
        self.config_file_header = "Enable = 1 and Disable = 0"
        self.valid_setting_count = 18
        self.config_settings_names = [
            "Enable display", "Display every minutes", "Display type", "Show sensor uptime",
            "Show system temperature", "Show environmental temperature", "Show pressure", "Show altitude",
            "Show humidity", "Show distance", "Show GAS", "Show particulate matter", "Show lumen", "Show colors",
            "Show ultra violet", "Show accelerometer", "Show magnetometer", "Show gyroscope"
        ]

        self.enable_display = 0
        self.display_type_numerical = "numerical"
        self.display_type_graph = "graph"

        self.minutes_between_display = 60
        self.display_type = self.display_type_numerical

        # Enable or Disable Sensors to Display.  0 = Disabled, 1 = Enabled
        self.sensor_uptime = 0
        self.system_temperature = 1
        self.env_temperature = 0
        self.pressure = 0
        self.altitude = 0
        self.humidity = 0
        self.distance = 0
        self.gas = 0
        self.particulate_matter = 0
        self.lumen = 0
        self.color = 0
        self.ultra_violet = 0
        self.accelerometer = 0
        self.magnetometer = 0
        self.gyroscope = 0

        self.update_configuration_settings_list()
        if load_from_file:
            self._init_config_variables()
            self._update_variables_from_settings_list()

    def set_config_with_str(self, config_file_text):
        super().set_config_with_str(config_file_text)
        self._update_variables_from_settings_list()

    def update_with_html_request(self, html_request):
        """ Updates the Display configuration based on provided HTML configuration data. """
        logger.network_logger.debug("Starting HTML Display Configuration Update Check")

        self.enable_display = 0
        self.sensor_uptime = 0
        self.system_temperature = 0
        self.env_temperature = 0
        self.pressure = 0
        self.altitude = 0
        self.humidity = 0
        self.distance = 0
        self.gas = 0
        self.particulate_matter = 0
        self.lumen = 0
        self.color = 0
        self.ultra_violet = 0
        self.accelerometer = 0
        self.magnetometer = 0
        self.gyroscope = 0

        if html_request.form.get("enable_display") is not None:
            self.enable_display = 1

        if html_request.form.get("display_interval_delay_min") is not None:
            try:
                self.minutes_between_display = int(html_request.form.get("display_interval_delay_min"))
            except Exception as error:
                logger.network_logger.error("Error setting Display delay minutes: " + str(error))

        if html_request.form.get("display_type") is not None:
            self.display_type = html_request.form.get("display_type")

        if html_request.form.get("DisplaySensorUptime") is not None:
            self.sensor_uptime = 1
        if html_request.form.get("DisplayCPUTemp") is not None:
            self.system_temperature = 1
        if html_request.form.get("DisplayEnvTemp") is not None:
            self.env_temperature = 1
        if html_request.form.get("DisplayPressure") is not None:
            self.pressure = 1
        if html_request.form.get("DisplayAltitude") is not None:
            self.altitude = 1
        if html_request.form.get("DisplayHumidity") is not None:
            self.humidity = 1
        if html_request.form.get("DisplayDistance") is not None:
            self.distance = 1
        if html_request.form.get("DisplayGas") is not None:
            self.gas = 1
        if html_request.form.get("DisplayParticulateMatter") is not None:
            self.particulate_matter = 1
        if html_request.form.get("DisplayLumen") is not None:
            self.lumen = 1
        if html_request.form.get("DisplayColours") is not None:
            self.color = 1
        if html_request.form.get("DisplayUltraViolet") is not None:
            self.ultra_violet = 1
        if html_request.form.get("DisplayAccelerometer") is not None:
            self.accelerometer = 1
        if html_request.form.get("DisplayMagnetometer") is not None:
            self.magnetometer = 1
        if html_request.form.get("DisplayGyroscope") is not None:
            self.gyroscope = 1
        self.update_configuration_settings_list()
        self.load_from_file = True

    def update_configuration_settings_list(self):
        """ Set's config_settings variable list based on current settings. """

        self.config_settings = [
            str(self.enable_display), str(self.minutes_between_display), str(self.display_type),
            str(self.sensor_uptime), str(self.system_temperature), str(self.env_temperature), str(self.pressure),
            str(self.altitude), str(self.humidity), str(self.distance), str(self.gas), str(self.particulate_matter),
            str(self.lumen), str(self.color), str(self.ultra_violet), str(self.accelerometer), str(self.magnetometer),
            str(self.gyroscope)
        ]

    def _update_variables_from_settings_list(self):
        try:
            self.enable_display = int(self.config_settings[0])
            self.minutes_between_display = int(self.config_settings[1])
            self.display_type = str(self.config_settings[2]).strip()
            if self.display_type != self.display_type_numerical and self.display_type != self.display_type_graph:
                self.display_type = self.display_type_numerical
            self.sensor_uptime = int(self.config_settings[3])
            self.system_temperature = int(self.config_settings[4])
            self.env_temperature = int(self.config_settings[5])
            self.pressure = int(self.config_settings[6])
            self.altitude = int(self.config_settings[7])
            self.humidity = int(self.config_settings[8])
            self.distance = int(self.config_settings[9])
            self.gas = int(self.config_settings[10])
            self.particulate_matter = int(self.config_settings[11])
            self.lumen = int(self.config_settings[12])
            self.color = int(self.config_settings[13])
            self.ultra_violet = int(self.config_settings[14])
            self.accelerometer = int(self.config_settings[15])
            self.magnetometer = int(self.config_settings[16])
            self.gyroscope = int(self.config_settings[17])
        except Exception as error:
            logger.primary_logger.debug("Display Config: " + str(error))
            self.update_configuration_settings_list()
            if self.load_from_file:
                logger.primary_logger.info("Saving Display Configuration.")
                self.save_config_to_file()
