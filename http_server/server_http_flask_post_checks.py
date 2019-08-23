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
import os
import shutil
from operations_modules import logger
from operations_modules import app_cached_variables
from operations_modules import file_locations
from operations_modules import configuration_main
from operations_modules import configuration_files
from operations_modules import app_generic_functions
from operations_modules import network_ip
from operations_modules import network_wifi
from operations_modules import trigger_variances as trigger_import


def check_html_config_main(html_request):
    logger.network_logger.debug("Starting HTML Main Configuration Update Check")
    if html_request.form.get("debug_logging") is not None:
        configuration_main.current_config.enable_debug_logging = 1
    else:
        configuration_main.current_config.enable_debug_logging = 0

    if html_request.form.get("enable_display") is not None:
        configuration_main.current_config.enable_display = 1
    else:
        configuration_main.current_config.enable_display = 0

    if html_request.form.get("enable_interval_recording") is not None:
        configuration_main.current_config.enable_interval_recording = 1
    else:
        configuration_main.current_config.enable_interval_recording = 0
    if html_request.form.get("interval_delay_seconds") is not None:
        configuration_main.current_config.sleep_duration_interval = float(html_request.form.get(
            "interval_delay_seconds"))

    if html_request.form.get("enable_trigger_recording") is not None:
        configuration_main.current_config.enable_trigger_recording = 1
    else:
        configuration_main.current_config.enable_trigger_recording = 0

    if html_request.form.get("enable_custom_temp_offset") is not None:
        configuration_main.current_config.enable_custom_temp = 1
        configuration_main.current_config.temperature_offset = float(html_request.form.get(
            "custom_temperature_offset"))
    else:
        configuration_main.current_config.enable_custom_temp = 0

    configuration_files.write_config_to_file(configuration_main.current_config)


