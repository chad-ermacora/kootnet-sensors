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


class CreateMQTTPublisherConfiguration(CreateGeneralConfiguration):
    """ Creates the MQTT Publisher Configuration object and loads settings from file (by default). """

    def __init__(self, load_from_file=True):
        CreateGeneralConfiguration.__init__(self, file_locations.mqtt_publisher_config, load_from_file=load_from_file)
        self.config_file_header = "Configure MQTT Publish Settings here. Enable = 1 & Disable = 0"
        self.valid_setting_count = 22
        self.config_settings_names = ["Enable MQTT Publisher", "Broker Server Address", "Broker Port #",
                                      "Enable Authentication", "User Name (Optional)", "Password (Optional)",
                                      "Seconds Between Reading Posts", "Publish System Uptime",
                                      "Publish CPU Temperature", "Publish Environmental Temperature",
                                      "Publish Pressure", "Publish Altitude", "Publish Humidity", "Publish Distance",
                                      "Publish GAS", "Publish Particulate Matter", "Publish Lumen", "Publish Colors",
                                      "Publish Ultra Violet", "Publish Accelerometer", "Publish Magnetometer",
                                      "Publish Gyroscope"]

        self.enable_mqtt_publisher = 0
        self.broker_address = ""
        self.broker_server_port = 1883
        self.enable_broker_auth = 0
        self.broker_user = ""
        self.broker_password = ""
        self.seconds_to_wait = 60
        self.mqtt_base_topic = "KS/"

        self.send_all_as_json = 0
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

        self._update_configuration_settings_list()
        if load_from_file:
            self._init_config_variables()
            self._update_variables_from_settings_list()

    def set_config_with_str(self, config_file_text):
        super().set_config_with_str(config_file_text)
        self._update_variables_from_settings_list()

    def update_with_html_request(self, html_request):
        """ Updates the MQTT Publisher configuration based on provided HTML configuration data. """
        logger.network_logger.debug("Starting HTML MQTT Publisher Configuration Update Check")
        self.__init__(load_from_file=False)
        if html_request.form.get("enable_mqtt_publisher") is not None:
            self.enable_mqtt_publisher = 1
        if html_request.form.get("publish_broker_address") is not None:
            self.broker_address = html_request.form.get("publish_broker_address")
        if html_request.form.get("publish_broker_port") is not None:
            try:
                self.broker_server_port = int(html_request.form.get("publish_broker_port"))
            except Exception as error:
                logger.network_logger.error("Invalid Broker Port #: " + str(error))
        if html_request.form.get("enable_broker_auth") is not None:
            self.enable_broker_auth = 1
        if html_request.form.get("broker_username") is not None:
            self.broker_user = str(html_request.form.get("broker_username"))
        if html_request.form.get("broker_password") is not None:
            self.broker_password = str(html_request.form.get("broker_password"))
        if html_request.form.get("publish_seconds_wait") is not None:
            self.seconds_to_wait = int(html_request.form.get("publish_seconds_wait"))
        if html_request.form.get("MQTTSensorUptime") is not None:
            self.sensor_uptime = 1
        if html_request.form.get("MQTTCPUTemp") is not None:
            self.system_temperature = 1
        if html_request.form.get("MQTTEnvTemp") is not None:
            self.env_temperature = 1
        if html_request.form.get("MQTTPressure") is not None:
            self.pressure = 1
        if html_request.form.get("MQTTAltitude") is not None:
            self.altitude = 1
        if html_request.form.get("MQTTHumidity") is not None:
            self.humidity = 1
        if html_request.form.get("MQTTDistance") is not None:
            self.distance = 1
        if html_request.form.get("MQTTGas") is not None:
            self.gas = 1
        if html_request.form.get("MQTTParticulateMatter") is not None:
            self.particulate_matter = 1
        if html_request.form.get("MQTTLumen") is not None:
            self.lumen = 1
        if html_request.form.get("MQTTColours") is not None:
            self.color = 1
        if html_request.form.get("MQTTUltraViolet") is not None:
            self.ultra_violet = 1
        if html_request.form.get("MQTTAccelerometer") is not None:
            self.accelerometer = 1
        if html_request.form.get("MQTTMagnetometer") is not None:
            self.magnetometer = 1
        if html_request.form.get("MQTTGyroscope") is not None:
            self.gyroscope = 1
        self._update_configuration_settings_list()
        self.load_from_file = True

    def _update_configuration_settings_list(self):
        """ Set's config_settings variable list based on current settings. """
        self.config_settings = [str(self.enable_mqtt_publisher),
                                str(self.broker_address),
                                str(self.broker_server_port),
                                str(self.enable_broker_auth),
                                str(self.broker_user),
                                str(self.broker_password),
                                str(self.seconds_to_wait),
                                str(self.sensor_uptime),
                                str(self.system_temperature),
                                str(self.env_temperature),
                                str(self.pressure),
                                str(self.altitude),
                                str(self.humidity),
                                str(self.distance),
                                str(self.gas),
                                str(self.particulate_matter),
                                str(self.lumen),
                                str(self.color),
                                str(self.ultra_violet),
                                str(self.accelerometer),
                                str(self.magnetometer),
                                str(self.gyroscope)]

    def _update_variables_from_settings_list(self):
        bad_load = 0
        try:
            self.enable_mqtt_publisher = int(self.config_settings[0])
            self.broker_address = self.config_settings[1]
            self.broker_server_port = int(self.config_settings[2])
            self.enable_broker_auth = int(self.config_settings[3])
            self.broker_user = self.config_settings[4]
            self.broker_password = self.config_settings[5]
            self.seconds_to_wait = int(self.config_settings[6])
            self.sensor_uptime = int(self.config_settings[7])
            self.system_temperature = int(self.config_settings[8])
            self.env_temperature = int(self.config_settings[9])
            self.pressure = int(self.config_settings[10])
            self.altitude = int(self.config_settings[11])
            self.humidity = int(self.config_settings[12])
            self.distance = int(self.config_settings[13])
            self.gas = int(self.config_settings[14])
            self.particulate_matter = int(self.config_settings[15])
            self.lumen = int(self.config_settings[16])
            self.color = int(self.config_settings[17])
            self.ultra_violet = int(self.config_settings[18])
            self.accelerometer = int(self.config_settings[19])
            self.magnetometer = int(self.config_settings[20])
            self.gyroscope = int(self.config_settings[21])
        except Exception as error:
            if self.load_from_file:
                log_msg = "Invalid Settings detected for " + self.config_file_location + ": "
                logger.primary_logger.error(log_msg + str(error))
            bad_load += 100

        # if bad_load < 99:
        #     try:
        #         self.web_portal_port = int(self.config_settings[7)
        #     except Exception as error:
        #         if self.load_from_file:
        #             logger.primary_logger.error("HTTPS Web Portal port number not found, using default.")
        #             logger.primary_logger.debug(str(error))
        #         bad_load += 1

        if bad_load:
            self._update_configuration_settings_list()
            if self.load_from_file:
                logger.primary_logger.info("Saving MQTT Publisher Configuration.")
                self.save_config_to_file()
