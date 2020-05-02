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
from operations_modules import app_cached_variables
from operations_modules import app_config_access
from sensor_modules import sensor_access

display_variables = app_cached_variables.CreateDisplaySensorsVariables()


def scroll_interval_readings_on_display():
    logger.primary_logger.info(" -- Sensor Display Server Started")
    while True:
        if app_config_access.display_config.display_type == display_variables.display_type_numerical:
            sensor_access.display_message(get_numerical_display_text())
        else:
            sensor_access.display_message(get_graphed_sensors())
        sleep(app_config_access.display_config.minutes_between_display)


# TODO: Set multi sensor
# TODO: Add sensor check
def get_numerical_display_text():
    text_message = ""

    if display_variables.sensor_uptime in app_config_access.display_config.sensors_to_display:
        text_message += "Uptime: " + str(sensor_access.get_uptime_minutes())
    if display_variables.system_temperature in app_config_access.display_config.sensors_to_display:
        text_message += "CPU Temp: " + str(sensor_access.get_cpu_temperature())
    if display_variables.env_temperature in app_config_access.display_config.sensors_to_display:
        text_message += "Env Temp: " + str(sensor_access.get_sensor_temperature())
    if display_variables.pressure in app_config_access.display_config.sensors_to_display:
        text_message += "Pressure: " + str(sensor_access.get_pressure())
    if display_variables.altitude in app_config_access.display_config.sensors_to_display:
        text_message += "Altitude: " + str(sensor_access.get_altitude())
    if display_variables.humidity in app_config_access.display_config.sensors_to_display:
        text_message += "Humidity: " + str(sensor_access.get_humidity())
    if display_variables.distance in app_config_access.display_config.sensors_to_display:
        text_message += "Distance: " + str(sensor_access.get_distance())
    if display_variables.gas in app_config_access.display_config.sensors_to_display:
        text_message += "GAS: " + str(sensor_access.get_gas_resistance_index())
    if display_variables.particulate_matter in app_config_access.display_config.sensors_to_display:
        text_message += "PM: " + str(sensor_access.get_particulate_matter_1())
    if display_variables.lumen in app_config_access.display_config.sensors_to_display:
        text_message += "Lumen: " + str(sensor_access.get_lumen())
    if display_variables.color in app_config_access.display_config.sensors_to_display:
        text_message += "Color: " + str(sensor_access.get_ems())
    if display_variables.ultra_violet in app_config_access.display_config.sensors_to_display:
        text_message += "UV: " + str(sensor_access.get_ultra_violet_index())
    if display_variables.accelerometer in app_config_access.display_config.sensors_to_display:
        text_message += "Acc: " + str(sensor_access.get_accelerometer_xyz())
    if display_variables.magnetometer in app_config_access.display_config.sensors_to_display:
        text_message += "Mag: " + str(sensor_access.get_magnetometer_xyz())
    if display_variables.gyroscope in app_config_access.display_config.sensors_to_display:
        text_message += "Gyro: " + str(sensor_access.get_gyroscope_xyz())
    return text_message


def get_graphed_sensors():
    return "Work in Progress"