def check_html_installed_sensors(html_request):
    logger.network_logger.debug("Starting HTML Installed Sensors Update Check")
    try:
        if html_request.form.get("linux_system") is not None:
            configuration_main.installed_sensors.linux_system = 1
        else:
            configuration_main.installed_sensors.linux_system = 0

        if html_request.form.get("raspberry_pi_zero_w") is not None:
            configuration_main.installed_sensors.raspberry_pi_zero_w = 1
        else:
            configuration_main.installed_sensors.raspberry_pi_zero_w = 0

        if html_request.form.get("raspberry_pi_3b_plus") is not None:
            configuration_main.installed_sensors.raspberry_pi_3b_plus = 1
        else:
            configuration_main.installed_sensors.raspberry_pi_3b_plus = 0

        if html_request.form.get("raspberry_pi_sense_hat") is not None:
            configuration_main.installed_sensors.raspberry_pi_sense_hat = 1
        else:
            configuration_main.installed_sensors.raspberry_pi_sense_hat = 0

        if html_request.form.get("pimoroni_bh1745") is not None:
            configuration_main.installed_sensors.pimoroni_bh1745 = 1
        else:
            configuration_main.installed_sensors.pimoroni_bh1745 = 0

        if html_request.form.get("pimoroni_as7262") is not None:
            configuration_main.installed_sensors.pimoroni_as7262 = 1
        else:
            configuration_main.installed_sensors.pimoroni_as7262 = 0

        if html_request.form.get("pimoroni_bmp280") is not None:
            configuration_main.installed_sensors.pimoroni_bmp280 = 1
        else:
            configuration_main.installed_sensors.pimoroni_bmp280 = 0

        if html_request.form.get("pimoroni_bme680") is not None:
            configuration_main.installed_sensors.pimoroni_bme680 = 1
        else:
            configuration_main.installed_sensors.pimoroni_bme680 = 0

        if html_request.form.get("pimoroni_enviro") is not None:
            configuration_main.installed_sensors.pimoroni_enviro = 1
        else:
            configuration_main.installed_sensors.pimoroni_enviro = 0

        if html_request.form.get("pimoroni_enviroplus") is not None:
            configuration_main.installed_sensors.pimoroni_enviroplus = 1
        else:
            configuration_main.installed_sensors.pimoroni_enviroplus = 0

        if html_request.form.get("pimoroni_pms5003") is not None:
            configuration_main.installed_sensors.pimoroni_pms5003 = 1
        else:
            configuration_main.installed_sensors.pimoroni_pms5003 = 0

        if html_request.form.get("pimoroni_lsm303d") is not None:
            configuration_main.installed_sensors.pimoroni_lsm303d = 1
        else:
            configuration_main.installed_sensors.pimoroni_lsm303d = 0

        if html_request.form.get("pimoroni_icm20948") is not None:
            configuration_main.installed_sensors.pimoroni_icm20948 = 1
        else:
            configuration_main.installed_sensors.pimoroni_icm20948 = 0

        if html_request.form.get("pimoroni_vl53l1x") is not None:
            configuration_main.installed_sensors.pimoroni_vl53l1x = 1
        else:
            configuration_main.installed_sensors.pimoroni_vl53l1x = 0

        if html_request.form.get("pimoroni_ltr_559") is not None:
            configuration_main.installed_sensors.pimoroni_ltr_559 = 1
        else:
            configuration_main.installed_sensors.pimoroni_ltr_559 = 0

        if html_request.form.get("pimoroni_veml6075") is not None:
            configuration_main.installed_sensors.pimoroni_veml6075 = 1
        else:
            configuration_main.installed_sensors.pimoroni_veml6075 = 0

        if html_request.form.get("pimoroni_matrix_11x7") is not None:
            configuration_main.installed_sensors.pimoroni_matrix_11x7 = 1
        else:
            configuration_main.installed_sensors.pimoroni_matrix_11x7 = 0

        if html_request.form.get("pimoroni_st7735") is not None:
            configuration_main.installed_sensors.pimoroni_st7735 = 1
        else:
            configuration_main.installed_sensors.pimoroni_st7735 = 0

        if html_request.form.get("pimoroni_mono_oled_luma") is not None:
            configuration_main.installed_sensors.pimoroni_mono_oled_luma = 1
        else:
            configuration_main.installed_sensors.pimoroni_mono_oled_luma = 0

        installed_sensors = configuration_main.installed_sensors.get_installed_sensors_config_as_str()
        configuration_files.write_installed_sensors_to_file(installed_sensors)
    except Exception as error:
        logger.network_logger.debug("Trigger Error: " + str(error))


