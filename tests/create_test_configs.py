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
from configuration_modules.config_primary import CreatePrimaryConfiguration
from configuration_modules.config_installed_sensors import CreateInstalledSensorsConfiguration
from configuration_modules.config_display import CreateDisplayConfiguration
from configuration_modules.config_interval_recording import CreateIntervalRecordingConfiguration
from configuration_modules.config_trigger_high_low import CreateTriggerHighLowConfiguration
from configuration_modules.config_trigger_variances import CreateTriggerVariancesConfiguration
from configuration_modules.config_email import CreateEmailConfiguration
from configuration_modules.config_mqtt_publisher import CreateMQTTPublisherConfiguration
from configuration_modules.config_mqtt_subscriber import CreateMQTTSubscriberConfiguration
from configuration_modules.config_weather_underground import CreateWeatherUndergroundConfiguration
from configuration_modules.config_luftdaten import CreateLuftdatenConfiguration
from configuration_modules.config_open_sense_map import CreateOpenSenseMapConfiguration


class CreatePrimaryConfigurationTest(CreatePrimaryConfiguration):
    def __init__(self):
        CreatePrimaryConfiguration.__init__(self, load_from_file=False)

    def set_settings_for_test1(self):
        self.enable_debug_logging = 0
        self.utc0_hour_offset = -4.0
        self.web_portal_port = 10065
        self.update_configuration_settings_list()

    def set_settings_for_test2(self):
        self.enable_debug_logging = 1
        self.utc0_hour_offset = 22.0
        self.web_portal_port = 10064
        self.update_configuration_settings_list()


class CreateInstalledSensorsConfigurationTest(CreateInstalledSensorsConfiguration):
    def __init__(self):
        CreateInstalledSensorsConfiguration.__init__(self, load_from_file=False)

    def set_settings_for_test1(self):
        self.kootnet_dummy_sensor = 0
        self.linux_system = 0
        self.raspberry_pi = 0
        self.raspberry_pi_sense_hat = 0
        self.pimoroni_bh1745 = 0
        self.pimoroni_as7262 = 0
        self.pimoroni_mcp9600 = 0
        self.pimoroni_bmp280 = 0
        self.pimoroni_bme280 = 0
        self.pimoroni_bme680 = 0
        self.pimoroni_enviro = 0
        self.pimoroni_enviro2 = 0
        self.pimoroni_enviroplus = 0
        self.pimoroni_sgp30 = 0
        self.pimoroni_pms5003 = 0
        self.pimoroni_msa301 = 0
        self.pimoroni_lsm303d = 0
        self.pimoroni_icm20948 = 0
        self.pimoroni_vl53l1x = 0
        self.pimoroni_ltr_559 = 0
        self.pimoroni_veml6075 = 0
        self.pimoroni_mics6814 = 0
        self.pimoroni_matrix_11x7 = 0
        self.pimoroni_st7735 = 0
        self.pimoroni_mono_oled_luma = 0
        self.pimoroni_rv3028 = 0
        self.pimoroni_pa1010d = 0
        self.sensirion_sps30 = 0
        self.w1_therm_sensor = 0
        self.update_configuration_settings_list()

    def set_settings_for_test2(self):
        self.kootnet_dummy_sensor = 1
        self.linux_system = 1
        self.raspberry_pi = 1
        self.raspberry_pi_sense_hat = 1
        self.pimoroni_bh1745 = 1
        self.pimoroni_as7262 = 1
        self.pimoroni_mcp9600 = 1
        self.pimoroni_bmp280 = 1
        self.pimoroni_bme280 = 1
        self.pimoroni_bme680 = 1
        self.pimoroni_enviro = 1
        self.pimoroni_enviro2 = 1
        self.pimoroni_enviroplus = 1
        self.pimoroni_sgp30 = 1
        self.pimoroni_pms5003 = 1
        self.pimoroni_msa301 = 1
        self.pimoroni_lsm303d = 1
        self.pimoroni_icm20948 = 1
        self.pimoroni_vl53l1x = 1
        self.pimoroni_ltr_559 = 1
        self.pimoroni_veml6075 = 1
        self.pimoroni_mics6814 = 1
        self.pimoroni_matrix_11x7 = 1
        self.pimoroni_st7735 = 1
        self.pimoroni_mono_oled_luma = 1
        self.pimoroni_rv3028 = 1
        self.pimoroni_pa1010d = 1
        self.sensirion_sps30 = 1
        self.w1_therm_sensor = 1
        self.update_configuration_settings_list()


