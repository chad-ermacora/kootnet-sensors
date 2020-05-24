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
import unittest
from time import sleep
from operations_modules.app_generic_functions import get_http_sensor_reading, http_display_text_on_sensor, \
    send_http_command
from operations_modules.app_cached_variables import no_sensor_present, command_data_separator, \
    CreateNetworkGetCommands, CreateNetworkSetCommands
from configuration_modules.config_primary import CreatePrimaryConfiguration
from configuration_modules.config_installed_sensors import CreateInstalledSensorsConfiguration
from configuration_modules.config_trigger_variances import CreateTriggerVariancesConfiguration
from configuration_modules.config_sensor_control import CreateSensorControlConfiguration
from configuration_modules.config_weather_underground import CreateWeatherUndergroundConfiguration
from configuration_modules.config_luftdaten import CreateLuftdatenConfiguration
from configuration_modules.config_open_sense_map import CreateOpenSenseMapConfiguration

# TODO: Add missing Configurations


class CreatePrimaryConfigurationTest(CreatePrimaryConfiguration):
    def __init__(self):
        CreatePrimaryConfiguration.__init__(self, load_from_file=False)
        self.static_config_test = """Enable = 1 & Disable = 0
0 = Enable Debug Logging
1 = Interval Recording to SQL Database
1 = Trigger Recording to SQL Database
227.27 = Recording Interval in Seconds ** Caution **
1 = Enable Custom Temperature Offset
-11.23 = Current Temperature Offset
10165 = HTTPS Port Number (Default is 10065)"""

    def set_settings_for_test1(self):
        self.web_portal_port = 11445
        self.enable_debug_logging = 1
        self.enable_interval_recording = 1
        self.enable_trigger_recording = 1
        self.sleep_duration_interval = 245.11
        self.enable_custom_temp = 1
        self.temperature_offset = 11.11
        self.update_configuration_settings_list()

    def set_settings_for_test2(self):
        self.web_portal_port = 12289
        self.enable_debug_logging = 0
        self.enable_interval_recording = 0
        self.enable_trigger_recording = 0
        self.sleep_duration_interval = 320.58
        self.enable_custom_temp = 0
        self.temperature_offset = 0.0
        self.update_configuration_settings_list()


class CreateInstalledSensorsConfigurationTest(CreateInstalledSensorsConfiguration):
    def __init__(self):
        CreateInstalledSensorsConfiguration.__init__(self, load_from_file=False)
        self.static_config_test = """Enable = 1 & Disable = 0
1 = Gnu/Linux
0 = Raspberry Pi
1 = Raspberry Pi Sense HAT
0 = Pimoroni BH1745
1 = Pimoroni AS7262
0 = Pimoroni MCP9600
1 = Pimoroni BMP280
0 = Pimoroni BME680
1 = Pimoroni EnviroPHAT
0 = Pimoroni Enviro+
1 = Pimoroni SGP30
0 = Pimoroni PMS5003
1 = Pimoroni MSA301
0 = Pimoroni LSM303D
1 = Pimoroni ICM20948
0 = Pimoroni VL53L1X
1 = Pimoroni LTR-559
0 = Pimoroni VEML6075
1 = Pimoroni 11x7 LED Matrix
0 = Pimoroni 10.96'' SPI Colour LCD (160x80)
1 = Pimoroni 1.12'' Mono OLED (128x128, white/black)
1 = Kootnet Dummy Sensors
0 = Sensirion SPS30"""

    def set_settings_for_test1(self):
        self.linux_system = 0
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

    def set_settings_for_test2(self):
        self.linux_system = 1
        self.raspberry_pi = 1

        self.raspberry_pi_sense_hat = 1
        self.pimoroni_bh1745 = 1
        self.pimoroni_as7262 = 1
        self.pimoroni_mcp9600 = 1
        self.pimoroni_bmp280 = 1
        self.pimoroni_bme680 = 1
        self.pimoroni_enviro = 1
        self.pimoroni_enviroplus = 1
        self.pimoroni_sgp30 = 1
        self.pimoroni_pms5003 = 1
        self.pimoroni_msa301 = 1
        self.pimoroni_lsm303d = 1
        self.pimoroni_icm20948 = 1
        self.pimoroni_vl53l1x = 1
        self.pimoroni_ltr_559 = 1
        self.pimoroni_veml6075 = 1

        self.pimoroni_matrix_11x7 = 1
        self.pimoroni_st7735 = 1
        self.pimoroni_mono_oled_luma = 1
        self.update_configuration_settings_list()