def check_html_variance_triggers(html_request):
    logger.network_logger.debug("Starting HTML Variance Triggers Update Check")
    if html_request.form.get("checkbox_sensor_uptime") is not None:
        new_uptime_days = float(html_request.form.get("days_sensor_uptime")) * 60.0 * 60.0 * 24.0
        configuration_main.trigger_variances.sensor_uptime_enabled = 1
        configuration_main.trigger_variances.sensor_uptime_wait_seconds = new_uptime_days
    else:
        configuration_main.trigger_variances.sensor_uptime_enabled = 0

    if html_request.form.get("checkbox_cpu_temperature") is not None:
        new_variance = html_request.form.get("trigger_cpu_temperature")
        new_seconds_delay = html_request.form.get("seconds_cpu_temperature")
        configuration_main.trigger_variances.cpu_temperature_enabled = 1
        configuration_main.trigger_variances.cpu_temperature_variance = new_variance
        configuration_main.trigger_variances.cpu_temperature_wait_seconds = new_seconds_delay
    else:
        configuration_main.trigger_variances.cpu_temperature_enabled = 0

    if html_request.form.get("env_temperature") is not None:
        new_variance = html_request.form.get("trigger_env_temperature")
        new_seconds_delay = html_request.form.get("seconds_env_temperature")
        configuration_main.trigger_variances.env_temperature_enabled = 1
        configuration_main.trigger_variances.env_temperature_variance = new_variance
        configuration_main.trigger_variances.env_temperature_wait_seconds = new_seconds_delay
    else:
        configuration_main.trigger_variances.env_temperature_enabled = 0

    if html_request.form.get("pressure") is not None:
        new_variance = html_request.form.get("trigger_pressure")
        new_seconds_delay = html_request.form.get("seconds_pressure")
        configuration_main.trigger_variances.pressure_enabled = 1
        configuration_main.trigger_variances.pressure_variance = new_variance
        configuration_main.trigger_variances.pressure_wait_seconds = new_seconds_delay
    else:
        configuration_main.trigger_variances.pressure_enabled = 0

    if html_request.form.get("humidity") is not None:
        new_variance = html_request.form.get("trigger_humidity")
        new_seconds_delay = html_request.form.get("seconds_humidity")
        configuration_main.trigger_variances.humidity_enabled = 1
        configuration_main.trigger_variances.humidity_variance = new_variance
        configuration_main.trigger_variances.humidity_wait_seconds = new_seconds_delay
    else:
        configuration_main.trigger_variances.humidity_enabled = 0

    if html_request.form.get("altitude") is not None:
        new_variance = html_request.form.get("trigger_altitude")
        new_seconds_delay = html_request.form.get("seconds_altitude")
        configuration_main.trigger_variances.altitude_enabled = 1
        configuration_main.trigger_variances.altitude_variance = new_variance
        configuration_main.trigger_variances.altitude_wait_seconds = new_seconds_delay
    else:
        configuration_main.trigger_variances.altitude_enabled = 0

    if html_request.form.get("distance") is not None:
        new_variance = html_request.form.get("trigger_distance")
        new_seconds_delay = html_request.form.get("seconds_distance")
        configuration_main.trigger_variances.distance_enabled = 1
        configuration_main.trigger_variances.distance_variance = new_variance
        configuration_main.trigger_variances.distance_wait_seconds = new_seconds_delay
    else:
        configuration_main.trigger_variances.distance_enabled = 0

    if html_request.form.get("lumen") is not None:
        new_variance = html_request.form.get("trigger_lumen")
        new_seconds_delay = html_request.form.get("seconds_lumen")
        configuration_main.trigger_variances.lumen_enabled = 1
        configuration_main.trigger_variances.lumen_variance = new_variance
        configuration_main.trigger_variances.lumen_wait_seconds = new_seconds_delay
    else:
        configuration_main.trigger_variances.lumen_enabled = 0

    if html_request.form.get("colour") is not None:
        new_variance_red = html_request.form.get("red")
        new_variance_orange = html_request.form.get("orange")
        new_variance_yellow = html_request.form.get("yellow")
        new_variance_green = html_request.form.get("green")
        new_variance_blue = html_request.form.get("blue")
        new_variance_violet = html_request.form.get("violet")
        new_seconds_delay = html_request.form.get("seconds_colour")
        configuration_main.trigger_variances.colour_enabled = 1
        configuration_main.trigger_variances.red_variance = new_variance_red
        configuration_main.trigger_variances.orange_variance = new_variance_orange
        configuration_main.trigger_variances.yellow_variance = new_variance_yellow
        configuration_main.trigger_variances.green_variance = new_variance_green
        configuration_main.trigger_variances.blue_variance = new_variance_blue
        configuration_main.trigger_variances.violet_variance = new_variance_violet
        configuration_main.trigger_variances.colour_wait_seconds = new_seconds_delay
    else:
        configuration_main.trigger_variances.colour_enabled = 0

    if html_request.form.get("ultra_violet") is not None:
        new_variance_uva = html_request.form.get("ultra_violet_a")
        new_variance_uvb = html_request.form.get("ultra_violet_b")
        new_seconds_delay = html_request.form.get("seconds_ultra_violet")
        configuration_main.trigger_variances.ultra_violet_enabled = 1
        configuration_main.trigger_variances.ultra_violet_a_variance = new_variance_uva
        configuration_main.trigger_variances.ultra_violet_b_variance = new_variance_uvb
        configuration_main.trigger_variances.ultra_violet_wait_seconds = new_seconds_delay
    else:
        configuration_main.trigger_variances.ultra_violet_enabled = 0

    if html_request.form.get("gas") is not None:
        new_variance_index = html_request.form.get("trigger_gas_index")
        new_variance_oxidising = html_request.form.get("trigger_gas_oxidising")
        new_variance_reducing = html_request.form.get("trigger_gas_reducing")
        new_variance_nh3 = html_request.form.get("trigger_gas_nh3")
        new_seconds_delay = html_request.form.get("seconds_gas")
        configuration_main.trigger_variances.gas_enabled = 1
        configuration_main.trigger_variances.gas_resistance_index_variance = new_variance_index
        configuration_main.trigger_variances.gas_oxidising_variance = new_variance_oxidising
        configuration_main.trigger_variances.gas_reducing_variance = new_variance_reducing
        configuration_main.trigger_variances.gas_nh3_variance = new_variance_nh3
        configuration_main.trigger_variances.gas_wait_seconds = new_seconds_delay
    else:
        configuration_main.trigger_variances.gas_enabled = 0

    if html_request.form.get("particulate_matter") is not None:
        new_variance_pm1 = html_request.form.get("trigger_pm1")
        new_variance_pm2_5 = html_request.form.get("trigger_pm2_5")
        new_variance_pm_10 = html_request.form.get("trigger_pm10")
        new_seconds_delay = html_request.form.get("seconds_pm")
        configuration_main.trigger_variances.particulate_matter_enabled = 1
        configuration_main.trigger_variances.particulate_matter_1_variance = new_variance_pm1
        configuration_main.trigger_variances.particulate_matter_2_5_variance = new_variance_pm2_5
        configuration_main.trigger_variances.particulate_matter_10_variance = new_variance_pm_10
        configuration_main.trigger_variances.humidity_wait_seconds = new_seconds_delay
    else:
        configuration_main.trigger_variances.particulate_matter_enabled = 0

    if html_request.form.get("accelerometer") is not None:
        new_variance_x = html_request.form.get("accelerometer_x")
        new_variance_y = html_request.form.get("accelerometer_y")
        new_variance_z = html_request.form.get("accelerometer_z")
        new_seconds_delay = html_request.form.get("seconds_accelerometer")
        configuration_main.trigger_variances.accelerometer_enabled = 1
        configuration_main.trigger_variances.accelerometer_x_variance = new_variance_x
        configuration_main.trigger_variances.accelerometer_y_variance = new_variance_y
        configuration_main.trigger_variances.accelerometer_z_variance = new_variance_z
        configuration_main.trigger_variances.accelerometer_wait_seconds = new_seconds_delay
    else:
        configuration_main.trigger_variances.accelerometer_enabled = 0

    if html_request.form.get("magnetometer") is not None:
        new_variance_x = html_request.form.get("magnetometer_x")
        new_variance_y = html_request.form.get("magnetometer_y")
        new_variance_z = html_request.form.get("magnetometer_z")
        new_seconds_delay = html_request.form.get("seconds_magnetometer")
        configuration_main.trigger_variances.magnetometer_enabled = 1
        configuration_main.trigger_variances.magnetometer_x_variance = new_variance_x
        configuration_main.trigger_variances.magnetometer_y_variance = new_variance_y
        configuration_main.trigger_variances.magnetometer_z_variance = new_variance_z
        configuration_main.trigger_variances.magnetometer_wait_seconds = new_seconds_delay
    else:
        configuration_main.trigger_variances.magnetometer_enabled = 0

    if html_request.form.get("gyroscope") is not None:
        new_variance_x = html_request.form.get("gyroscope_x")
        new_variance_y = html_request.form.get("gyroscope_y")
        new_variance_z = html_request.form.get("gyroscope_z")
        new_seconds_delay = html_request.form.get("seconds_gyroscope")
        configuration_main.trigger_variances.gyroscope_enabled = 1
        configuration_main.trigger_variances.gyroscope_x_variance = new_variance_x
        configuration_main.trigger_variances.gyroscope_y_variance = new_variance_y
        configuration_main.trigger_variances.gyroscope_z_variance = new_variance_z
        configuration_main.trigger_variances.gyroscope_wait_seconds = new_seconds_delay
    else:
        configuration_main.trigger_variances.gyroscope_enabled = 0

    trigger_import.write_triggers_to_file(configuration_main.trigger_variances)