class CreateDisplayConfigurationTest(CreateDisplayConfiguration):
    def __init__(self):
        CreateDisplayConfiguration.__init__(self, load_from_file=False)

    def set_settings_for_test1(self):
        self.enable_display = 0
        self.minutes_between_display = 6
        self.display_type = "Test1"
        self.sensor_uptime = 0
        self.system_temperature = 0
        self.env_temperature = 0
        self.pressure = 0
        self.altitude = 0
        self.humidity = 0
        self.dew_point = 0
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

    def set_settings_for_test2(self):
        self.enable_display = 2
        self.minutes_between_display = 2
        self.display_type = "Test2"
        self.sensor_uptime = 2
        self.system_temperature = 2
        self.env_temperature = 2
        self.pressure = 2
        self.altitude = 2
        self.humidity = 2
        self.dew_point = 2
        self.distance = 2
        self.gas = 2
        self.particulate_matter = 2
        self.lumen = 2
        self.color = 2
        self.ultra_violet = 2
        self.accelerometer = 2
        self.magnetometer = 2
        self.gyroscope = 2
        self.update_configuration_settings_list()


class CreateIntervalRecordingConfigurationTest(CreateIntervalRecordingConfiguration):
    def __init__(self):
        CreateIntervalRecordingConfiguration.__init__(self, load_from_file=False)

    def set_settings_for_test1(self):
        self.enable_interval_recording = 0
        self.sleep_duration_interval = 444.0
        self.enable_interval_recording = 1
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
        self.gps_enabled = 0
        self.update_configuration_settings_list()

    def set_settings_for_test2(self):
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
        self.gps_enabled = 1
        self.update_configuration_settings_list()