class CreateTriggerVariancesConfigurationTest(CreateTriggerVariancesConfiguration):
    def __init__(self):
        CreateTriggerVariancesConfiguration.__init__(self, load_from_file=False)
        self.static_config_test = """Configure Variance Settings.  0 = Disabled, 1 = Enabled
1 = Enable Sensor Uptime
22.12 = Seconds between SQL Writes of Sensor Uptime
1 = Enable CPU Temperature
345.0 = CPU Temperature variance
122.0 = Seconds between 'CPU Temperature' readings
1 = Enable Environmental Temperature
134.5 = Environmental Temperature variance
332.0 = Seconds between 'Env Temperature' readings
0 = Enable Pressure
122.64 = Pressure variance
121.56 = Seconds between 'Pressure' readings
0 = Enable Altitude
130.0 = Altitude variance
131.0 = Seconds between 'Altitude' readings
0 = Enable Humidity
53.0 = Humidity variance
602.0 = Seconds between 'Humidity' readings
0 = Enable Distance
6200.0 = Distance variance
331.0 = Seconds between 'Distance' readings
0 = Enable Gas
1030.0 = Gas Resistance Index variance
1030.0 = Gas Oxidising variance
1050.0 = Gas Reducing variance
1800.0 = Gas NH3 variance
308.0 = Seconds between 'Gas' readings
0 = Enable Particulate Matter (PM)
433.0 = Particulate Matter 1 (PM1) variance
44.0 = Particulate Matter 2.5 (PM2.5) variance
674.0 = Particulate Matter 10 (PM10) variance
650.0 = Seconds between 'PM' readings
1 = Enable Lumen
5100.0 = Lumen variance
150.0 = Seconds between 'Lumen' readings
0 = Enable Colour
1555.0 = Red variance
1665.0 = Orange variance
1775.0 = Yellow variance
1785.0 = Green variance
1995.0 = Blue variance
1885.0 = Violet variance
1044.0 = Seconds between 'Colour' readings
0 = Enable Ultra Violet
335.0 = Ultra Violet Index variance
104.32 = Ultra Violet A variance
3210.3 = Ultra Violet B variance
533.0 = Seconds between 'Ultra Violet' readings
1 = Enable Accelerometer
110.1 = Accelerometer X variance
30.1 = Accelerometer Y variance
40.1 = Accelerometer Z variance
2350.3 = Seconds between 'Accelerometer' readings
0 = Enable Magnetometer
2522.0 = Magnetometer X variance
325.0 = Magnetometer Y variance
5245.0 = Magnetometer Z variance
660.3 = Seconds between 'Magnetometer' readings
0 = Enable Gyroscope
252.0 = Gyroscope X variance
275.0 = Gyroscope Y variance
285.0 = Gyroscope Z variance
1202.3 = Seconds between 'Gyroscope' readings
"""

    def set_settings_for_test1(self):
        self.sensor_uptime_enabled = 0
        self.sensor_uptime_wait_seconds = 240.729

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
        self._update_configuration_settings_list()

    def set_settings_for_test2(self):
        self.sensor_uptime_enabled = 1
        self.sensor_uptime_wait_seconds = 658.169

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
        self._update_configuration_settings_list()


