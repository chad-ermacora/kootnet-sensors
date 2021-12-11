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
from operations_modules.app_generic_disk import write_file_to_disk


class CreateMQTTBrokerConfiguration(CreateGeneralConfiguration):
    """ Creates the MQTT Broker Configuration object and loads settings from file (by default). """

    def __init__(self, load_from_file=True):
        CreateGeneralConfiguration.__init__(self, file_locations.mqtt_broker_config, load_from_file=load_from_file)
        self.config_file_header = "Configure MQTT Broker Server settings here. Enable = 1 & Disable = 0"
        self.valid_setting_count = 1
        self.config_settings_names = ["Enable MQTT Broker"]

        self.enable_mqtt_broker = 0

        self.update_configuration_settings_list()
        if load_from_file:
            self._init_config_variables()
            self._update_variables_from_settings_list()

    def set_config_with_str(self, config_file_text):
        super().set_config_with_str(config_file_text)
        self._update_variables_from_settings_list()

    def update_with_html_request(self, html_request):
        """ Updates the MQTT Broker configuration based on provided HTML configuration data. """
        logger.network_logger.debug("Starting HTML MQTT Broker Configuration Update Check")

        self.enable_mqtt_broker = 0
        if html_request.form.get("enable_broker_server") is not None:
            self.enable_mqtt_broker = 1
        write_file_to_disk(file_locations.mosquitto_configuration,
                           str(html_request.form.get("mosquitto_config")).strip())
        self.update_configuration_settings_list()

    def update_configuration_settings_list(self):
        """ Set's config_settings variable list based on current settings. """

        self.config_settings = [str(self.enable_mqtt_broker)]

    def _update_variables_from_settings_list(self):
        try:
            self.enable_mqtt_broker = int(self.config_settings[0])
        except Exception as error:
            logger.primary_logger.debug("MQTT Broker Config: " + str(error))
            self.update_configuration_settings_list()
            if self.load_from_file:
                logger.primary_logger.info("Saving MQTT Broker Configuration.")
                self.save_config_to_file()
