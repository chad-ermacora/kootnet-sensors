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


class CreateMQTTSubscriberConfiguration(CreateGeneralConfiguration):
    """ Creates the MQTT Subscriber Configuration object and loads settings from file (by default). """

    def __init__(self, load_from_file=True):
        CreateGeneralConfiguration.__init__(self, file_locations.mqtt_subscriber_config, load_from_file=load_from_file)
        self.config_file_header = "Configure MQTT Subscriber Settings here. Enable = 1 & Disable = 0"
        self.valid_setting_count = 9
        self.config_settings_names = [
            "Enable MQTT Subscriber", "Broker Server Address", "Broker Port #", "Enable Authentication",
            "User Name (Optional)", "Password (Optional)", "MQTT Quality of Service Level (0-2)",
            "Topics as CSV Eg. KS/Sensor32/EnvironmentTemperature,KS/Sensor12/#", "Enable MQTT write to SQL DB"
        ]

        self.enable_mqtt_subscriber = 0
        self.enable_mqtt_sql_recording = 0

        self.broker_address = ""
        self.broker_server_port = 1883
        self.enable_broker_auth = 0
        self.broker_user = ""
        self.broker_password = ""
        self.subscribed_topics_list = ["#"]

        self.mqtt_subscriber_qos = 0

        self._update_configuration_settings_list()
        if load_from_file:
            self._init_config_variables()
            self._update_variables_from_settings_list()

    def set_config_with_str(self, config_file_text):
        super().set_config_with_str(config_file_text)
        self._update_variables_from_settings_list()

    def update_with_html_request(self, html_request):
        """ Updates the MQTT Subscriber configuration based on provided HTML configuration data. """
        logger.network_logger.debug("Starting HTML MQTT Subscriber Configuration Update Check")

        self.enable_mqtt_subscriber = 0
        self.enable_mqtt_sql_recording = 0
        self.enable_broker_auth = 0

        if html_request.form.get("enable_mqtt_subscriber") is not None:
            self.enable_mqtt_subscriber = 1
        if html_request.form.get("enable_mqtt_sql_recording") is not None:
            self.enable_mqtt_sql_recording = 1

        if html_request.form.get("sub_broker_address") is not None:
            self.broker_address = html_request.form.get("sub_broker_address")
        if html_request.form.get("sub_broker_port") is not None:
            try:
                self.broker_server_port = int(html_request.form.get("sub_broker_port"))
            except Exception as error:
                logger.network_logger.error("Invalid Broker Port #: " + str(error))

        if html_request.form.get("enable_broker_auth") is not None:
            self.enable_broker_auth = 1
            self.broker_user = str(html_request.form.get("broker_username"))
            broker_pass = str(html_request.form.get("broker_password"))
            if broker_pass != "":
                self.broker_password = broker_pass
        else:
            self.broker_user = ""
            self.broker_password = ""

        if html_request.form.get("mqtt_qos_level") is not None:
            self.mqtt_subscriber_qos = int(html_request.form.get("mqtt_qos_level"))
        if html_request.form.get("subscriber_topics") is not None:
            topics_text_list = str(html_request.form.get("subscriber_topics")).split(",")
            self.subscribed_topics_list = []
            for topic in topics_text_list:
                self.subscribed_topics_list.append(topic.strip())
        self._update_configuration_settings_list()
        self.load_from_file = True

    def _update_configuration_settings_list(self):
        """ Set's config_settings variable list based on current settings. """

        topics_text = ""
        for topic in self.subscribed_topics_list:
            topics_text += topic + ","
        topics_text = topics_text[:-1]
        self.config_settings = [
            str(self.enable_mqtt_subscriber), str(self.broker_address), str(self.broker_server_port),
            str(self.enable_broker_auth), str(self.broker_user), str(self.broker_password),
            str(self.mqtt_subscriber_qos), topics_text, str(self.enable_mqtt_sql_recording)
        ]

    def _update_variables_from_settings_list(self):
        try:
            self.enable_mqtt_subscriber = int(self.config_settings[0])
            self.broker_address = self.config_settings[1]
            self.broker_server_port = int(self.config_settings[2])
            self.enable_broker_auth = int(self.config_settings[3])
            self.broker_user = self.config_settings[4]
            self.broker_password = self.config_settings[5]
            self.mqtt_subscriber_qos = int(self.config_settings[6])
            topics_text_list = self.config_settings[7].split(",")
            self.subscribed_topics_list = []
            for topic in topics_text_list:
                if topic.strip() != "":
                    self.subscribed_topics_list.append(topic.strip())
            self.enable_mqtt_sql_recording = int(self.config_settings[8])
        except Exception as error:
            logger.primary_logger.debug("MQTT Subscriber Config: " + str(error))
            self._update_configuration_settings_list()
            if self.load_from_file:
                logger.primary_logger.info("Saving MQTT Subscriber Configuration.")
                self.save_config_to_file()
