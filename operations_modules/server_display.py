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
from time import sleep
from operations_modules import logger
from operations_modules.app_generic_functions import CreateMonitoredThread
from operations_modules import app_cached_variables
from configuration_modules import app_config_access
from sensor_modules.system_access import get_uptime_minutes
from sensor_modules import sensor_access

db_v = app_cached_variables.database_variables


def start_display_server():
    text_name = "Display"
    function = _display_server
    app_cached_variables.mini_display_thread = CreateMonitoredThread(function, thread_name=text_name)


def _display_server():
    sleep(5)
    app_cached_variables.mini_display_thread.current_state = "Disabled"
    if not app_config_access.display_config.enable_display:
        logger.primary_logger.debug("Display Disabled in Primary Configuration")
    while not app_config_access.display_config.enable_display:
        sleep(5)
    app_cached_variables.mini_display_thread.current_state = "Running"
    app_cached_variables.restart_mini_display_thread = False
    if sensor_access.display_message("Test", check_test=True):
        logger.primary_logger.info(" -- Sensor Display Server Started")
        sleep_fraction_interval = 5
        while not app_cached_variables.restart_mini_display_thread:
            display_type_numerical = app_config_access.display_config.display_type_numerical
            if app_config_access.display_config.display_type == display_type_numerical:
                sensor_access.display_message(get_numerical_display_text())
            else:
                sensor_access.display_message(get_graphed_sensors())
            display_sleep = app_config_access.display_config.minutes_between_display * 60
            sleep_total = 0
            while sleep_total < display_sleep and not app_cached_variables.restart_mini_display_thread:
                sleep(sleep_fraction_interval)
                sleep_total += sleep_fraction_interval
    else:
        logger.primary_logger.debug("No Compatible Display Found - Display Server Entering Sleep Mode")
        while not app_cached_variables.restart_mini_display_thread:
            sleep(10)


def _get_sensor_reading_text(sensor_get_function, add_to_text):
    sensor_reading = sensor_get_function()
    if sensor_reading is not None:
        try:
            for index, reading in sensor_reading.items():
                add_to_text += index + ": " + str(reading) + " "
        except Exception as error:
            logger.primary_logger.warning("Display Server error converting reading to text: " + str(error))
    return add_to_text


def get_numerical_display_text():
    text_message = ""

    if app_config_access.display_config.sensor_uptime:
        text_message = _get_sensor_reading_text(get_uptime_minutes, text_message)
    if app_config_access.display_config.system_temperature:
        text_message = _get_sensor_reading_text(sensor_access.get_cpu_temperature, text_message)
    if app_config_access.display_config.env_temperature:
        text_message = _get_sensor_reading_text(sensor_access.get_environment_temperature, text_message)
    if app_config_access.display_config.pressure:
        text_message = _get_sensor_reading_text(sensor_access.get_pressure, text_message)
    if app_config_access.display_config.altitude:
        text_message = _get_sensor_reading_text(sensor_access.get_altitude, text_message)
    if app_config_access.display_config.humidity:
        text_message = _get_sensor_reading_text(sensor_access.get_humidity, text_message)
    if app_config_access.display_config.distance:
        text_message = _get_sensor_reading_text(sensor_access.get_distance, text_message)
    if app_config_access.display_config.gas:
        text_message = _get_sensor_reading_text(sensor_access.get_gas, text_message)
    if app_config_access.display_config.particulate_matter:
        text_message = _get_sensor_reading_text(sensor_access.get_particulate_matter, text_message)
    if app_config_access.display_config.lumen:
        text_message = _get_sensor_reading_text(sensor_access.get_lumen, text_message)
    if app_config_access.display_config.color:
        text_message = _get_sensor_reading_text(sensor_access.get_ems_colors, text_message)
    if app_config_access.display_config.ultra_violet:
        text_message = _get_sensor_reading_text(sensor_access.get_ultra_violet, text_message)
    if app_config_access.display_config.accelerometer:
        text_message = _get_sensor_reading_text(sensor_access.get_accelerometer_xyz, text_message)
    if app_config_access.display_config.magnetometer:
        text_message = _get_sensor_reading_text(sensor_access.get_magnetometer_xyz, text_message)
    if app_config_access.display_config.gyroscope:
        text_message = _get_sensor_reading_text(sensor_access.get_gyroscope_xyz, text_message)
    return text_message


def get_graphed_sensors():
    return "Work in Progress"
