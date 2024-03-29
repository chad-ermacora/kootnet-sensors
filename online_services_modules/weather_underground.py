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
import requests
from time import sleep
from operations_modules import logger
from operations_modules import software_version
from operations_modules import app_cached_variables
from operations_modules.app_generic_classes import CreateMonitoredThread
from configuration_modules.app_config_access import weather_underground_config
from sensor_modules import sensor_access


database_variables = app_cached_variables.database_variables


def start_weather_underground_server():
    if weather_underground_config.weather_underground_enabled:
        text_name = "Weather Underground"
        function = _weather_underground_server
        app_cached_variables.weather_underground_thread = CreateMonitoredThread(function, thread_name=text_name)
    else:
        logger.primary_logger.debug("Weather Underground Disabled in Configuration")


def _weather_underground_server():
    """ Sends compatible sensor readings to Weather Underground every X seconds based on set Interval. """
    app_cached_variables.restart_weather_underground_thread = False
    interval_seconds = weather_underground_config.interval_seconds
    while not app_cached_variables.restart_weather_underground_thread:
        try:
            sensor_readings = get_weather_underground_readings()
            sw_version_text_list = software_version.version.split(".")
            sw_version_text = str(sw_version_text_list[0]) + "." + str(sw_version_text_list[1])
            if sensor_readings:
                if interval_seconds < 10:
                    url = weather_underground_config.wu_rapid_fire_url_start
                else:
                    url = weather_underground_config.wu_main_url_start

                url += weather_underground_config.wu_id + weather_underground_config.station_id + \
                       weather_underground_config.wu_key + weather_underground_config.station_key + \
                       weather_underground_config.wu_utc_datetime + \
                       sensor_readings + \
                       weather_underground_config.wu_software_version + sw_version_text + \
                       weather_underground_config.wu_action

                if interval_seconds < 10:
                    url += weather_underground_config.wu_rapid_fire_url_end + str(interval_seconds)

                html_get_response = requests.get(url=url)

                if html_get_response.status_code == 200:
                    logger.network_logger.debug("Sensors sent to Weather Underground OK")
                elif html_get_response.status_code == 401:
                    logger.network_logger.error("Weather Underground: Bad Station ID or Key")
                elif html_get_response.status_code == 400:
                    logger.network_logger.error("Weather Underground: Invalid Options")
                else:
                    status_code = str(html_get_response.status_code)
                    response_text = str(html_get_response.text)
                    log_msg = "Weather Underground - Unknown Error " + status_code + ": " + response_text
                    logger.network_logger.error(log_msg)
            else:
                log_msg = "Weather Underground - No Compatible Sensors: No further attempts will be made"
                logger.primary_logger.error(log_msg)
                while not app_cached_variables.restart_weather_underground_thread:
                    sleep(5)
        except Exception as error:
            logger.network_logger.error("Weather Underground - Error sending data")
            logger.network_logger.debug("Weather Underground - Detailed Error: " + str(error))

        sleep_fraction_interval = 5
        sleep_total = 0
        while sleep_total < interval_seconds and not app_cached_variables.restart_weather_underground_thread:
            sleep(sleep_fraction_interval)
            sleep_total += sleep_fraction_interval


def get_weather_underground_readings():
    """
    Returns supported sensor readings for Weather Underground in URL format.
    Example:  &tempf=59.56&humidity=15.65
    """
    round_decimal_to = 5
    return_readings_str = ""

    temp_c = sensor_access.get_environment_temperature()
    if temp_c is not None:
        temp_c = temp_c[database_variables.env_temperature]
        try:
            temperature_f = (float(temp_c) * (9.0 / 5.0)) + 32.0
            if weather_underground_config.outdoor_sensor:
                return_readings_str += "&tempf=" + str(round(temperature_f, round_decimal_to))
            else:
                return_readings_str += "&indoortempf=" + str(round(temperature_f, round_decimal_to))
        except Exception as error:
            log_msg = "Weather Underground - Unable to calculate Temperature into fahrenheit: " + str(error)
            logger.sensors_logger.error(log_msg)

    humidity = sensor_access.get_humidity()
    if humidity is not None:
        humidity = humidity[database_variables.humidity]
        if weather_underground_config.outdoor_sensor:
            return_readings_str += "&humidity=" + str(round(humidity, round_decimal_to))
        else:
            return_readings_str += "&indoorhumidity=" + str(round(humidity, round_decimal_to))

    out_door_dew_point = sensor_access.get_dew_point()
    if out_door_dew_point is not None and weather_underground_config.outdoor_sensor:
        out_door_dew_point = out_door_dew_point[database_variables.dew_point]
        try:
            dew_point_f = (float(out_door_dew_point) * (9.0 / 5.0)) + 32.0
            return_readings_str += "&dewptf=" + str(round(dew_point_f, round_decimal_to))
        except Exception as error:
            log_msg = "Weather Underground - Unable to calculate Dew Point into fahrenheit: " + str(error)
            logger.sensors_logger.error(log_msg)

    pressure_hpa = sensor_access.get_pressure()
    if pressure_hpa is not None:
        pressure_hpa = pressure_hpa[database_variables.pressure]
        try:
            baromin = float(pressure_hpa) * 0.029529983071445
            return_readings_str += "&baromin=" + str(round(baromin, round_decimal_to))
        except Exception as error:
            logger.sensors_logger.error("Weather Underground - Unable to calculate Pressure into Hg: " + str(error))

    ultra_violet = sensor_access.get_ultra_violet()
    if ultra_violet is not None:
        if database_variables.ultra_violet_index in ultra_violet:
            uv_index = ultra_violet[database_variables.ultra_violet_index]
            return_readings_str += "&UV=" + str(round(uv_index, round_decimal_to))

    pm_readings = sensor_access.get_particulate_matter()
    if pm_readings is not None:
        if database_variables.particulate_matter_2_5 in pm_readings:
            pm_2_5 = pm_readings[database_variables.particulate_matter_2_5]
            return_readings_str += "&AqPM2.5=" + str(round(pm_2_5, round_decimal_to))
        if database_variables.particulate_matter_10 in pm_readings:
            pm_10 = pm_readings[database_variables.particulate_matter_10]
            return_readings_str += "&AqPM10=" + str(round(pm_10, round_decimal_to))
    return return_readings_str