class CreateSensorControlConfigurationTest(CreateSensorControlConfiguration):
    def __init__(self):
        CreateSensorControlConfiguration.__init__(self, load_from_file=False)
        self.static_config_test = """This contains saved values for HTML Sensor Control
combo_report = selected_action
None = selected_send_type
192.168.7.216 = senor_ip_1
223.222.44.5 = senor_ip_2
223.222.44.5 = senor_ip_3
223.222.44.5 = senor_ip_4
223.222.44.5 = senor_ip_5
223.222.44.5 = senor_ip_6
223.222.44.5 = senor_ip_7
 = senor_ip_8
223.222.44.5 = senor_ip_9
223.222.44.5 = senor_ip_10
server2.dsomethin.krack.net:22344 = senor_ip_11
 = senor_ip_12
223.222.44.5 = senor_ip_13
 = senor_ip_14
223.222.44.5 = senor_ip_15
223.222.44.5 = senor_ip_16
 = senor_ip_17
 = senor_ip_18
server.dsomethin.krack:33344 = senor_ip_19
 = senor_ip_20"""

    def set_settings_for_test1(self):
        self.selected_action = self.radio_download_reports
        self.selected_send_type = self.radio_send_type_relayed
        self.sensor_ip_dns1 = "1.2.3.4"
        self.sensor_ip_dns2 = "1.2.3.4"
        self.sensor_ip_dns3 = "1.2.3.4"
        self.sensor_ip_dns4 = "1.2.3.4"
        self.sensor_ip_dns5 = "1.2.3.4"
        self.sensor_ip_dns6 = "1.2.3.4"
        self.sensor_ip_dns7 = "1.2.3.4"
        self.sensor_ip_dns8 = "1.2.3.4"
        self.sensor_ip_dns9 = "1.2.3.4"
        self.sensor_ip_dns10 = "1.2.3.4"
        self.sensor_ip_dns11 = "1.2.3.4"
        self.sensor_ip_dns12 = "1.2.3.4"
        self.sensor_ip_dns13 = "1.2.3.4"
        self.sensor_ip_dns14 = "1.2.3.4"
        self.sensor_ip_dns15 = "1.2.3.4"
        self.sensor_ip_dns16 = "1.2.3.4"
        self.sensor_ip_dns17 = "1.2.3.4"
        self.sensor_ip_dns18 = "1.2.3.4"
        self.sensor_ip_dns19 = "1.2.3.4"
        self.sensor_ip_dns20 = "1.2.3.4"
        self._update_configuration_settings_list()

    def set_settings_for_test2(self):
        self.selected_action = self.radio_download_logs
        self.selected_send_type = self.radio_send_type_direct
        self.sensor_ip_dns1 = "229.165.237.111"
        self.sensor_ip_dns2 = "229.165.237.111"
        self.sensor_ip_dns3 = "229.165.237.111"
        self.sensor_ip_dns4 = "229.165.237.111"
        self.sensor_ip_dns5 = "229.165.237.111"
        self.sensor_ip_dns6 = "229.165.237.111"
        self.sensor_ip_dns7 = "229.165.237.111"
        self.sensor_ip_dns8 = "229.165.237.111"
        self.sensor_ip_dns9 = "229.165.237.111"
        self.sensor_ip_dns10 = "229.165.237.111"
        self.sensor_ip_dns11 = "229.165.237.111"
        self.sensor_ip_dns12 = "229.165.237.111"
        self.sensor_ip_dns13 = "229.165.237.111"
        self.sensor_ip_dns14 = "229.165.237.111"
        self.sensor_ip_dns15 = "229.165.237.111"
        self.sensor_ip_dns16 = "229.165.237.111"
        self.sensor_ip_dns17 = "229.165.237.111"
        self.sensor_ip_dns18 = "229.165.237.111"
        self.sensor_ip_dns19 = "229.165.237.111"
        self.sensor_ip_dns20 = "229.165.237.111"
        self._update_configuration_settings_list()


