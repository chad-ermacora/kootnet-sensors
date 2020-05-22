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
import random
from operations_modules import logger
from operations_modules import file_locations
from operations_modules.app_generic_functions import CreateGeneralConfiguration


class CreateMQTTPublisherConfiguration(CreateGeneralConfiguration):
    """ Creates the MQTT Publisher Configuration object and loads settings from file (by default). """

    def __init__(self, load_from_file=True):
        CreateGeneralConfiguration.__init__(self, file_locations.mqtt_publisher_config, load_from_file=load_from_file)
        self.config_file_header = "Configure MQTT Publish Settings here. Enable = 1 & Disable = 0"
        self.valid_setting_count = 38
        self.config_settings_names = ["Enable MQTT Publisher", "Broker Server Address", "Broker Port #",
                                      "Enable Authentication", "User Name (Optional)", "Password (Optional)",
                                      "Seconds Between Reading Posts", "Publish System Uptime",
                                      "Publish CPU Temperature", "Publish Environmental Temperature",
                                      "Publish Pressure", "Publish Altitude", "Publish Humidity", "Publish Distance",
                                      "Publish GAS", "Publish Particulate Matter", "Publish Lumen", "Publish Colors",
                                      "Publish Ultra Violet", "Publish Accelerometer", "Publish Magnetometer",
                                      "Publish Gyroscope", "System Uptime Topic", "CPU Temperature Topic",
                                      "Environmental Temperature Topic", "Pressure Topic", "Altitude Topic",
                                      "Humidity Topic", "Distance Topic", "GAS Topic", "Particulate Matter Topic",
                                      "Lumen Topic", "Colors Topic", "Ultra Violet Topic", "Accelerometer Topic",
                                      "Magnetometer Topic", "Gyroscope Topic", "Publisher Quality of Service Level"]

        self.enable_mqtt_publisher = 0
        self.broker_address = ""
        self.broker_server_port = 1883
        self.enable_broker_auth = 0
        self.broker_user = ""
        self.broker_password = ""
        self.seconds_to_wait = 60

        self.mqtt_publisher_qos = 0

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

        self.mqtt_base_topic = "KS/Default" + str(random.randint(100000, 999999)) + "/"

        self.send_all_as_json_topic = self.mqtt_base_topic + "JSON"
        self.sensor_uptime_topic = self.mqtt_base_topic + "SystemUpTime"
        self.system_temperature_topic = self.mqtt_base_topic + "SystemTemperature"
        self.env_temperature_topic = self.mqtt_base_topic + "EnvironmentTemperature"
        self.pressure_topic = self.mqtt_base_topic + "Pressure"
        self.altitude_topic = self.mqtt_base_topic + "Altitude"
        self.humidity_topic = self.mqtt_base_topic + "Humidity"
        self.distance_topic = self.mqtt_base_topic + "Distance"
        self.gas_topic = self.mqtt_base_topic + "Gas"
        self.particulate_matter_topic = self.mqtt_base_topic + "ParticulateMatter"
        self.lumen_topic = self.mqtt_base_topic + "Lumen"
        self.color_topic = self.mqtt_base_topic + "Color"
        self.ultra_violet_topic = self.mqtt_base_topic + "UltraViolet"
        self.accelerometer_topic = self.mqtt_base_topic + "Accelerometer"
        self.magnetometer_topic = self.mqtt_base_topic + "Magnetometer"
        self.gyroscope_topic = self.mqtt_base_topic + "Gyroscope"

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

        if html_request.form.get("publish_qos_level") is not None:
            qos_level = html_request.form.get("publish_qos_level")
            if qos_level == "0":
                self.mqtt_publisher_qos = 0
            else:
                self.mqtt_publisher_qos = int(qos_level)

        if html_request.form.get("enable_broker_auth") is not None:
            self.enable_broker_auth = 1
        if html_request.form.get("broker_username") is not None:
            self.broker_user = str(html_request.form.get("broker_username"))
        if html_request.form.get("broker_password") is not None:
            self.broker_password = str(html_request.form.get("broker_password"))
        if html_request.form.get("publish_seconds_wait") is not None:
            self.seconds_to_wait = int(html_request.form.get("publish_seconds_wait"))

        if html_request.form.get("mqtt_system_uptime") is not None:
            self.sensor_uptime = 1
        if html_request.form.get("mqtt_cpu_temp") is not None:
            self.system_temperature = 1
        if html_request.form.get("mqtt_env_temp") is not None:
            self.env_temperature = 1
        if html_request.form.get("mqtt_pressure") is not None:
            self.pressure = 1
        if html_request.form.get("mqtt_altitude") is not None:
            self.altitude = 1
        if html_request.form.get("mqtt_humidity") is not None:
            self.humidity = 1
        if html_request.form.get("mqtt_distance") is not None:
            self.distance = 1
        if html_request.form.get("mqtt_gas") is not None:
            self.gas = 1
        if html_request.form.get("mqtt_particulate_matter") is not None:
            self.particulate_matter = 1
        if html_request.form.get("mqtt_lumen") is not None:
            self.lumen = 1
        if html_request.form.get("mqtt_colours") is not None:
            self.color = 1
        if html_request.form.get("mqtt_ultra_violet") is not None:
            self.ultra_violet = 1
        if html_request.form.get("mqtt_accelerometer") is not None:
            self.accelerometer = 1
        if html_request.form.get("mqtt_magnetometer") is not None:
            self.magnetometer = 1
        if html_request.form.get("mqtt_gyroscope") is not None:
            self.gyroscope = 1

        if html_request.form.get("topic_mqtt_system_uptime").strip() != "":
            self.sensor_uptime_topic = html_request.form.get("topic_mqtt_system_uptime")
        if html_request.form.get("topic_mqtt_cpu_temp").strip() != "":
            self.system_temperature_topic = html_request.form.get("topic_mqtt_cpu_temp")
        if html_request.form.get("topic_mqtt_env_temp").strip() != "":
            self.env_temperature_topic = html_request.form.get("topic_mqtt_env_temp")
        if html_request.form.get("topic_mqtt_pressure").strip() != "":
            self.pressure_topic = html_request.form.get("topic_mqtt_pressure")
        if html_request.form.get("topic_mqtt_altitude").strip() != "":
            self.altitude_topic = html_request.form.get("topic_mqtt_altitude")
        if html_request.form.get("topic_mqtt_humidity").strip() != "":
            self.humidity_topic = html_request.form.get("topic_mqtt_humidity")
        if html_request.form.get("topic_mqtt_distance").strip() != "":
            self.distance_topic = html_request.form.get("topic_mqtt_distance")
        if html_request.form.get("topic_mqtt_gas").strip() != "":
            self.gas_topic = html_request.form.get("topic_mqtt_gas")
        if html_request.form.get("topic_mqtt_particulate_matter").strip() != "":
            self.particulate_matter_topic = html_request.form.get("topic_mqtt_particulate_matter")
        if html_request.form.get("topic_mqtt_lumen").strip() != "":
            self.lumen_topic = html_request.form.get("topic_mqtt_lumen")
        if html_request.form.get("topic_mqtt_colours").strip() != "":
            self.color_topic = html_request.form.get("topic_mqtt_colours")
        if html_request.form.get("topic_mqtt_ultra_violet").strip() != "":
            self.ultra_violet_topic = html_request.form.get("topic_mqtt_ultra_violet")
        if html_request.form.get("topic_mqtt_accelerometer").strip() != "":
            self.accelerometer_topic = html_request.form.get("topic_mqtt_accelerometer")
        if html_request.form.get("topic_mqtt_magnetometer").strip() != "":
            self.magnetometer_topic = html_request.form.get("topic_mqtt_magnetometer")
        if html_request.form.get("topic_mqtt_gyroscope").strip() != "":
            self.gyroscope_topic = html_request.form.get("topic_mqtt_gyroscope")
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
                                str(self.gyroscope),
                                str(self.sensor_uptime_topic),
                                str(self.system_temperature_topic),
                                str(self.env_temperature_topic),
                                str(self.pressure_topic),
                                str(self.altitude_topic),
                                str(self.humidity_topic),
                                str(self.distance_topic),
                                str(self.gas_topic),
                                str(self.particulate_matter_topic),
                                str(self.lumen_topic),
                                str(self.color_topic),
                                str(self.ultra_violet_topic),
                                str(self.accelerometer_topic),
                                str(self.magnetometer_topic),
                                str(self.gyroscope_topic),
                                str(self.mqtt_publisher_qos)]

    def _update_variables_from_settings_list(self):
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

            self.sensor_uptime_topic = self.config_settings[22].strip()
            self.system_temperature_topic = self.config_settings[23].strip()
            self.env_temperature_topic = self.config_settings[24].strip()
            self.pressure_topic = self.config_settings[25].strip()
            self.altitude_topic = self.config_settings[26].strip()
            self.humidity_topic = self.config_settings[27].strip()
            self.distance_topic = self.config_settings[28].strip()
            self.gas_topic = self.config_settings[29].strip()
            self.particulate_matter_topic = self.config_settings[30].strip()
            self.lumen_topic = self.config_settings[31].strip()
            self.color_topic = self.config_settings[32].strip()
            self.ultra_violet_topic = self.config_settings[33].strip()
            self.accelerometer_topic = self.config_settings[34].strip()
            self.magnetometer_topic = self.config_settings[35].strip()
            self.gyroscope_topic = self.config_settings[36].strip()

            self.mqtt_publisher_qos = int(self.config_settings[37].strip())
        except Exception as error:
            logger.primary_logger.debug("MQTT Publisher Config: " + str(error))
            self._update_configuration_settings_list()
            if self.load_from_file:
                logger.primary_logger.info("Saving MQTT Publisher Configuration.")
                self.save_config_to_file()