class CreateTriggerHighLowConfigurationTest(CreateTriggerHighLowConfiguration):
    def __init__(self):
        CreateTriggerHighLowConfiguration.__init__(self, load_from_file=False)

    def set_settings_for_test1(self):
        self.enable_high_low_trigger_recording = 0
        self.cpu_temperature_enabled = 0
        self.env_temperature_enabled = 0
        self.pressure_enabled = 0
        self.humidity_enabled = 0
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

        self.cpu_temperature_low = 6.0
        self.cpu_temperature_high = 999.0
        self.cpu_temperature_wait_seconds = 33.0
        self.env_temperature_low = 6.0
        self.env_temperature_high = 999.0
        self.env_temperature_wait_seconds = 33.0
        self.pressure_low = 6
        self.pressure_high = 999
        self.pressure_wait_seconds = 33.0
        self.humidity_low = 6.0
        self.humidity_high = 999.0
        self.humidity_wait_seconds = 33.0
        self.altitude_low = 6
        self.altitude_high = 999
        self.altitude_wait_seconds = 33.0
        self.distance_low = 6.0
        self.distance_high = 999.0
        self.distance_wait_seconds = 33
        self.lumen_low = 6.0
        self.lumen_high = 999.0
        self.lumen_wait_seconds = 33
        self.red_low = 6.0
        self.red_high = 999.0
        self.orange_low = 6.0
        self.orange_high = 999.0
        self.yellow_low = 6.0
        self.yellow_high = 999.0
        self.green_low = 6.0
        self.green_high = 999.0
        self.blue_low = 6.0
        self.blue_high = 999.0
        self.violet_low = 6.0
        self.violet_high = 999.0
        self.colour_wait_seconds = 33.0
        self.ultra_violet_index_low = 6.0
        self.ultra_violet_index_high = 999.0
        self.ultra_violet_a_low = 6.0
        self.ultra_violet_a_high = 999.0
        self.ultra_violet_b_low = 6.0
        self.ultra_violet_b_high = 999.0
        self.ultra_violet_wait_seconds = 33.0
        self.gas_resistance_index_low = 6.0
        self.gas_resistance_index_high = 999.0
        self.gas_oxidising_low = 6.0
        self.gas_oxidising_high = 999.0
        self.gas_reducing_low = 6.0
        self.gas_reducing_high = 999.0
        self.gas_nh3_low = 6.0
        self.gas_nh3_high = 999.0
        self.gas_wait_seconds = 33.0
        self.particulate_matter_1_low = 6.0
        self.particulate_matter_1_high = 999.0
        self.particulate_matter_2_5_low = 6.0
        self.particulate_matter_2_5_high = 999.0
        self.particulate_matter_4_low = 6.0
        self.particulate_matter_4_high = 999.0
        self.particulate_matter_10_low = 6.0
        self.particulate_matter_10_high = 999.0
        self.particulate_matter_wait_seconds = 33.0
        self.accelerometer_x_low = 0.6
        self.accelerometer_x_high = 0.999
        self.accelerometer_y_low = 0.6
        self.accelerometer_y_high = 0.999
        self.accelerometer_z_low = 0.6
        self.accelerometer_z_high = 0.999
        self.accelerometer_wait_seconds = 33
        self.magnetometer_x_low = 6.0
        self.magnetometer_x_high = 999.0
        self.magnetometer_y_low = 6.0
        self.magnetometer_y_high = 999.0
        self.magnetometer_z_low = 6.0
        self.magnetometer_z_high = 999.0
        self.magnetometer_wait_seconds = 33
        self.gyroscope_x_low = 6.0
        self.gyroscope_x_high = 999.0
        self.gyroscope_y_low = 6.0
        self.gyroscope_y_high = 999.0
        self.gyroscope_z_low = 6.0
        self.gyroscope_z_high = 999.0
        self.gyroscope_wait_seconds = 33
        self.update_configuration_settings_list()

    def set_settings_for_test2(self):
        self.enable_high_low_trigger_recording = 1
        self.cpu_temperature_enabled = 1
        self.env_temperature_enabled = 1
        self.pressure_enabled = 1
        self.humidity_enabled = 1
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

        self.cpu_temperature_low = 99.0
        self.cpu_temperature_high = 8888.0
        self.cpu_temperature_wait_seconds = 41.0
        self.env_temperature_low = 99.0
        self.env_temperature_high = 8888.0
        self.env_temperature_wait_seconds = 41.0
        self.pressure_low = 99
        self.pressure_high = 8888
        self.pressure_wait_seconds = 41.0
        self.humidity_low = 99.0
        self.humidity_high = 8888.0
        self.humidity_wait_seconds = 41.0
        self.altitude_low = 99
        self.altitude_high = 8888
        self.altitude_wait_seconds = 41.0
        self.distance_low = 99.0
        self.distance_high = 8888.0
        self.distance_wait_seconds = 41
        self.lumen_low = 99.0
        self.lumen_high = 8888.0
        self.lumen_wait_seconds = 41
        self.red_low = 99.0
        self.red_high = 8888.0
        self.orange_low = 99.0
        self.orange_high = 8888.0
        self.yellow_low = 99.0
        self.yellow_high = 8888.0
        self.green_low = 99.0
        self.green_high = 8888.0
        self.blue_low = 99.0
        self.blue_high = 8888.0
        self.violet_low = 99.0
        self.violet_high = 8888.0
        self.colour_wait_seconds = 41.0
        self.ultra_violet_index_low = 99.0
        self.ultra_violet_index_high = 8888.0
        self.ultra_violet_a_low = 99.0
        self.ultra_violet_a_high = 8888.0
        self.ultra_violet_b_low = 99.0
        self.ultra_violet_b_high = 8888.0
        self.ultra_violet_wait_seconds = 41.0
        self.gas_resistance_index_low = 99.0
        self.gas_resistance_index_high = 8888.0
        self.gas_oxidising_low = 99.0
        self.gas_oxidising_high = 8888.0
        self.gas_reducing_low = 99.0
        self.gas_reducing_high = 8888.0
        self.gas_nh3_low = 99.0
        self.gas_nh3_high = 8888.0
        self.gas_wait_seconds = 41.0
        self.particulate_matter_1_low = 99.0
        self.particulate_matter_1_high = 8888.0
        self.particulate_matter_2_5_low = 99.0
        self.particulate_matter_2_5_high = 8888.0
        self.particulate_matter_4_low = 99.0
        self.particulate_matter_4_high = 8888.0
        self.particulate_matter_10_low = 99.0
        self.particulate_matter_10_high = 8888.0
        self.particulate_matter_wait_seconds = 41.0
        self.accelerometer_x_low = 0.99
        self.accelerometer_x_high = 8888
        self.accelerometer_y_low = 0.99
        self.accelerometer_y_high = 8888
        self.accelerometer_z_low = 0.99
        self.accelerometer_z_high = 8888
        self.accelerometer_wait_seconds = 41
        self.magnetometer_x_low = 99.0
        self.magnetometer_x_high = 8888.0
        self.magnetometer_y_low = 99.0
        self.magnetometer_y_high = 8888.0
        self.magnetometer_z_low = 99.0
        self.magnetometer_z_high = 8888.0
        self.magnetometer_wait_seconds = 41
        self.gyroscope_x_low = 99.0
        self.gyroscope_x_high = 8888.0
        self.gyroscope_y_low = 99.0
        self.gyroscope_y_high = 8888.0
        self.gyroscope_z_low = 99.0
        self.gyroscope_z_high = 8888.0
        self.gyroscope_wait_seconds = 41
        self.update_configuration_settings_list()