class CreateWeatherUndergroundConfigurationTest(CreateWeatherUndergroundConfiguration):
    def __init__(self):
        CreateWeatherUndergroundConfiguration.__init__(self, load_from_file=False)
        self.static_config_test = """Enable = 1 & Disable = 0
0 = Enable Weather Underground
9332.0 = Send to Server in Seconds
1 = Sensor is Outdoors
SOMETHING = Weather Underground Station ID
SOMETHINGELSE = Weather Underground Station Key
1 = Enable Rapid Fire Updates"""

    def set_settings_for_test1(self):
        self.weather_underground_enabled = 0
        self.interval_seconds = 999.9
        self.outdoor_sensor = 0
        self.station_id = "Test_1"
        self.station_key = "Test_2"
        self.wu_rapid_fire_enabled = 0
        self._update_configuration_settings_list()

    def set_settings_for_test2(self):
        self.weather_underground_enabled = 1
        self.interval_seconds = 78855.321
        self.outdoor_sensor = 1
        self.station_id = "Test_3"
        self.station_key = "Test_5"
        self.wu_rapid_fire_enabled = 1
        self._update_configuration_settings_list()


class CreateLuftdatenConfigurationTest(CreateLuftdatenConfiguration):
    def __init__(self):
        CreateLuftdatenConfiguration.__init__(self, load_from_file=False)
        self.static_config_test = """Enable = 1 & Disable = 0
0 = Enable Luftdaten
3333.3 = Send to Server in Seconds"""

    def set_settings_for_test1(self):
        self.luftdaten_enabled = 0
        self.interval_seconds = 9663.09
        self._update_configuration_settings_list()

    def set_settings_for_test2(self):
        self.luftdaten_enabled = 1
        self.interval_seconds = 55712.21
        self._update_configuration_settings_list()


class CreateOpenSenseMapConfigurationTest(CreateOpenSenseMapConfiguration):
    def __init__(self):
        CreateOpenSenseMapConfiguration.__init__(self, load_from_file=False)
        self.static_config_test = """Enable = 1 & Disable = 0
0 = Enable Open Sense Map
Mega2311kk = SenseBox ID
9023.1 = Send to Server in Seconds
234kjh25asdgfh = Temperature Sensor ID
234kjh25h23sdgd = Pressure Sensor ID
234kjh444 = Altitude Sensor ID
234kjh25h3dd = Humidity Sensor ID
234kjh25hddd = Gas VOC Sensor ID
234kjh254hfs234 = Gas NH3 Sensor ID
2344kjh25h235 = Gas Oxidised Sensor ID
234kj44h234234 = Gas Reduced Sensor ID
2344kjh25h = PM 1.0 Sensor ID
234kjh425h = PM 2.5 Sensor ID
234kjerh25h = PM 10 Sensor ID
234kjah25h = Lumen Sensor ID
234kjsh25h = Red Sensor ID
234kjdh25h = Orange Sensor ID
234kjvh25h = Yellow Sensor ID
234kjh25h = Green Sensor ID
234kjhag25h = Blue Sensor ID
234kjh5225h = Violet Sensor ID
234kjhsadgf25h = Ultra Violet Index Sensor ID
234kjh2ags5h = Ultra Violet A Sensor ID
234kjsdfh25h = Ultra Violet B Sensor ID"""

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
        self._update_configuration_settings_list()

    def set_settings_for_test2(self):
        self.open_sense_map_enabled = 1
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
        self._update_configuration_settings_list()