def check_html_config_wifi(html_request):
    logger.network_logger.debug("Starting HTML WiFi Configuration Update Check")
    if html_request.form.get("ssid1") is not None:
        wifi_template = app_generic_functions.get_file_content(file_locations.wifi_config_file_template)

        wifi_country_code = "CA"
        if len(html_request.form.get("country_code")) == 2:
            wifi_country_code = html_request.form.get("country_code").upper()

        wifi_ssid1 = html_request.form.get("ssid1")
        wifi_security_type1 = html_request.form.get("wifi_security1")
        wifi_psk1 = html_request.form.get("wifi_key1")

        if wifi_security_type1 == "wireless_wpa":
            wifi_security_type1 = ""
            if wifi_psk1 is not "":
                wifi_template = wifi_template.replace("{{ WirelessPSK1 }}", wifi_psk1)
            else:
                wifi_template = wifi_template.replace("{{ WirelessPSK1 }}", app_cached_variables.wifi_psk)
        else:
            wifi_security_type1 = "key_mgmt=None"
            wifi_template = wifi_template.replace("{{ WirelessPSK1 }}", "")

        wifi_template = wifi_template.replace("{{ WirelessCountryCode }}", wifi_country_code)
        wifi_template = wifi_template.replace("{{ WirelessSSID1 }}", wifi_ssid1)
        wifi_template = wifi_template.replace("{{ WirelessKeyMgmt1 }}", wifi_security_type1)

        network_wifi.write_wifi_config_to_file(wifi_template)
        return wifi_template
    else:
        logger.network_logger.warning("HTML WiFi Configuration Update Failed: Missing SSID")
        return ""