class CreateTriggerVariancesConfigurationTest(CreateTriggerVariancesConfiguration):
    def __init__(self):
        CreateTriggerVariancesConfiguration.__init__(self, load_from_file=False)

    def set_settings_for_test1(self):
        self.enable_trigger_variance = 0
        self.cpu_temperature_enabled = 0
        self.cpu_temperature_variance = 65.72
        self.cpu_temperature_wait_seconds = 65.72
        self.env_temperature_enabled = 0
        self.env_temperature_variance = 65.72
        self.env_temperature_wait_seconds = 65.72
        self.pressure_enabled = 0
        self.pressure_variance = 65.72
        self.pressure_wait_seconds = 65.72
        self.humidity_enabled = 0
        self.humidity_variance = 65.72
        self.humidity_wait_seconds = 65.72
        self.altitude_enabled = 0
        self.altitude_variance = 65.72
        self.altitude_wait_seconds = 65.72
        self.distance_enabled = 0
        self.distance_variance = 65.72
        self.distance_wait_seconds = 65.72
        self.lumen_enabled = 0
        self.lumen_variance = 65.72
        self.lumen_wait_seconds = 65.72
        self.colour_enabled = 0
        self.red_variance = 65.72
        self.orange_variance = 65.72
        self.yellow_variance = 65.72
        self.green_variance = 65.72
        self.blue_variance = 65.72
        self.violet_variance = 65.72
        self.colour_wait_seconds = 65.72
        self.ultra_violet_enabled = 0
        self.ultra_violet_index_variance = 65.72
        self.ultra_violet_a_variance = 65.72
        self.ultra_violet_b_variance = 65.72
        self.ultra_violet_wait_seconds = 65.72
        self.gas_enabled = 0
        self.gas_resistance_index_variance = 65.72
        self.gas_oxidising_variance = 65.72
        self.gas_reducing_variance = 65.72
        self.gas_nh3_variance = 65.72
        self.gas_wait_seconds = 65.72
        self.particulate_matter_enabled = 0
        self.particulate_matter_1_variance = 65.72
        self.particulate_matter_2_5_variance = 65.72
        self.particulate_matter_10_variance = 65.72
        self.particulate_matter_wait_seconds = 65.72
        self.accelerometer_enabled = 0
        self.accelerometer_x_variance = 65.72
        self.accelerometer_y_variance = 65.72
        self.accelerometer_z_variance = 65.72
        self.accelerometer_wait_seconds = 65.72
        self.magnetometer_enabled = 0
        self.magnetometer_x_variance = 65.72
        self.magnetometer_y_variance = 65.72
        self.magnetometer_z_variance = 65.72
        self.magnetometer_wait_seconds = 65.72
        self.gyroscope_enabled = 0
        self.gyroscope_x_variance = 65.72
        self.gyroscope_y_variance = 65.72
        self.gyroscope_z_variance = 65.72
        self.gyroscope_wait_seconds = 65.72
        self.update_configuration_settings_list()

    def set_settings_for_test2(self):
        self.enable_trigger_variance = 0
        self.cpu_temperature_enabled = 1
        self.cpu_temperature_variance = 84.16
        self.cpu_temperature_wait_seconds = 84.16
        self.env_temperature_enabled = 1
        self.env_temperature_variance = 84.16
        self.env_temperature_wait_seconds = 84.16
        self.pressure_enabled = 1
        self.pressure_variance = 84.16
        self.pressure_wait_seconds = 84.16
        self.humidity_enabled = 1
        self.humidity_variance = 84.16
        self.humidity_wait_seconds = 84.16
        self.altitude_enabled = 1
        self.altitude_variance = 84.16
        self.altitude_wait_seconds = 84.16
        self.distance_enabled = 1
        self.distance_variance = 84.16
        self.distance_wait_seconds = 84.16
        self.lumen_enabled = 1
        self.lumen_variance = 84.16
        self.lumen_wait_seconds = 84.16
        self.colour_enabled = 1
        self.red_variance = 84.16
        self.orange_variance = 84.16
        self.yellow_variance = 84.16
        self.green_variance = 84.16
        self.blue_variance = 84.16
        self.violet_variance = 84.16
        self.colour_wait_seconds = 84.16
        self.ultra_violet_enabled = 1
        self.ultra_violet_index_variance = 84.16
        self.ultra_violet_a_variance = 84.16
        self.ultra_violet_b_variance = 84.16
        self.ultra_violet_wait_seconds = 84.16
        self.gas_enabled = 1
        self.gas_resistance_index_variance = 84.16
        self.gas_oxidising_variance = 84.16
        self.gas_reducing_variance = 84.16
        self.gas_nh3_variance = 84.16
        self.gas_wait_seconds = 84.16
        self.particulate_matter_enabled = 1
        self.particulate_matter_1_variance = 84.16
        self.particulate_matter_2_5_variance = 84.16
        self.particulate_matter_10_variance = 84.16
        self.particulate_matter_wait_seconds = 84.16
        self.accelerometer_enabled = 1
        self.accelerometer_x_variance = 84.16
        self.accelerometer_y_variance = 84.16
        self.accelerometer_z_variance = 84.16
        self.accelerometer_wait_seconds = 84.16
        self.magnetometer_enabled = 1
        self.magnetometer_x_variance = 84.16
        self.magnetometer_y_variance = 84.16
        self.magnetometer_z_variance = 84.16
        self.magnetometer_wait_seconds = 84.16
        self.gyroscope_enabled = 1
        self.gyroscope_x_variance = 84.16
        self.gyroscope_y_variance = 84.16
        self.gyroscope_z_variance = 84.16
        self.gyroscope_wait_seconds = 84.16
        self.update_configuration_settings_list()


