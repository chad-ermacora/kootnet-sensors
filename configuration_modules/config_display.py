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


class CreateDisplaySensorsVariables:
    """ Create a object instance holding Sensor Display Variables (Such as sensor types to display). """

    def __init__(self):
        self.sensor_uptime = "UpTime"
        self.system_temperature = "SysTemp"
        self.env_temperature = "EnvTemp"
        self.pressure = "Pressure"
        self.altitude = "Altitude"
        self.humidity = "Humidity"
        self.distance = "Distance"
        self.gas = "Gas"
        self.particulate_matter = "PM"
        self.lumen = "Lumen"
        self.color = "Color"
        self.ultra_violet = "UV"

        self.accelerometer = "Acc"
        self.magnetometer = "Mag"
        self.gyroscope = "Gyro"


class CreateDisplayConfiguration(CreateGeneralConfiguration):
    """ Creates the Primary Configuration object and loads settings from file (by default). """

    def __init__(self, load_from_file=True):
        CreateGeneralConfiguration.__init__(self, file_locations.display_config, load_from_file=load_from_file)
        self.config_file_header = "Enable = 1 & Disable = 0"
        self.valid_setting_count = 3
        self.config_settings_names = ["Display every X Minutes", "Display Type", "Sensors to Display"]

        self.display_variables = CreateDisplaySensorsVariables()
        self.display_type_numerical = "numerical"
        self.display_type_graph = "graph"

        self.minutes_between_display = 60
        self.display_type = self.display_type_numerical

        self.sensors_to_display = {self.display_variables.sensor_uptime: False,
                                   self.display_variables.system_temperature: False,
                                   self.display_variables.env_temperature: False,
                                   self.display_variables.pressure: False,
                                   self.display_variables.altitude: False,
                                   self.display_variables.humidity: False,
                                   self.display_variables.distance: False,
                                   self.display_variables.gas: False,
                                   self.display_variables.particulate_matter: False,
                                   self.display_variables.lumen: False,
                                   self.display_variables.color: False,
                                   self.display_variables.ultra_violet: False,
                                   self.display_variables.accelerometer: False,
                                   self.display_variables.magnetometer: False,
                                   self.display_variables.gyroscope: False}

        self._update_configuration_settings_list()
        if load_from_file:
            self._init_config_variables()
            self._update_variables_from_settings_list()

    def set_config_with_str(self, config_file_text):
        super().set_config_with_str(config_file_text)
        self._update_variables_from_settings_list()

    def update_with_html_request(self, html_request):
        """ Updates the Display configuration based on provided HTML configuration data. """
        logger.network_logger.debug("Starting HTML Display Configuration Update Check")
        self.__init__(load_from_file=False)
        if html_request.form.get("display_interval_delay_min") is not None:
            try:
                self.minutes_between_display = int(html_request.form.get("display_interval_delay_min"))
            except Exception as error:
                logger.network_logger.error("Error setting Display delay minutes: " + str(error))

        if html_request.form.get("display_type") is not None:
            self.display_type = html_request.form.get("display_type")

        if html_request.form.get("DisplaySensorUptime") is not None:
            self.sensors_to_display[self.display_variables.sensor_uptime] = True
        if html_request.form.get("DisplayCPUTemp") is not None:
            self.sensors_to_display[self.display_variables.system_temperature] = True
        if html_request.form.get("DisplayEnvTemp") is not None:
            self.sensors_to_display[self.display_variables.env_temperature] = True
        if html_request.form.get("DisplayPressure") is not None:
            self.sensors_to_display[self.display_variables.pressure] = True
        if html_request.form.get("DisplayAltitude") is not None:
            self.sensors_to_display[self.display_variables.altitude] = True
        if html_request.form.get("DisplayHumidity") is not None:
            self.sensors_to_display[self.display_variables.humidity] = True
        if html_request.form.get("DisplayDistance") is not None:
            self.sensors_to_display[self.display_variables.distance] = True
        if html_request.form.get("DisplayGas") is not None:
            self.sensors_to_display[self.display_variables.gas] = True
        if html_request.form.get("DisplayParticulateMatter") is not None:
            self.sensors_to_display[self.display_variables.particulate_matter] = True
        if html_request.form.get("DisplayLumen") is not None:
            self.sensors_to_display[self.display_variables.lumen] = True
        if html_request.form.get("DisplayColours") is not None:
            self.sensors_to_display[self.display_variables.color] = True
        if html_request.form.get("DisplayUltraViolet") is not None:
            self.sensors_to_display[self.display_variables.ultra_violet] = True
        if html_request.form.get("DisplayAccelerometer") is not None:
            self.sensors_to_display[self.display_variables.accelerometer] = True
        if html_request.form.get("DisplayMagnetometer") is not None:
            self.sensors_to_display[self.display_variables.magnetometer] = True
        if html_request.form.get("DisplayGyroscope") is not None:
            self.sensors_to_display[self.display_variables.gyroscope] = True
        self._update_configuration_settings_list()
        self.load_from_file = True

    def _update_configuration_settings_list(self):
        """ Set's config_settings variable list based on current settings. """
        sensors_str = ""
        for config in self.sensors_to_display:
            sensors_str += str(config) + ":" + str(self.sensors_to_display[config]) + ","
        sensors_str = sensors_str[:-1].strip()
        self.config_settings = [str(self.minutes_between_display), str(self.display_type), sensors_str]

    def _update_variables_from_settings_list(self):
        bad_load = 0
        try:
            self.minutes_between_display = int(self.config_settings[0])
            self.display_type = self.config_settings[1]
            temp_sensors_list = self.config_settings[2].split(",")
            for sensor in temp_sensors_list:
                sensor_split = sensor.split(":")
                if str(sensor_split[1]).strip() == "True":
                    self.sensors_to_display[str(sensor_split[0]).strip()] = True
                else:
                    self.sensors_to_display[str(sensor_split[0]).strip()] = False
        except Exception as error:
            if self.load_from_file:
                log_msg = "Invalid Settings detected for " + self.config_file_location + ": "
                logger.primary_logger.error(log_msg + str(error))
            bad_load += 100

        # if bad_load < 99:
        #     try:
        #         self.web_portal_port = int(self.config_settings[7])
        #     except Exception as error:
        #         if self.load_from_file:
        #             logger.primary_logger.error("HTTPS Web Portal port number not found, using default.")
        #             logger.primary_logger.debug(str(error))
        #         bad_load += 1

        if bad_load:
            self._update_configuration_settings_list()
            if self.load_from_file:
                logger.primary_logger.info("Saving Display Configuration.")
                self.save_config_to_file()