def check_html_config_ipv4(html_request):
    logger.network_logger.debug("Starting HTML IPv4 Configuration Update Check")
    dhcpcd_template = app_generic_functions.get_file_content(file_locations.dhcpcd_config_file_template)

    hostname = html_request.form.get("ip_hostname")
    os.system("hostnamectl set-hostname " + hostname)
    app_cached_variables.hostname = hostname

    ip_address = html_request.form.get("ip_address")
    ip_subnet_mask = html_request.form.get("ip_subnet")
    ip_gateway = html_request.form.get("ip_gateway")
    ip_dns1 = html_request.form.get("ip_dns1")
    ip_dns2 = html_request.form.get("ip_dns2")

    ip_network_text = "interface wlan0\nstatic ip_address=" + ip_address + ip_subnet_mask + "\nstatic routers=" + ip_gateway + \
                      "\nstatic domain_name_servers=" + ip_dns1 + " " + ip_dns2

    dhcpcd_template = dhcpcd_template.replace("{{ StaticIPSettings }}", ip_network_text)
    network_ip.write_ipv4_config_to_file(dhcpcd_template)

    shutil.chown(file_locations.dhcpcd_config_file, "root", "netdev")
    os.chmod(file_locations.dhcpcd_config_file, 0o664)


def get_html_checkbox_state(config_setting):
    if config_setting:
        return "checked"
    else:
        return ""