class CreateEmailConfigurationTest(CreateEmailConfiguration):
    def __init__(self):
        CreateEmailConfiguration.__init__(self, load_from_file=False)

    def set_settings_for_test1(self):
        self.server_sending_email = "test@test.com"
        self.server_smtp_address = "somemailserver.overthere.com"
        self.server_smtp_ssl_enabled = 1
        self.server_smtp_tls_enabled = 1
        self.server_smtp_port = 587
        self.server_smtp_user = "test_user"
        self.server_smtp_password = "test_pass"
        self.enable_combo_report_emails = 0
        self.send_report_every = self.send_option_monthly
        self.email_reports_time_of_day = "11:05"
        self.send_report_to_csv_emails = "test@test.com"
        self.enable_graph_emails = 0
        self.send_graph_every = self.send_option_monthly
        self.email_graph_time_of_day = "03:28"
        self.graph_past_hours = 11
        self.graph_type = 0  # 0 = Quick Graph / 1+ = Plotly Graph
        self.send_graphs_to_csv_emails = "test@test.com"
        # Enable or Disable Sensors to Graph.  0 = Disabled, 1 = Enabled
        self.sensor_uptime = 1
        self.system_temperature = 1
        self.env_temperature = 1
        self.pressure = 1
        self.altitude = 1
        self.humidity = 1
        self.distance = 1
        self.gas = 1
        self.particulate_matter = 1
        self.lumen = 1
        self.color = 1
        self.ultra_violet = 1
        self.accelerometer = 1
        self.magnetometer = 1
        self.gyroscope = 1
        self.update_configuration_settings_list()

    def set_settings_for_test2(self):
        self.server_sending_email = "test44@test.com"
        self.server_smtp_address = "somemailserver44.overthere.com"
        self.server_smtp_ssl_enabled = 0
        self.server_smtp_tls_enabled = 0
        self.server_smtp_port = 465
        self.server_smtp_user = "test_user2"
        self.server_smtp_password = "test_pass2"
        self.enable_combo_report_emails = 0
        self.send_report_every = self.send_option_yearly
        self.email_reports_time_of_day = "08:55"
        self.send_report_to_csv_emails = "test@test.com"
        self.enable_graph_emails = 0
        self.send_graph_every = self.send_option_weekly
        self.email_graph_time_of_day = "04:35"
        self.graph_past_hours = 22
        self.graph_type = 0  # 0 = Quick Graph / 1+ = Plotly Graph
        self.send_graphs_to_csv_emails = "test2@test.com"
        # Enable or Disable Sensors to Graph.  0 = Disabled, 1 = Enabled
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
        self.update_configuration_settings_list()


