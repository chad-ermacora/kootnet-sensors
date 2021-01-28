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
import datetime
from time import sleep
from operations_modules import logger
from operations_modules.app_generic_functions import CreateMonitoredThread
from operations_modules import app_cached_variables
from configuration_modules import app_config_access
from operations_modules import sqlite_database
from sensor_modules import sensor_access

database_variables = app_cached_variables.database_variables


def start_interval_recording_server():
    text_name = "Interval Recording"
    function = _interval_recording
    app_cached_variables.interval_recording_thread = CreateMonitoredThread(function, thread_name=text_name)
    if not app_config_access.interval_recording_config.enable_interval_recording:
        logger.primary_logger.debug("Interval Recording Disabled in the Configuration")
        app_cached_variables.interval_recording_thread.current_state = "Disabled"


def _interval_recording():
    """ Starts recording all sensor readings to the SQL database every X Seconds (set in config). """
    table_interval = database_variables.table_interval
    sleep(5)
    app_cached_variables.interval_recording_thread.current_state = "Disabled"
    while not app_config_access.interval_recording_config.enable_interval_recording:
        sleep(5)
    app_cached_variables.interval_recording_thread.current_state = "Running"
    logger.primary_logger.info(" -- Interval Recording Started")
    app_cached_variables.restart_interval_recording_thread = False
    while not app_cached_variables.restart_interval_recording_thread:
        try:
            new_sensor_data = get_interval_sensor_readings()
            sql_column_names = ""
            sql_value_placeholders = ""
            sql_data = []
            for index, data in new_sensor_data.items():
                sql_column_names += index + ","
                sql_value_placeholders += "?,"
                sql_data.append(str(data))
            sql_column_names = sql_column_names[:-1]
            sql_value_placeholders = sql_value_placeholders[:-1]

            sql_string = "INSERT OR IGNORE INTO " + table_interval + " (" + sql_column_names + ") " + \
                         "VALUES (" + sql_value_placeholders + ")"

            sqlite_database.write_to_sql_database(sql_string, sql_data)
        except Exception as error:
            logger.primary_logger.error("Interval Recording Failure: " + str(error))

        sleep_duration_interval = app_config_access.interval_recording_config.sleep_duration_interval
        sleep_fraction_interval = 1
        if sleep_fraction_interval > sleep_duration_interval:
            sleep_fraction_interval = sleep_duration_interval
        sleep_total = 0
        while sleep_total < sleep_duration_interval and not app_cached_variables.restart_interval_recording_thread:
            sleep(sleep_fraction_interval)
            sleep_total += sleep_fraction_interval


def get_interval_sensor_readings():
    """
    Returns Interval formatted sensor readings based on installed sensors.
    Format = 'CSV String Installed Sensor Types' + special separator + 'CSV String Sensor Readings'
    """
    interval_recording_config = app_config_access.interval_recording_config
    sa = sensor_access
    utc_0_date_time_now = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    return_dictionary = {database_variables.all_tables_datetime: utc_0_date_time_now,
                         database_variables.sensor_name: str(sa.get_hostname()),
                         database_variables.ip: str(sa.get_ip())}

    if interval_recording_config.sensor_uptime_enabled:
        reading = sa.get_uptime_minutes()
        if reading is not None:
            return_dictionary.update({database_variables.sensor_uptime: str(reading)})
    if interval_recording_config.cpu_temperature_enabled:
        return_dictionary = _update_dic_with_sensor_reading(sa.get_cpu_temperature, return_dictionary)
    if interval_recording_config.env_temperature_enabled:
        reading = sa.get_environment_temperature()
        if reading is not None:
            return_dictionary.update(reading)
            reading2 = sa.get_environment_temperature(temperature_correction=False)
            reading = reading[database_variables.env_temperature] - reading2[database_variables.env_temperature]
            return_dictionary.update({database_variables.env_temperature_offset: reading})
    if interval_recording_config.pressure_enabled:
        return_dictionary = _update_dic_with_sensor_reading(sa.get_pressure, return_dictionary)
    if interval_recording_config.altitude_enabled:
        return_dictionary = _update_dic_with_sensor_reading(sa.get_altitude, return_dictionary)
    if interval_recording_config.humidity_enabled:
        return_dictionary = _update_dic_with_sensor_reading(sa.get_humidity, return_dictionary)
    if interval_recording_config.dew_point_enabled:
        return_dictionary = _update_dic_with_sensor_reading(sa.get_dew_point, return_dictionary)
    if interval_recording_config.distance_enabled:
        return_dictionary = _update_dic_with_sensor_reading(sa.get_distance, return_dictionary)
    if interval_recording_config.gas_enabled:
        return_dictionary = _update_dic_with_sensor_reading(sa.get_gas, return_dictionary)
    if interval_recording_config.particulate_matter_enabled:
        return_dictionary = _update_dic_with_sensor_reading(sa.get_particulate_matter, return_dictionary)
    if interval_recording_config.lumen_enabled:
        return_dictionary = _update_dic_with_sensor_reading(sa.get_lumen, return_dictionary)
    if interval_recording_config.colour_enabled:
        return_dictionary = _update_dic_with_sensor_reading(sa.get_ems_colors, return_dictionary)
    if interval_recording_config.ultra_violet_enabled:
        return_dictionary = _update_dic_with_sensor_reading(sa.get_ultra_violet, return_dictionary)
    if interval_recording_config.accelerometer_enabled:
        return_dictionary = _update_dic_with_sensor_reading(sa.get_accelerometer_xyz, return_dictionary)
    if interval_recording_config.magnetometer_enabled:
        return_dictionary = _update_dic_with_sensor_reading(sa.get_magnetometer_xyz, return_dictionary)
    if interval_recording_config.gyroscope_enabled:
        return_dictionary = _update_dic_with_sensor_reading(sa.get_gyroscope_xyz, return_dictionary)
    return return_dictionary


def _update_dic_with_sensor_reading(sensor_function, sensor_dic):
    reading = sensor_function()
    if reading is not None:
        sensor_dic.update(reading)
    return sensor_dic