class TestApp(unittest.TestCase):
    def test_primary_config(self):
        self.assertTrue(self._config_test_changes(primary_config_test,
                                                  remote_get.sensor_configuration_file,
                                                  remote_set.set_primary_configuration,
                                                  config_name="Primary"))

    def test_installed_sensors_config(self):
        self.assertTrue(self._config_test_changes(installed_sensors_config_test,
                                                  remote_get.installed_sensors_file,
                                                  remote_set.set_installed_sensors,
                                                  config_name="Installed Sensors"))

    def test_trigger_variances_config(self):
        self.assertTrue(self._config_test_changes(trigger_variances_config_test,
                                                  remote_get.variance_config,
                                                  remote_set.set_variance_configuration,
                                                  config_name="Triggers"))

    def test_sensor_control_config(self):
        self.assertTrue(self._config_test_changes(sensor_control_config_test,
                                                  remote_get.sensor_control_configuration_file,
                                                  remote_set.set_sensor_control_configuration,
                                                  config_name="Sensor Control"))

    def test_weather_underground_config(self):
        self.assertTrue(self._config_test_changes(weather_underground_config_test,
                                                  remote_get.weather_underground_config_file,
                                                  remote_set.set_weather_underground_configuration,
                                                  config_name="Weather Underground"))

    def test_luftdaten_config(self):
        self.assertTrue(self._config_test_changes(luftdaten_config_test,
                                                  remote_get.luftdaten_config_file,
                                                  remote_set.set_luftdaten_configuration,
                                                  config_name="Luftdaten"))

    def test_open_sense_map_config(self):
        self.assertTrue(self._config_test_changes(open_sense_map_config_test,
                                                  remote_get.open_sense_map_config_file,
                                                  remote_set.set_open_sense_map_configuration,
                                                  config_name="OSM"))

    def _config_test_changes(self, config_instance, config_get_command, config_set_command, config_name=""):
        original_config = get_http_sensor_reading(sensor_address, command=config_get_command)

        config_instance.set_settings_for_test1()

        send_config = config_instance.get_config_as_str()
        send_http_command(sensor_address, command=config_set_command, included_data=send_config, test_run=True)
        first_set_config = get_http_sensor_reading(sensor_address, command=config_get_command)
        if self._bad_config(config_instance.get_config_as_str(), first_set_config, config_name=config_name + " 1"):
            send_http_command(sensor_address, command=config_set_command, included_data=original_config, test_run=True)
            return False

        config_instance.set_settings_for_test2()

        send_config = config_instance.get_config_as_str()
        send_http_command(sensor_address, command=config_set_command, included_data=send_config, test_run=True)
        second_set_config = get_http_sensor_reading(sensor_address, command=config_get_command)
        if self._bad_config(config_instance.get_config_as_str(), second_set_config, config_name=config_name + " 2"):
            send_http_command(sensor_address, command=config_set_command, included_data=original_config, test_run=True)
            return False

        send_config = config_instance.static_config_test
        send_http_command(sensor_address, command=config_set_command, included_data=send_config, test_run=True)
        second_set_config = get_http_sensor_reading(sensor_address, command=config_get_command)
        if self._bad_config(config_instance.static_config_test, second_set_config, config_name=config_name + " 3"):
            send_http_command(sensor_address, command=config_set_command, included_data=original_config, test_run=True)
            return False

        send_http_command(sensor_address, command=config_set_command, included_data=original_config, test_run=True)

        original_set_config = get_http_sensor_reading(sensor_address, command=config_get_command)
        if self._bad_config(original_config, original_set_config, config_name=config_name + " 4"):
            send_http_command(sensor_address, command=config_set_command, included_data=original_config, test_run=True)
            return False
        return True

    @staticmethod
    def _bad_config(sent_config, received_config, config_name=""):
        if sent_config.strip() == received_config.strip():
            print("Info: Configuration " + config_name + " Check OK.")
            return False
        print("Error: Sent " + config_name + " Configuration is different from Received Configuration\n")
        print("-Sent Configuration-\n" + str(sent_config) + "\n-Received Configuration-\n" + str(received_config))
        return True

    def test_html_display_text(self):
        msg = "This is a Test Message"
        if http_display_text_on_sensor(msg, sensor_address):
            print("Info: Sent Sensor Display Message OK")
            self.assertTrue(True)
        else:
            self.assertTrue(False)
            print("Error: Sent Sensor Display Message Failed")

    def test_sensor_get_commands(self):
        sensor_responses = []
        for command in sensor_get_commands:
            sensor_responses.append(get_http_sensor_reading(sensor_address, command=command, timeout=5))

        bad_count = 0
        for response in sensor_responses:
            if response is None:
                bad_count += 1

        if bad_count > 0:
            log_msg = "Warning: " + str(bad_count) + " Bad HTTPS Responses out of " + str(len(sensor_get_commands))
            print(log_msg + " - Bad Network Connection?")
        # from routes file system_commands.py
        self.assertTrue(sensor_responses[0] == "OK")
        self.assertTrue(isinstance(sensor_responses[1], str))
        if not check_no_sensor_return(sensor_responses[2], sensor_get_commands[2]):
            self.assertTrue(isinstance(sensor_responses[2], str))
        # from routes file text_sensor_readings.py
        if not check_no_sensor_return(sensor_responses[3], sensor_get_commands[3]):
            sensor_reading = sensor_responses[3].split(command_data_separator)
            self.assertTrue(len(sensor_reading[0].split(",")) > 0)
            self.assertTrue(len(sensor_reading[1].split(",")) > 0)
        if not check_no_sensor_return(sensor_responses[4], sensor_get_commands[4]):
            sensor_reading = sensor_responses[4].split(command_data_separator)
            self.assertTrue(len(sensor_reading[0].split(",")) > 0)
            self.assertTrue(len(sensor_reading[1].split(",")) > 0)
        if not check_no_sensor_return(sensor_responses[5], sensor_get_commands[5]):
            self.assertTrue(isinstance(float(sensor_responses[5]), float))
        if not check_no_sensor_return(sensor_responses[6], sensor_get_commands[6]):
            self.assertTrue(isinstance(float(sensor_responses[6]), float))
        if not check_no_sensor_return(sensor_responses[7], sensor_get_commands[7]):
            self.assertTrue(isinstance(float(sensor_responses[7]), float))
        if not check_no_sensor_return(sensor_responses[8], sensor_get_commands[8]):
            self.assertTrue(isinstance(float(sensor_responses[8]), float))
        if not check_no_sensor_return(sensor_responses[9], sensor_get_commands[9]):
            self.assertTrue(isinstance(float(sensor_responses[9]), float))
        if not check_no_sensor_return(sensor_responses[10], sensor_get_commands[10]):
            self.assertTrue(isinstance(float(sensor_responses[10]), float))
        if not check_no_sensor_return(sensor_responses[11], sensor_get_commands[11]):
            self.assertTrue(isinstance(float(sensor_responses[11]), float))
        if not check_no_sensor_return(sensor_responses[12], sensor_get_commands[12]):
            self.assertTrue(len(sensor_responses[12][1:-1].split(",")) == 4)
        if not check_no_sensor_return(sensor_responses[13], sensor_get_commands[13]):
            self.assertTrue(isinstance(float(sensor_responses[13]), float))
        if not check_no_sensor_return(sensor_responses[14], sensor_get_commands[14]):
            self.assertTrue(isinstance(float(sensor_responses[14]), float))
        if not check_no_sensor_return(sensor_responses[15], sensor_get_commands[15]):
            self.assertTrue(isinstance(float(sensor_responses[15]), float))
        if not check_no_sensor_return(sensor_responses[16], sensor_get_commands[16]):
            self.assertTrue(isinstance(float(sensor_responses[16]), float))
        if not check_no_sensor_return(sensor_responses[17], sensor_get_commands[17]):
            self.assertTrue(len(sensor_responses[17][1:-1].split(",")) == 3)
        if not check_no_sensor_return(sensor_responses[18], sensor_get_commands[18]):
            self.assertTrue(isinstance(float(sensor_responses[18]), float))
        if not check_no_sensor_return(sensor_responses[19], sensor_get_commands[19]):
            self.assertTrue(isinstance(float(sensor_responses[19]), float))
        if not check_no_sensor_return(sensor_responses[20], sensor_get_commands[20]):
            self.assertTrue(isinstance(float(sensor_responses[20]), float))
        if not check_no_sensor_return(sensor_responses[21], sensor_get_commands[21]):
            self.assertTrue(isinstance(float(sensor_responses[21]), float))
        if not check_no_sensor_return(sensor_responses[22], sensor_get_commands[22]):
            sensor_reading = sensor_responses[22][1:-1].split(",")
            self.assertTrue(isinstance(float(sensor_reading[0]), float))
        if not check_no_sensor_return(sensor_responses[23], sensor_get_commands[23]):
            self.assertTrue(len(sensor_responses[23][1:-1].split(",")) == 2)
        if not check_no_sensor_return(sensor_responses[24], sensor_get_commands[24]):
            self.assertTrue(isinstance(float(sensor_responses[24]), float))
        if not check_no_sensor_return(sensor_responses[25], sensor_get_commands[25]):
            self.assertTrue(isinstance(float(sensor_responses[25]), float))
        if not check_no_sensor_return(sensor_responses[26], sensor_get_commands[26]):
            sensor_reading = sensor_responses[26][1:-1].split(",")
            self.assertTrue(isinstance(float(sensor_reading[0]), float))
            self.assertTrue(isinstance(float(sensor_reading[1]), float))
            self.assertTrue(isinstance(float(sensor_reading[2]), float))
        if not check_no_sensor_return(sensor_responses[27], sensor_get_commands[27]):
            sensor_reading = sensor_responses[27][1:-1].split(",")
            self.assertTrue(isinstance(float(sensor_reading[0]), float))
            self.assertTrue(isinstance(float(sensor_reading[1]), float))
            self.assertTrue(isinstance(float(sensor_reading[2]), float))
        if not check_no_sensor_return(sensor_responses[28], sensor_get_commands[28]):
            sensor_reading = sensor_responses[28][1:-1].split(",")
            self.assertTrue(isinstance(float(sensor_reading[0]), float))
            self.assertTrue(isinstance(float(sensor_reading[1]), float))
            self.assertTrue(isinstance(float(sensor_reading[2]), float))
        sleep(1)