class CreateMQTTPublisherConfigurationTest(CreateMQTTPublisherConfiguration):
    def __init__(self):
        CreateMQTTPublisherConfiguration.__init__(self, load_from_file=False)

    def set_settings_for_test1(self):
        self.enable_mqtt_publisher = 0
        self.broker_address = "testing.testers.com"
        self.broker_server_port = 1883
        self.enable_broker_auth = 1
        self.broker_user = "test_user"
        self.broker_password = "test_pass"
        self.seconds_to_wait = 76
        self.mqtt_publisher_qos = 1
        self.sensor_host_name = 1
        self.sensor_ip = 1
        self.gps_latitude = 1
        self.gps_longitude = 1
        self.sensor_uptime = 1
        self.system_temperature = 1
        self.env_temperature = 1
        self.pressure = 1
        self.altitude = 1
        self.humidity = 1
        self.distance = 1
        self.gas = 1
        self.particulate_matter = 1
        self.lumen = 1
        self.color = 1
        self.ultra_violet = 1
        self.accelerometer = 1
        self.magnetometer = 1
        self.gyroscope = 1
        self.mqtt_base_topic = "KSD44444Fg/"
        self.mqtt_custom_data_string = "ChangeMe"
        self.sensor_host_name_topic = "ChangeMe"
        self.gps_latitude_topic = "ChangeMe"
        self.gps_longitude_topic = "ChangeMe"
        self.sensor_ip_topic = "ChangeMe"
        self.sensor_uptime_topic = "ChangeMe"
        self.sensor_date_time_topic = "ChangeMe"
        self.system_temperature_topic = "ChangeMe"
        self.env_temperature_topic = "ChangeMe"
        self.pressure_topic = "ChangeMe"
        self.altitude_topic = "ChangeMe"
        self.humidity_topic = "ChangeMe"
        self.distance_topic = "ChangeMe"
        self.gas_topic = "ChangeMe"
        self.gas_resistance_index_topic = "ChangeMe"
        self.gas_oxidising_topic = "ChangeMe"
        self.gas_reducing_topic = "ChangeMe"
        self.gas_nh3_topic = "ChangeMe"
        self.particulate_matter_topic = "ChangeMe"
        self.particulate_matter_1_topic = "ChangeMe"
        self.particulate_matter_2_5_topic = "ChangeMe"
        self.particulate_matter_4_topic = "ChangeMe"
        self.particulate_matter_10_topic = "ChangeMe"
        self.lumen_topic = "ChangeMe"
        self.color_topic = "ChangeMe"
        self.color_red_topic = "ChangeMe"
        self.color_orange_topic = "ChangeMe"
        self.color_yellow_topic = "ChangeMe"
        self.color_green_topic = "ChangeMe"
        self.color_blue_topic = "ChangeMe"
        self.color_violet_topic = "ChangeMe"
        self.ultra_violet_topic = "ChangeMe"
        self.ultra_violet_index_topic = "ChangeMe"
        self.ultra_violet_a_topic = "ChangeMe"
        self.ultra_violet_b_topic = "ChangeMe"
        self.accelerometer_topic = "ChangeMe"
        self.accelerometer_x_topic = "ChangeMe"
        self.accelerometer_y_topic = "ChangeMe"
        self.accelerometer_z_topic = "ChangeMe"
        self.magnetometer_topic = "ChangeMe"
        self.magnetometer_x_topic = "ChangeMe"
        self.magnetometer_y_topic = "ChangeMe"
        self.magnetometer_z_topic = "ChangeMe"
        self.gyroscope_topic = "ChangeMe"
        self.gyroscope_x_topic = "ChangeMe"
        self.gyroscope_y_topic = "ChangeMe"
        self.gyroscope_z_topic = "ChangeMe"
        self.update_configuration_settings_list()

    def set_settings_for_test2(self):
        self.enable_mqtt_publisher = 0
        self.broker_address = "testing2.testers.com"
        self.broker_server_port = 54443
        self.enable_broker_auth = 0
        self.broker_user = "test_user2"
        self.broker_password = "test_pass2"
        self.seconds_to_wait = 44
        self.mqtt_publisher_qos = 2
        self.sensor_host_name = 0
        self.sensor_ip = 0
        self.gps_latitude = 0
        self.gps_longitude = 0
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
        self.mqtt_base_topic = "KSD43d47sSd4Fg/"
        self.mqtt_custom_data_string = "ChangeMe1"
        self.sensor_host_name_topic = "ChangeMe1"
        self.gps_latitude_topic = "ChangeMe1"
        self.gps_longitude_topic = "ChangeMe1"
        self.sensor_ip_topic = "ChangeMe1"
        self.sensor_uptime_topic = "ChangeMe1"
        self.sensor_date_time_topic = "ChangeMe1"
        self.system_temperature_topic = "ChangeMe1"
        self.env_temperature_topic = "ChangeMe1"
        self.pressure_topic = "ChangeMe1"
        self.altitude_topic = "ChangeMe1"
        self.humidity_topic = "ChangeMe1"
        self.distance_topic = "ChangeMe1"
        self.gas_topic = "ChangeMe1"
        self.gas_resistance_index_topic = "ChangeMe1"
        self.gas_oxidising_topic = "ChangeMe1"
        self.gas_reducing_topic = "ChangeMe1"
        self.gas_nh3_topic = "ChangeMe1"
        self.particulate_matter_topic = "ChangeMe1"
        self.particulate_matter_1_topic = "ChangeMe1"
        self.particulate_matter_2_5_topic = "ChangeMe1"
        self.particulate_matter_4_topic = "ChangeMe1"
        self.particulate_matter_10_topic = "ChangeMe1"
        self.lumen_topic = "ChangeMe1"
        self.color_topic = "ChangeMe1"
        self.color_red_topic = "ChangeMe1"
        self.color_orange_topic = "ChangeMe1"
        self.color_yellow_topic = "ChangeMe1"
        self.color_green_topic = "ChangeMe1"
        self.color_blue_topic = "ChangeMe1"
        self.color_violet_topic = "ChangeMe1"
        self.ultra_violet_topic = "ChangeMe1"
        self.ultra_violet_index_topic = "ChangeMe1"
        self.ultra_violet_a_topic = "ChangeMe1"
        self.ultra_violet_b_topic = "ChangeMe1"
        self.accelerometer_topic = "ChangeMe1"
        self.accelerometer_x_topic = "ChangeMe1"
        self.accelerometer_y_topic = "ChangeMe1"
        self.accelerometer_z_topic = "ChangeMe1"
        self.magnetometer_topic = "ChangeMe1"
        self.magnetometer_x_topic = "ChangeMe1"
        self.magnetometer_y_topic = "ChangeMe1"
        self.magnetometer_z_topic = "ChangeMe1"
        self.gyroscope_topic = "ChangeMe1"
        self.gyroscope_x_topic = "ChangeMe1"
        self.gyroscope_y_topic = "ChangeMe1"
        self.gyroscope_z_topic = "ChangeMe1"
        self.update_configuration_settings_list()


