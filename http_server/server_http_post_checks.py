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
from operations_modules import configuration_main


def check_html_installed_sensors(html_request):
    logger.network_logger.debug("Starting HTML Installed Sensors Update Check")
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
        configuration_main.current_config.sleep_duration_interval = html_request.form.get(
            "interval_delay_seconds")

    if html_request.form.get("enable_trigger_recording") is not None:
        configuration_main.current_config.enable_trigger_recording = 1
    else:
        configuration_main.current_config.enable_trigger_recording = 0

    if html_request.form.get("enable_custom_temp_offset") is not None:
        configuration_main.current_config.enable_custom_temp = 1
        configuration_main.current_config.temperature_offset = html_request.form.get(
            "custom_temperature_offset")
    else:
        configuration_main.current_config.enable_custom_temp = 0


def get_html_checkbox_state(config_setting):
    if config_setting:
        return "checked"
    else:
        return ""
