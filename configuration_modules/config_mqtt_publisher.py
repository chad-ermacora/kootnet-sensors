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
from datetime import datetime
from operations_modules import logger
from operations_modules import file_locations
from operations_modules.app_generic_classes import CreateGeneralConfiguration
from operations_modules import app_cached_variables

database_variables = app_cached_variables.database_variables


class CreateMQTTPublisherConfiguration(CreateGeneralConfiguration):
    """ Creates the MQTT Publisher Configuration object and loads settings from file (by default). """

    def __init__(self, load_from_file=True):
        CreateGeneralConfiguration.__init__(self, file_locations.mqtt_publisher_config, load_from_file=load_from_file)
        self.config_file_header = "Configure MQTT Publish Settings here. Enable = 1 & Disable = 0"
        self.valid_setting_count = 73
        self.config_settings_names = [
            "Enable MQTT Publisher", "Broker Server Address", "Broker Port #", "Enable Authentication",
            "User Name (Optional)", "Password (Optional)", "Seconds Between Reading Posts",
            "MQTT Quality of Service Level (0-2)", "MQTT Base Topic", "Selected MQTT Format to Send",
            "Custom Date Time Format", "Publish System Host Name", "Publish System IP", "Publish System Uptime",
            "Publish System Date & Time", "Publish CPU Temperature", "Publish Environmental Temperature",
            "Publish Pressure", "Publish Altitude", "Publish Humidity", "Publish Distance", "Publish GAS",
            "Publish Particulate Matter", "Publish Lumen", "Publish Colors", "Publish Ultra Violet",
            "Publish Accelerometer", "Publish Magnetometer", "Publish Gyroscope", "System Host Name Topic",
            "System IP Topic", "System Uptime Topic", "System Date & Time Topic", "CPU Temperature Topic",
            "Environmental Temperature Topic", "Pressure Topic", "Altitude Topic", "Humidity Topic", "Distance Topic",
            "GAS Resistance Topic", "GAS Oxidising Topic",  "GAS Reducing Topic", "GAS NH3 Topic",
            "Particulate Matter 1 Topic", "Particulate Matter 2.5 Topic", "Particulate Matter 4 Topic",
            "Particulate Matter 10 Topic", "Lumen Topic", "Color Red Topic", "Color Orange Topic", "Color Yellow Topic",
            "Color Green Topic", "Color Blue Topic", "Color Violet Topic", "Ultra Violet Index Topic",
            "Ultra Violet A Topic", "Ultra Violet B Topic", "Accelerometer X Topic", "Accelerometer Y Topic",
            "Accelerometer Z Topic", "Magnetometer X Topic", "Magnetometer Y Topic", "Magnetometer Z Topic",
            "Gyroscope X Topic", "Gyroscope Y Topic", "Gyroscope Z Topic", "Custom MQTT Send String", "Dew point",
            "Dew Point Topic", "GPS Latitude", "GPS Latitude Topic", "GPS Longitude", "GPS Longitude Topic"
        ]

        self.enable_mqtt_publisher = 0

        self.mqtt_send_format_kootnet = "KootnetSensors"
        self.mqtt_send_format_individual_topics = "IndividualTopics"
        self.mqtt_send_format_custom_string = "CustomString"
        self.selected_mqtt_send_format = self.mqtt_send_format_kootnet

        self.custom_str_datetime_format = "%Y-%m-%d %H:%M:%S.%f"

        self.broker_address = ""
        self.broker_server_port = 1883
        self.enable_broker_auth = 0
        self.broker_user = ""
        self.broker_password = ""
        self.seconds_to_wait = 60
        self.mqtt_publisher_qos = 0

        self.mqtt_base_topic = app_cached_variables.tmp_sensor_id + "/"

        self.mqtt_custom_data_string = str(self.get_mqtt_replacements_dictionary())

        self.sensor_host_name = 0
        self.sensor_ip = 0
        self.gps_latitude = 0
        self.gps_longitude = 0
        self.sensor_uptime = 0
        self.sensor_date_time = 0
        self.system_temperature = 0
        self.env_temperature = 0
        self.pressure = 0
        self.altitude = 0
        self.humidity = 0
        self.dew_point = 0
        self.distance = 0
        self.gas = 0
        self.gas_resistance_index = 0
        self.gas_oxidising = 0
        self.gas_reducing = 0
        self.gas_nh3 = 0
        self.particulate_matter = 0
        self.particulate_matter_1 = 0
        self.particulate_matter_2_5 = 0
        self.particulate_matter_4 = 0
        self.particulate_matter_10 = 0
        self.lumen = 0
        self.color = 0
        self.color_red = 0
        self.color_orange = 0
        self.color_yellow = 0
        self.color_green = 0
        self.color_blue = 0
        self.color_violet = 0
        self.ultra_violet = 0
        self.ultra_violet_a = 0
        self.ultra_violet_b = 0
        self.accelerometer = 0
        self.accelerometer_x = 0
        self.accelerometer_y = 0
        self.accelerometer_z = 0
        self.magnetometer = 0
        self.magnetometer_x = 0
        self.magnetometer_y = 0
        self.magnetometer_z = 0
        self.gyroscope = 0
        self.gyroscope_x = 0
        self.gyroscope_y = 0
        self.gyroscope_z = 0

        self.sensor_host_name_topic = database_variables.sensor_name
        self.sensor_ip_topic = database_variables.ip
        self.gps_latitude_topic = database_variables.latitude
        self.gps_longitude_topic = database_variables.longitude
        self.sensor_uptime_topic = database_variables.sensor_uptime
        self.sensor_date_time_topic = database_variables.all_tables_datetime
        self.system_temperature_topic = database_variables.system_temperature
        self.env_temperature_topic = database_variables.env_temperature
        self.pressure_topic = database_variables.pressure
        self.altitude_topic = database_variables.altitude
        self.humidity_topic = database_variables.humidity
        self.dew_point_topic = database_variables.dew_point
        self.distance_topic = database_variables.distance
        self.gas_topic = database_variables.gas_all_dic
        self.gas_resistance_index_topic = database_variables.gas_resistance_index
        self.gas_oxidising_topic = database_variables.gas_oxidising
        self.gas_reducing_topic = database_variables.gas_reducing
        self.gas_nh3_topic = database_variables.gas_nh3
        self.particulate_matter_topic = database_variables.particulate_matter_all_dic
        self.particulate_matter_1_topic = database_variables.particulate_matter_1
        self.particulate_matter_2_5_topic = database_variables.particulate_matter_2_5
        self.particulate_matter_4_topic = database_variables.particulate_matter_4
        self.particulate_matter_10_topic = database_variables.particulate_matter_10
        self.lumen_topic = database_variables.lumen
        self.color_topic = database_variables.colour_all_dic
        self.color_red_topic = database_variables.red
        self.color_orange_topic = database_variables.orange
        self.color_yellow_topic = database_variables.yellow
        self.color_green_topic = database_variables.green
        self.color_blue_topic = database_variables.blue
        self.color_violet_topic = database_variables.violet
        self.ultra_violet_topic = database_variables.ultra_violet_all_dic
        self.ultra_violet_index_topic = database_variables.ultra_violet_index
        self.ultra_violet_a_topic = database_variables.ultra_violet_a
        self.ultra_violet_b_topic = database_variables.ultra_violet_b
        self.accelerometer_topic = database_variables.acc_all_dic
        self.accelerometer_x_topic = database_variables.acc_x
        self.accelerometer_y_topic = database_variables.acc_y
        self.accelerometer_z_topic = database_variables.acc_z
        self.magnetometer_topic = database_variables.mag_all_dic
        self.magnetometer_x_topic = database_variables.mag_x
        self.magnetometer_y_topic = database_variables.mag_y
        self.magnetometer_z_topic = database_variables.mag_z
        self.gyroscope_topic = database_variables.gyro_all_dic
        self.gyroscope_x_topic = database_variables.gyro_x
        self.gyroscope_y_topic = database_variables.gyro_y
        self.gyroscope_z_topic = database_variables.gyro_z

        self.update_configuration_settings_list()
        if load_from_file:
            self._init_config_variables()
            self._update_variables_from_settings_list()

    def set_config_with_str(self, config_file_text):
        super().set_config_with_str(config_file_text)
        self._update_variables_from_settings_list()

    def update_with_html_request(self, html_request):
        """ Updates the MQTT Publisher configuration based on provided HTML configuration data. """
        logger.network_logger.debug("Starting HTML MQTT Publisher Configuration Update Check")

        config_type = str(html_request.form.get("ConfigSection"))
        if config_type == "Main":
            self._reset_for_html_main_update()

            if html_request.form.get("enable_mqtt_publisher") is not None:
                self.enable_mqtt_publisher = 1

            if html_request.form.get("publish_broker_address") is not None:
                self.broker_address = html_request.form.get("publish_broker_address")

            if html_request.form.get("publish_broker_port") is not None:
                self.broker_server_port = int(html_request.form.get("publish_broker_port"))

            if html_request.form.get("publish_qos_level") is not None:
                qos_level = html_request.form.get("publish_qos_level")
                self.mqtt_publisher_qos = int(qos_level)

            if html_request.form.get("enable_broker_auth") is not None:
                self.enable_broker_auth = 1
                self.broker_user = str(html_request.form.get("broker_username")).strip()
                if html_request.form.get("enable_broker_auth_pass") is not None:
                    self.broker_password = str(html_request.form.get("broker_password")).strip()
            else:
                self.broker_user = ""
                self.broker_password = ""

            if html_request.form.get("publish_seconds_wait") is not None:
                self.seconds_to_wait = int(html_request.form.get("publish_seconds_wait"))

            if html_request.form.get("system_hostname") is not None:
                self.sensor_host_name = 1
            if html_request.form.get("sensor_uptime") is not None:
                self.sensor_uptime = 1
            if html_request.form.get("sensor_ip") is not None:
                self.sensor_ip = 1
            if html_request.form.get("sensor_gps") is not None:
                self.gps_latitude = 1
                self.gps_longitude = 1
            if html_request.form.get("sensor_datetime") is not None:
                self.sensor_date_time = 1
            if html_request.form.get("cpu_temperature") is not None:
                self.system_temperature = 1
            if html_request.form.get("env_temperature") is not None:
                self.env_temperature = 1
            if html_request.form.get("pressure") is not None:
                self.pressure = 1
            if html_request.form.get("altitude") is not None:
                self.altitude = 1
            if html_request.form.get("humidity") is not None:
                self.humidity = 1
            if html_request.form.get("dew_point") is not None:
                self.dew_point = 1
            if html_request.form.get("distance") is not None:
                self.distance = 1
            if html_request.form.get("gas") is not None:
                self.gas = 1
            if html_request.form.get("particulate_matter") is not None:
                self.particulate_matter = 1
            if html_request.form.get("lumen") is not None:
                self.lumen = 1
            if html_request.form.get("colour") is not None:
                self.color = 1
            if html_request.form.get("ultra_violet") is not None:
                self.ultra_violet = 1
            if html_request.form.get("accelerometer") is not None:
                self.accelerometer = 1
            if html_request.form.get("magnetometer") is not None:
                self.magnetometer = 1
            if html_request.form.get("gyroscope") is not None:
                self.gyroscope = 1
        elif config_type == "Advanced":
            self.selected_mqtt_send_format = str(html_request.form.get("mqtt_send_type"))

            base_topic = str(html_request.form.get("topic_mqtt_base_topic")).strip()
            if base_topic[0] == "/":
                base_topic = base_topic[1:]
            if base_topic[-1] == "/":
                base_topic = base_topic[:-1]
            self.mqtt_base_topic = base_topic + "/"

            mqtt_custom_data_string = html_request.form.get("mqtt_custom_data")
            if mqtt_custom_data_string is not None:
                mqtt_custom_data_string = str(mqtt_custom_data_string).strip()
                self.mqtt_custom_data_string = mqtt_custom_data_string

            if self.selected_mqtt_send_format == self.mqtt_send_format_individual_topics:
                if html_request.form.get("topic_mqtt_system_hostname").strip() != "":
                    self.sensor_host_name_topic = html_request.form.get("topic_mqtt_system_hostname")
                if html_request.form.get("topic_mqtt_system_ip").strip() != "":
                    self.sensor_ip_topic = html_request.form.get("topic_mqtt_system_ip")
                if html_request.form.get("topic_mqtt_gps_lat").strip() != "":
                    self.gps_latitude_topic = html_request.form.get("topic_mqtt_gps_lat")
                if html_request.form.get("topic_mqtt_gps_long").strip() != "":
                    self.gps_longitude_topic = html_request.form.get("topic_mqtt_gps_long")
                if html_request.form.get("topic_mqtt_system_uptime").strip() != "":
                    self.sensor_uptime_topic = html_request.form.get("topic_mqtt_system_uptime")
                if html_request.form.get("topic_mqtt_system_datetime").strip() != "":
                    self.sensor_date_time_topic = html_request.form.get("topic_mqtt_system_datetime")
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
                if html_request.form.get("topic_mqtt_dew_point").strip() != "":
                    self.dew_point_topic = html_request.form.get("topic_mqtt_dew_point")
                if html_request.form.get("topic_mqtt_distance").strip() != "":
                    self.distance_topic = html_request.form.get("topic_mqtt_distance")
                if html_request.form.get("topic_mqtt_gas_resistance_index").strip() != "":
                    self.gas_resistance_index_topic = html_request.form.get("topic_mqtt_gas_resistance_index")
                if html_request.form.get("topic_mqtt_gas_oxidising").strip() != "":
                    self.gas_oxidising_topic = html_request.form.get("topic_mqtt_gas_oxidising")
                if html_request.form.get("topic_mqtt_gas_reducing").strip() != "":
                    self.gas_reducing_topic = html_request.form.get("topic_mqtt_gas_reducing")
                if html_request.form.get("topic_mqtt_gas_nh3").strip() != "":
                    self.gas_nh3_topic = html_request.form.get("topic_mqtt_gas_nh3")
                if html_request.form.get("topic_mqtt_pm_1").strip() != "":
                    self.particulate_matter_1_topic = html_request.form.get("topic_mqtt_pm_1")
                if html_request.form.get("topic_mqtt_pm_2_5").strip() != "":
                    self.particulate_matter_2_5_topic = html_request.form.get("topic_mqtt_pm_2_5")
                if html_request.form.get("topic_mqtt_pm_4").strip() != "":
                    self.particulate_matter_4_topic = html_request.form.get("topic_mqtt_pm_4")
                if html_request.form.get("topic_mqtt_pm_10").strip() != "":
                    self.particulate_matter_10_topic = html_request.form.get("topic_mqtt_pm_10")
                if html_request.form.get("topic_mqtt_lumen").strip() != "":
                    self.lumen_topic = html_request.form.get("topic_mqtt_lumen")
                if html_request.form.get("topic_mqtt_colour_red").strip() != "":
                    self.color_red_topic = html_request.form.get("topic_mqtt_colour_red")
                if html_request.form.get("topic_mqtt_colour_orange").strip() != "":
                    self.color_orange_topic = html_request.form.get("topic_mqtt_colour_orange")
                if html_request.form.get("topic_mqtt_colour_yellow").strip() != "":
                    self.color_yellow_topic = html_request.form.get("topic_mqtt_colour_yellow")
                if html_request.form.get("topic_mqtt_colour_green").strip() != "":
                    self.color_green_topic = html_request.form.get("topic_mqtt_colour_green")
                if html_request.form.get("topic_mqtt_colour_blue").strip() != "":
                    self.color_blue_topic = html_request.form.get("topic_mqtt_colour_blue")
                if html_request.form.get("topic_mqtt_colour_violet").strip() != "":
                    self.color_violet_topic = html_request.form.get("topic_mqtt_colour_violet")
                if html_request.form.get("topic_mqtt_ultra_violet_a").strip() != "":
                    self.ultra_violet_a_topic = html_request.form.get("topic_mqtt_ultra_violet_a")
                if html_request.form.get("topic_mqtt_ultra_violet_b").strip() != "":
                    self.ultra_violet_b_topic = html_request.form.get("topic_mqtt_ultra_violet_b")
                if html_request.form.get("topic_mqtt_accelerometer_x").strip() != "":
                    self.accelerometer_x_topic = html_request.form.get("topic_mqtt_accelerometer_x")
                if html_request.form.get("topic_mqtt_accelerometer_y").strip() != "":
                    self.accelerometer_y_topic = html_request.form.get("topic_mqtt_accelerometer_y")
                if html_request.form.get("topic_mqtt_accelerometer_z").strip() != "":
                    self.accelerometer_z_topic = html_request.form.get("topic_mqtt_accelerometer_z")
                if html_request.form.get("topic_mqtt_magnetometer_x").strip() != "":
                    self.magnetometer_x_topic = html_request.form.get("topic_mqtt_magnetometer_x")
                if html_request.form.get("topic_mqtt_magnetometer_y").strip() != "":
                    self.magnetometer_y_topic = html_request.form.get("topic_mqtt_magnetometer_y")
                if html_request.form.get("topic_mqtt_magnetometer_z").strip() != "":
                    self.magnetometer_z_topic = html_request.form.get("topic_mqtt_magnetometer_z")
                if html_request.form.get("topic_mqtt_gyroscope_x").strip() != "":
                    self.gyroscope_x_topic = html_request.form.get("topic_mqtt_gyroscope_x")
                if html_request.form.get("topic_mqtt_gyroscope_y").strip() != "":
                    self.gyroscope_y_topic = html_request.form.get("topic_mqtt_gyroscope_y")
                if html_request.form.get("topic_mqtt_gyroscope_z").strip() != "":
                    self.gyroscope_z_topic = html_request.form.get("topic_mqtt_gyroscope_z")
        self.update_configuration_settings_list()
        self.load_from_file = True

    def reset_publisher_topics(self):
        self.sensor_host_name_topic = database_variables.sensor_name
        self.sensor_ip_topic = database_variables.ip
        self.sensor_uptime_topic = database_variables.sensor_uptime
        self.sensor_date_time_topic = database_variables.all_tables_datetime
        self.system_temperature_topic = database_variables.system_temperature
        self.env_temperature_topic = database_variables.env_temperature
        self.pressure_topic = database_variables.pressure
        self.altitude_topic = database_variables.altitude
        self.humidity_topic = database_variables.humidity
        self.dew_point_topic = database_variables.dew_point
        self.distance_topic = database_variables.distance
        self.gas_topic = database_variables.gas_all_dic
        self.gas_resistance_index_topic = database_variables.gas_resistance_index
        self.gas_oxidising_topic = database_variables.gas_oxidising
        self.gas_reducing_topic = database_variables.gas_reducing
        self.gas_nh3_topic = database_variables.gas_nh3
        self.particulate_matter_topic = database_variables.particulate_matter_all_dic
        self.particulate_matter_1_topic = database_variables.particulate_matter_1
        self.particulate_matter_2_5_topic = database_variables.particulate_matter_2_5
        self.particulate_matter_4_topic = database_variables.particulate_matter_4
        self.particulate_matter_10_topic = database_variables.particulate_matter_10
        self.lumen_topic = database_variables.lumen
        self.color_topic = database_variables.colour_all_dic
        self.color_red_topic = database_variables.red
        self.color_orange_topic = database_variables.orange
        self.color_yellow_topic = database_variables.yellow
        self.color_green_topic = database_variables.green
        self.color_blue_topic = database_variables.blue
        self.color_violet_topic = database_variables.violet
        self.ultra_violet_topic = database_variables.ultra_violet_all_dic
        self.ultra_violet_index_topic = database_variables.ultra_violet_index
        self.ultra_violet_a_topic = database_variables.ultra_violet_a
        self.ultra_violet_b_topic = database_variables.ultra_violet_b
        self.accelerometer_topic = database_variables.acc_all_dic
        self.accelerometer_x_topic = database_variables.acc_x
        self.accelerometer_y_topic = database_variables.acc_y
        self.accelerometer_z_topic = database_variables.acc_z
        self.magnetometer_topic = database_variables.mag_all_dic
        self.magnetometer_x_topic = database_variables.mag_x
        self.magnetometer_y_topic = database_variables.mag_y
        self.magnetometer_z_topic = database_variables.mag_z
        self.gyroscope_topic = database_variables.gyro_all_dic
        self.gyroscope_x_topic = database_variables.gyro_x
        self.gyroscope_y_topic = database_variables.gyro_y
        self.gyroscope_z_topic = database_variables.gyro_z
        self.gps_latitude_topic = database_variables.latitude
        self.gps_longitude_topic = database_variables.longitude

    def update_configuration_settings_list(self):
        """ Set's config_settings variable list based on current settings. """

        self.config_settings = [
            str(self.enable_mqtt_publisher), str(self.broker_address), str(self.broker_server_port),
            str(self.enable_broker_auth), str(self.broker_user), str(self.broker_password), str(self.seconds_to_wait),
            str(self.mqtt_publisher_qos), str(self.mqtt_base_topic), str(self.selected_mqtt_send_format),
            str(self.custom_str_datetime_format), str(self.sensor_host_name), str(self.sensor_ip),
            str(self.sensor_uptime), str(self.sensor_date_time), str(self.system_temperature),
            str(self.env_temperature), str(self.pressure), str(self.altitude), str(self.humidity), str(self.distance),
            str(self.gas), str(self.particulate_matter), str(self.lumen), str(self.color), str(self.ultra_violet),
            str(self.accelerometer), str(self.magnetometer), str(self.gyroscope), str(self.sensor_host_name_topic),
            str(self.sensor_ip_topic), str(self.sensor_uptime_topic), str(self.sensor_date_time_topic),
            str(self.system_temperature_topic), str(self.env_temperature_topic), str(self.pressure_topic),
            str(self.altitude_topic), str(self.humidity_topic), str(self.distance_topic),
            str(self.gas_resistance_index_topic), str(self.gas_oxidising_topic), str(self.gas_reducing_topic),
            str(self.gas_nh3_topic), str(self.particulate_matter_1_topic), str(self.particulate_matter_2_5_topic),
            str(self.particulate_matter_4_topic), str(self.particulate_matter_10_topic), str(self.lumen_topic),
            str(self.color_red_topic), str(self.color_orange_topic), str(self.color_yellow_topic),
            str(self.color_green_topic), str(self.color_blue_topic), str(self.color_violet_topic),
            str(self.ultra_violet_index_topic), str(self.ultra_violet_a_topic), str(self.ultra_violet_b_topic),
            str(self.accelerometer_x_topic), str(self.accelerometer_y_topic), str(self.accelerometer_z_topic),
            str(self.magnetometer_x_topic), str(self.magnetometer_y_topic), str(self.magnetometer_z_topic),
            str(self.gyroscope_x_topic), str(self.gyroscope_y_topic), str(self.gyroscope_z_topic),
            str(self.mqtt_custom_data_string), str(self.dew_point), str(self.dew_point_topic), str(self.gps_latitude),
            str(self.gps_latitude_topic), str(self.gps_longitude), str(self.gps_longitude_topic)
        ]

    def _update_variables_from_settings_list(self):
        try:
            self.enable_mqtt_publisher = int(self.config_settings[0])
            self.broker_address = self.config_settings[1]
            self.broker_server_port = int(self.config_settings[2])
            self.enable_broker_auth = int(self.config_settings[3])
            self.broker_user = self.config_settings[4]
            self.broker_password = self.config_settings[5]
            self.seconds_to_wait = int(self.config_settings[6])
            self.mqtt_publisher_qos = int(self.config_settings[7].strip())
            self.mqtt_base_topic = self.config_settings[8].strip()
            self.selected_mqtt_send_format = self.config_settings[9].strip()
            self.custom_str_datetime_format = self.config_settings[10].strip()

            self.sensor_host_name = int(self.config_settings[11].strip())
            self.sensor_ip = int(self.config_settings[12].strip())
            self.sensor_uptime = int(self.config_settings[13])
            self.sensor_date_time = int(self.config_settings[14])
            self.system_temperature = int(self.config_settings[15])
            self.env_temperature = int(self.config_settings[16])
            self.pressure = int(self.config_settings[17])
            self.altitude = int(self.config_settings[18])
            self.humidity = int(self.config_settings[19])
            self.distance = int(self.config_settings[20])
            self.gas = int(self.config_settings[21])
            self.particulate_matter = int(self.config_settings[22])
            self.lumen = int(self.config_settings[23])
            self.color = int(self.config_settings[24])
            self.ultra_violet = int(self.config_settings[25])
            self.accelerometer = int(self.config_settings[26])
            self.magnetometer = int(self.config_settings[27])
            self.gyroscope = int(self.config_settings[28])

            self.sensor_host_name_topic = self.config_settings[29].strip()
            self.sensor_ip_topic = self.config_settings[30].strip()
            self.sensor_uptime_topic = self.config_settings[31].strip()
            self.sensor_date_time_topic = self.config_settings[32].strip()
            self.system_temperature_topic = self.config_settings[33].strip()
            self.env_temperature_topic = self.config_settings[34].strip()
            self.pressure_topic = self.config_settings[35].strip()
            self.altitude_topic = self.config_settings[36].strip()
            self.humidity_topic = self.config_settings[37].strip()
            self.distance_topic = self.config_settings[38].strip()
            self.gas_resistance_index_topic = self.config_settings[39].strip()
            self.gas_oxidising_topic = self.config_settings[40].strip()
            self.gas_reducing_topic = self.config_settings[41].strip()
            self.gas_nh3_topic = self.config_settings[42].strip()
            self.particulate_matter_1_topic = self.config_settings[43].strip()
            self.particulate_matter_2_5_topic = self.config_settings[44].strip()
            self.particulate_matter_4_topic = self.config_settings[45].strip()
            self.particulate_matter_10_topic = self.config_settings[46].strip()
            self.lumen_topic = self.config_settings[47].strip()
            self.color_red_topic = self.config_settings[48].strip()
            self.color_orange_topic = self.config_settings[49].strip()
            self.color_yellow_topic = self.config_settings[50].strip()
            self.color_green_topic = self.config_settings[51].strip()
            self.color_blue_topic = self.config_settings[52].strip()
            self.color_violet_topic = self.config_settings[53].strip()
            self.ultra_violet_index_topic = self.config_settings[54].strip()
            self.ultra_violet_a_topic = self.config_settings[55].strip()
            self.ultra_violet_b_topic = self.config_settings[56].strip()
            self.accelerometer_x_topic = self.config_settings[57].strip()
            self.accelerometer_y_topic = self.config_settings[58].strip()
            self.accelerometer_z_topic = self.config_settings[59].strip()
            self.magnetometer_x_topic = self.config_settings[60].strip()
            self.magnetometer_y_topic = self.config_settings[61].strip()
            self.magnetometer_z_topic = self.config_settings[62].strip()
            self.gyroscope_x_topic = self.config_settings[63].strip()
            self.gyroscope_y_topic = self.config_settings[64].strip()
            self.gyroscope_z_topic = self.config_settings[65].strip()

            self.mqtt_custom_data_string = self.config_settings[66].strip()
            self.dew_point = int(self.config_settings[67].strip())
            self.dew_point_topic = self.config_settings[68].strip()

            self.gps_latitude = int(self.config_settings[69].strip())
            self.gps_latitude_topic = self.config_settings[70].strip()
            self.gps_longitude = int(self.config_settings[71].strip())
            self.gps_longitude_topic = self.config_settings[72].strip()

            if self.selected_mqtt_send_format == self.mqtt_send_format_kootnet:
                self.reset_publisher_topics()
        except Exception as error:
            logger.primary_logger.debug("MQTT Publisher Config: " + str(error))
            self.update_configuration_settings_list()
            if self.load_from_file:
                logger.primary_logger.info("Saving MQTT Publisher Configuration.")
                self.save_config_to_file()

    @staticmethod
    def get_mqtt_replacements_dictionary():
        mqtt_pub_replacement_dic = {
            database_variables.sensor_name: "{{ SystemHostName }}",
            database_variables.ip: "{{ SystemIPAddress }}",
            database_variables.latitude: "{{ Latitude }}",
            database_variables.longitude: "{{ Longitude }}",
            database_variables.sensor_uptime: "{{ SystemUpTimeMin }}",
            database_variables.all_tables_datetime: "{{ SystemDateTime }}",
            database_variables.system_temperature: "{{ SystemCPUTemp }}",
            database_variables.env_temperature: "{{ EnvTemp }}",
            database_variables.pressure: "{{ Pressure }}",
            database_variables.altitude: "{{ Altitude }}",
            database_variables.humidity: "{{ Humidity }}",
            database_variables.dew_point: "{{ DewPoint }}",
            database_variables.distance: "{{ Distance }}",
            database_variables.lumen: "{{ Lumen }}",
            database_variables.red: "{{ Red }}",
            database_variables.orange: "{{ Orange }}",
            database_variables.yellow: "{{ Yellow }}",
            database_variables.green: "{{ Green }}",
            database_variables.blue: "{{ Blue }}",
            database_variables.violet: "{{ Violet }}",
            database_variables.ultra_violet_index: "{{ UltraVioletIndex }}",
            database_variables.ultra_violet_a: "{{ UltraVioletA }}",
            database_variables.ultra_violet_b: "{{ UltraVioletB }}",
            database_variables.gas_resistance_index: "{{ GasIndex }}",
            database_variables.gas_oxidising: "{{ GasOxidising }}",
            database_variables.gas_reducing: "{{ GasReducing }}",
            database_variables.gas_nh3: "{{ GasNH3 }}",
            database_variables.particulate_matter_1: "{{ PM1 }}",
            database_variables.particulate_matter_2_5: "{{ PM2.5 }}",
            database_variables.particulate_matter_4: "{{ PM4 }}",
            database_variables.particulate_matter_10: "{{ PM10 }}",
            database_variables.acc_x: "{{ AccX }}",
            database_variables.acc_y: "{{ AccY }}",
            database_variables.acc_z: "{{ AccZ }}",
            database_variables.mag_x: "{{ MagX }}",
            database_variables.mag_y: "{{ MagY }}",
            database_variables.mag_z: "{{ MagZ }}",
            database_variables.gyro_x: "{{ GyroX }}",
            database_variables.gyro_y: "{{ GyroY }}",
            database_variables.gyro_z: "{{ GyroZ }}"
        }
        return mqtt_pub_replacement_dic

    def get_custom_utc0_datetime(self):
        utc_0_date_time_now = datetime.utcnow().strftime(self.custom_str_datetime_format)
        return utc_0_date_time_now

    def _reset_for_html_main_update(self):
        self.enable_mqtt_publisher = 0
        self.enable_broker_auth = 0

        self.sensor_host_name = 0
        self.sensor_ip = 0
        self.sensor_uptime = 0
        self.sensor_date_time = 0
        self.system_temperature = 0
        self.env_temperature = 0
        self.pressure = 0
        self.altitude = 0
        self.humidity = 0
        self.dew_point = 0
        self.distance = 0
        self.gas = 0
        self.gas_resistance_index = 0
        self.gas_oxidising = 0
        self.gas_reducing = 0
        self.gas_nh3 = 0
        self.particulate_matter = 0
        self.particulate_matter_1 = 0
        self.particulate_matter_2_5 = 0
        self.particulate_matter_4 = 0
        self.particulate_matter_10 = 0
        self.lumen = 0
        self.color = 0
        self.color_red = 0
        self.color_orange = 0
        self.color_yellow = 0
        self.color_green = 0
        self.color_blue = 0
        self.color_violet = 0
        self.ultra_violet = 0
        self.ultra_violet_a = 0
        self.ultra_violet_b = 0
        self.accelerometer = 0
        self.accelerometer_x = 0
        self.accelerometer_y = 0
        self.accelerometer_z = 0
        self.magnetometer = 0
        self.magnetometer_x = 0
        self.magnetometer_y = 0
        self.magnetometer_z = 0
        self.gyroscope = 0
        self.gyroscope_x = 0
        self.gyroscope_y = 0
        self.gyroscope_z = 0
        self.gps_latitude = 0
        self.gps_longitude = 0