class CreateMQTTSubscriberConfigurationTest(CreateMQTTSubscriberConfiguration):
    def __init__(self):
        CreateMQTTSubscriberConfiguration.__init__(self, load_from_file=False)

    def set_settings_for_test1(self):
        self.enable_mqtt_subscriber = 1
        self.enable_mqtt_sql_recording = 1
        self.broker_address = "nowhere.com"
        self.broker_server_port = 1883
        self.enable_broker_auth = 1
        self.broker_user = "test"
        self.broker_password = "test"
        self.subscribed_topics_list = ["testing/#"]
        self.mqtt_subscriber_qos = 1
        self.update_configuration_settings_list()

    def set_settings_for_test2(self):
        self.enable_mqtt_subscriber = 0
        self.enable_mqtt_sql_recording = 0
        self.broker_address = "somewhere.com"
        self.broker_server_port = 1664
        self.enable_broker_auth = 0
        self.broker_user = "maybe"
        self.broker_password = "not"
        self.subscribed_topics_list = ["jack/#"]
        self.mqtt_subscriber_qos = 2
        self.update_configuration_settings_list()


class CreateWeatherUndergroundConfigurationTest(CreateWeatherUndergroundConfiguration):
    def __init__(self):
        CreateWeatherUndergroundConfiguration.__init__(self, load_from_file=False)

    def set_settings_for_test1(self):
        self.weather_underground_enabled = 0
        self.interval_seconds = 999.9
        self.outdoor_sensor = 0
        self.station_id = "Test_1"
        self.station_key = "Test_2"
        self.update_configuration_settings_list()

    def set_settings_for_test2(self):
        self.weather_underground_enabled = 0
        self.interval_seconds = 78855.321
        self.outdoor_sensor = 1
        self.station_id = "Test_3"
        self.station_key = "Test_5"
        self.update_configuration_settings_list()