def check_no_sensor_return(sensor_data, data_name):
    if sensor_data == no_sensor_present:
        print("Warning: " + data_name + " Reading as No Sensor Present")
        return True
    print("Info: " + data_name + " OK")
    return False


primary_config_test = CreatePrimaryConfigurationTest()
installed_sensors_config_test = CreateInstalledSensorsConfigurationTest()
trigger_variances_config_test = CreateTriggerVariancesConfigurationTest()
sensor_control_config_test = CreateSensorControlConfigurationTest()
weather_underground_config_test = CreateWeatherUndergroundConfigurationTest()
luftdaten_config_test = CreateLuftdatenConfigurationTest()
open_sense_map_config_test = CreateOpenSenseMapConfigurationTest()

sensor_address = "localhost"

remote_set = CreateNetworkSetCommands()
remote_get = CreateNetworkGetCommands()
sensor_get_commands = [remote_get.check_online_status, remote_get.sensor_name, remote_get.system_uptime,
                       remote_get.sensor_readings, remote_get.sensors_latency, remote_get.cpu_temp,
                       remote_get.environmental_temp, remote_get.env_temp_offset, remote_get.pressure,
                       remote_get.altitude, remote_get.humidity, remote_get.distance, remote_get.all_gas,
                       remote_get.gas_index, remote_get.gas_oxidised, remote_get.gas_reduced, remote_get.gas_nh3,
                       remote_get.all_particulate_matter, remote_get.pm_1, remote_get.pm_2_5, remote_get.pm_10,
                       remote_get.lumen, remote_get.electromagnetic_spectrum, remote_get.all_ultra_violet,
                       remote_get.ultra_violet_a, remote_get.ultra_violet_b, remote_get.accelerometer_xyz,
                       remote_get.magnetometer_xyz, remote_get.gyroscope_xyz]

bad_sensor_contact = True
bad_sensor_login = True
if get_http_sensor_reading(sensor_address, timeout=5) == "OK":
    bad_sensor_contact = False
    if get_http_sensor_reading(sensor_address, command="TestLogin", timeout=5) == "OK":
        bad_sensor_login = False


if __name__ == '__main__':
    if not bad_sensor_login and not bad_sensor_contact:
        unittest.main()
    else:
        if bad_sensor_contact:
            print("\n-- Sensor Offline --\n")
        elif bad_sensor_login:
            print("\n-- Incorrect Sensor Login --\n")
