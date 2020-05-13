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


def scroll_interval_readings_on_display():
    if sensor_access.display_message("KS init: " + get_numerical_display_text()):
        logger.primary_logger.info(" -- Sensor Display Server Started")
        while True:
            sleep(app_config_access.display_config.minutes_between_display * 60)
            display_type_numerical = app_config_access.display_config.display_type_numerical
            if app_config_access.display_config.display_type == display_type_numerical:
                sensor_access.display_message(get_numerical_display_text())
            else:
                sensor_access.display_message(get_graphed_sensors())
    else:
        logger.primary_logger.error(" -- Sensor Display Server Failed to Start: No Compatible Display Found")


def get_numerical_display_text():
    text_message = ""

    if app_config_access.display_config.sensor_uptime:
        text_message += "Uptime: " + str(sensor_access.get_uptime_minutes())
    if app_config_access.display_config.system_temperature:
        text_message += " CPU Temp: " + str(sensor_access.get_cpu_temperature())
    if app_config_access.display_config.env_temperature:
        text_message += " Env Temp: " + str(sensor_access.get_sensor_temperature())
    if app_config_access.display_config.pressure:
        text_message += " Pressure: " + str(sensor_access.get_pressure())
    if app_config_access.display_config.altitude:
        text_message += " Altitude: " + str(sensor_access.get_altitude())
    if app_config_access.display_config.humidity:
        text_message += " Humidity: " + str(sensor_access.get_humidity())
    if app_config_access.display_config.distance:
        text_message += " Distance: " + str(sensor_access.get_distance())
    if app_config_access.display_config.gas:
        gas_readings = sensor_access.get_gas(return_as_dictionary=True)
        for text_name, item_value in gas_readings.items():
            if text_name == app_cached_variables.database_variables.gas_resistance_index:
                text_name = " Gas Index:"
            elif text_name == app_cached_variables.database_variables.gas_oxidising:
                text_name = " Gas Ox:"
            elif text_name == app_cached_variables.database_variables.gas_reducing:
                text_name = " Gas Re:"
            elif text_name == app_cached_variables.database_variables.gas_nh3:
                text_name = " Gas NH3:"
            text_message += str(text_name) + str(item_value)
    if app_config_access.display_config.particulate_matter:
        pm_readings = sensor_access.get_particulate_matter(return_as_dictionary=True)
        for text_name, item_value in pm_readings.items():
            if text_name == app_cached_variables.database_variables.particulate_matter_1:
                text_name = " PM1:"
            elif text_name == app_cached_variables.database_variables.particulate_matter_2_5:
                text_name = " PM2:"
            elif text_name == app_cached_variables.database_variables.particulate_matter_10:
                text_name = " PM10:"
            text_message += str(text_name) + str(item_value)
    if app_config_access.display_config.lumen:
        text_message += " Lumen: " + str(sensor_access.get_lumen())
    if app_config_access.display_config.color:
        ems_color_readings = sensor_access.get_ems_colors(return_as_dictionary=True)
        for text_name, item_value in ems_color_readings.items():
            text_message += " " + str(text_name) + ": " + str(item_value)
    if app_config_access.display_config.ultra_violet:
        uv_readings = sensor_access.get_ultra_violet(return_as_dictionary=True)
        for text_name, item_value in uv_readings.items():
            if text_name == app_cached_variables.database_variables.ultra_violet_index:
                text_name = " UV Index:"
            elif text_name == app_cached_variables.database_variables.ultra_violet_a:
                text_name = " UVA:"
            elif text_name == app_cached_variables.database_variables.ultra_violet_b:
                text_name = " UVB:"
            text_message += str(text_name) + str(item_value)
    if app_config_access.display_config.accelerometer:
        xzy = sensor_access.get_accelerometer_xyz()
        text_message += " |Acc X:" + str(xzy[0]) + " Y:" + str(xzy[1]) + " Z:" + str(str(xzy[2]))
    if app_config_access.display_config.magnetometer:
        xzy = sensor_access.get_magnetometer_xyz()
        text_message += " |Mag X:" + str(xzy[0]) + " Y:" + str(xzy[1]) + " Z:" + str(str(xzy[2]))
    if app_config_access.display_config.gyroscope:
        xzy = sensor_access.get_gyroscope_xyz()
        text_message += " |Gyro X:" + str(xzy[0]) + " Y:" + str(xzy[1]) + " Z:" + str(str(xzy[2]))
    return text_message


def get_graphed_sensors():
    return "Work in Progress"