class CreateLuftdatenConfigurationTest(CreateLuftdatenConfiguration):
    def __init__(self):
        CreateLuftdatenConfiguration.__init__(self, load_from_file=False)

    def set_settings_for_test1(self):
        self.luftdaten_enabled = 0
        self.interval_seconds = 9663.09
        self.update_configuration_settings_list()

    def set_settings_for_test2(self):
        self.luftdaten_enabled = 0
        self.interval_seconds = 55712.21
        self.update_configuration_settings_list()


class CreateOpenSenseMapConfigurationTest(CreateOpenSenseMapConfiguration):
    def __init__(self):
        CreateOpenSenseMapConfiguration.__init__(self, load_from_file=False)

    def set_settings_for_test1(self):
        self.open_sense_map_enabled = 0
        self.sense_box_id = "11111"
        self.interval_seconds = 911100.11
        self.temperature_id = "123333"
        self.pressure_id = "123333"
        self.altitude_id = "123333"
        self.humidity_id = "123333"
        self.gas_voc_id = "123333"
        self.gas_oxidised_id = "123333"
        self.gas_reduced_id = "123333"
        self.gas_nh3_id = "123333"
        self.pm1_id = "123333"
        self.pm2_5_id = "123333"
        self.pm4_id = "123333"
        self.pm10_id = "123333"
        self.lumen_id = "123333"
        self.red_id = "123333"
        self.orange_id = "123333"
        self.yellow_id = "123333"
        self.green_id = "123333"
        self.blue_id = "123333"
        self.violet_id = "123333"
        self.ultra_violet_index_id = "123333"
        self.ultra_violet_a_id = "123333"
        self.ultra_violet_b_id = "123333"
        self.update_configuration_settings_list()

    def set_settings_for_test2(self):
        self.open_sense_map_enabled = 0
        self.sense_box_id = "33322158"
        self.interval_seconds = 12.9
        self.temperature_id = "698742"
        self.pressure_id = "698742"
        self.altitude_id = "698742"
        self.humidity_id = "698742"
        self.gas_voc_id = "698742"
        self.gas_oxidised_id = "698742"
        self.gas_reduced_id = "698742"
        self.gas_nh3_id = "698742"
        self.pm1_id = "698742"
        self.pm2_5_id = "698742"
        self.pm4_id = "698742"
        self.pm10_id = "698742"
        self.lumen_id = "698742"
        self.red_id = "698742"
        self.orange_id = "698742"
        self.yellow_id = "698742"
        self.green_id = "698742"
        self.blue_id = "698742"
        self.violet_id = "698742"
        self.ultra_violet_index_id = "698742"
        self.ultra_violet_a_id = "698742"
        self.ultra_violet_b_id = "698742"
        self.update_configuration_settings_list()
