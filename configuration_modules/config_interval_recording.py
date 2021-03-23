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


class CreateIntervalRecordingConfiguration(CreateGeneralConfiguration):
    """ Creates the Interval Recording Configuration object and loads settings from file (by default). """

    def __init__(self, load_from_file=True):
        CreateGeneralConfiguration.__init__(self, file_locations.interval_config, load_from_file=load_from_file)
        self.config_file_header = "Enable = 1 and Disable = 0"
        self.valid_setting_count = 18
        self.config_settings_names = [
            "Enable interval recording", "Recording interval in seconds * Caution *", "Enable sensor uptime",
            "Enable CPU temperature", "Enable environmental temperature", "Enable pressure", "Enable humidity",
            "Enable altitude", "Enable distance", "Enable lumen", "Enable color", "Enable ultra violet", "Enable GAS",
            "Enable particulate matter", "Enable accelerometer", "Enable magnetometer", "Enable gyroscope",
            "Enable Dew Point"
        ]

        self.enable_interval_recording = 1
        self.sleep_duration_interval = 300.0

        self.enable_interval_recording = 1
        self.sensor_uptime_enabled = 1
        self.cpu_temperature_enabled = 1
        self.env_temperature_enabled = 1
        self.pressure_enabled = 1
        self.humidity_enabled = 1
        self.dew_point_enabled = 1
        self.altitude_enabled = 1
        self.distance_enabled = 1
        self.lumen_enabled = 1
        self.colour_enabled = 1
        self.ultra_violet_enabled = 1
        self.gas_enabled = 1
        self.particulate_matter_enabled = 1
        self.accelerometer_enabled = 1
        self.magnetometer_enabled = 1
        self.gyroscope_enabled = 1

        self.update_configuration_settings_list()
        if load_from_file:
            self._init_config_variables()
            self._update_variables_from_settings_list()

    def set_config_with_str(self, config_file_text):
        super().set_config_with_str(config_file_text)
        self._update_variables_from_settings_list()

    def update_with_html_request(self, html_request):
        """ Updates the Interval Recording configuration based on provided HTML configuration data. """
        logger.network_logger.debug("Starting HTML Interval Recording Configuration Update Check")

        self.enable_interval_recording = 0
        self.sensor_uptime_enabled = 0
        self.cpu_temperature_enabled = 0
        self.env_temperature_enabled = 0
        self.pressure_enabled = 0
        self.humidity_enabled = 0
        self.dew_point_enabled = 0
        self.altitude_enabled = 0
        self.distance_enabled = 0
        self.lumen_enabled = 0
        self.colour_enabled = 0
        self.ultra_violet_enabled = 0
        self.gas_enabled = 0
        self.particulate_matter_enabled = 0
        self.accelerometer_enabled = 0
        self.magnetometer_enabled = 0
        self.gyroscope_enabled = 0

        if html_request.form.get("enable_interval_recording") is not None:
            self.enable_interval_recording = 1
        if html_request.form.get("interval_delay_seconds") is not None:
            new_sleep_duration = float(html_request.form.get("interval_delay_seconds"))
            self.sleep_duration_interval = new_sleep_duration

        if html_request.form.get("sensor_uptime") is not None:
            self.sensor_uptime_enabled = 1
        if html_request.form.get("cpu_temperature") is not None:
            self.cpu_temperature_enabled = 1
        if html_request.form.get("pressure") is not None:
            self.pressure_enabled = 1
        if html_request.form.get("humidity") is not None:
            self.humidity_enabled = 1
        if html_request.form.get("dew_point") is not None:
            self.dew_point_enabled = 1
        if html_request.form.get("gas") is not None:
            self.gas_enabled = 1
        if html_request.form.get("particulate_matter") is not None:
            self.particulate_matter_enabled = 1
        if html_request.form.get("accelerometer") is not None:
            self.accelerometer_enabled = 1
        if html_request.form.get("magnetometer") is not None:
            self.magnetometer_enabled = 1
        if html_request.form.get("env_temperature") is not None:
            self.env_temperature_enabled = 1
        if html_request.form.get("altitude") is not None:
            self.altitude_enabled = 1
        if html_request.form.get("distance") is not None:
            self.distance_enabled = 1
        if html_request.form.get("lumen") is not None:
            self.lumen_enabled = 1
        if html_request.form.get("colour") is not None:
            self.colour_enabled = 1
        if html_request.form.get("ultra_violet") is not None:
            self.ultra_violet_enabled = 1
        if html_request.form.get("gyroscope") is not None:
            self.gyroscope_enabled = 1
        self.update_configuration_settings_list()

    def update_configuration_settings_list(self):
        """ Set's config_settings variable list based on current settings. """

        self.config_settings = [
            str(self.enable_interval_recording), str(self.sleep_duration_interval), str(self.sensor_uptime_enabled),
            str(self.cpu_temperature_enabled), str(self.env_temperature_enabled), str(self.pressure_enabled),
            str(self.humidity_enabled), str(self.altitude_enabled), str(self.distance_enabled), str(self.lumen_enabled),
            str(self.colour_enabled), str(self.ultra_violet_enabled), str(self.gas_enabled),
            str(self.particulate_matter_enabled), str(self.accelerometer_enabled), str(self.magnetometer_enabled),
            str(self.gyroscope_enabled), str(self.dew_point_enabled)
        ]

    def _update_variables_from_settings_list(self):
        try:
            self.enable_interval_recording = int(self.config_settings[0])
            self.sleep_duration_interval = float(self.config_settings[1])
            self.sensor_uptime_enabled = int(self.config_settings[2])
            self.cpu_temperature_enabled = int(self.config_settings[3])
            self.env_temperature_enabled = int(self.config_settings[4])
            self.pressure_enabled = int(self.config_settings[5])
            self.humidity_enabled = int(self.config_settings[6])
            self.altitude_enabled = int(self.config_settings[7])
            self.distance_enabled = int(self.config_settings[8])
            self.lumen_enabled = int(self.config_settings[9])
            self.colour_enabled = int(self.config_settings[10])
            self.ultra_violet_enabled = int(self.config_settings[11])
            self.gas_enabled = int(self.config_settings[12])
            self.particulate_matter_enabled = int(self.config_settings[13])
            self.accelerometer_enabled = int(self.config_settings[14])
            self.magnetometer_enabled = int(self.config_settings[15])
            self.gyroscope_enabled = int(self.config_settings[16])
            self.dew_point_enabled = int(self.config_settings[17])
        except Exception as error:
            if self.load_from_file:
                logger.primary_logger.debug("Interval Config: " + str(error))
            self.update_configuration_settings_list()
            if self.load_from_file:
                logger.primary_logger.info("Saving Interval Recording Configuration.")
                self.save_config_to_file()
