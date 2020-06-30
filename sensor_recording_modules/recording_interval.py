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


class CreateHasSensorVariables:
    def __init__(self):
        self._set_all_has_sensor_states(0)
        if sensor_access.get_cpu_temperature() != app_cached_variables.no_sensor_present:
            self.has_cpu_temperature = 1
        if sensor_access.get_sensor_temperature() != app_cached_variables.no_sensor_present:
            self.has_env_temperature = 1
        if sensor_access.get_pressure() != app_cached_variables.no_sensor_present:
            self.has_pressure = 1
        if sensor_access.get_altitude() != app_cached_variables.no_sensor_present:
            self.has_altitude = 1
        if sensor_access.get_humidity() != app_cached_variables.no_sensor_present:
            self.has_humidity = 1
        if sensor_access.get_distance() != app_cached_variables.no_sensor_present:
            self.has_distance = 1
        if sensor_access.get_gas() != app_cached_variables.no_sensor_present:
            self.has_gas = 1

        pm_readings = sensor_access.get_particulate_matter(return_as_dictionary=True)
        if pm_readings[database_variables.particulate_matter_1] != app_cached_variables.no_sensor_present \
                or pm_readings[database_variables.particulate_matter_2_5] != app_cached_variables.no_sensor_present \
                or pm_readings[database_variables.particulate_matter_4] != app_cached_variables.no_sensor_present \
                or pm_readings[database_variables.particulate_matter_10] != app_cached_variables.no_sensor_present:
            self.has_particulate_matter = 1
        if sensor_access.get_ultra_violet() != app_cached_variables.no_sensor_present:
            self.has_ultra_violet = 1
        if sensor_access.get_lumen() != app_cached_variables.no_sensor_present:
            self.has_lumen = 1
        if sensor_access.get_ems_colors() != app_cached_variables.no_sensor_present:
            self.has_color = 1
        if sensor_access.get_accelerometer_xyz() != app_cached_variables.no_sensor_present:
            self.has_acc = 1
        if sensor_access.get_magnetometer_xyz() != app_cached_variables.no_sensor_present:
            self.has_mag = 1
        if sensor_access.get_gyroscope_xyz() != app_cached_variables.no_sensor_present:
            self.has_gyro = 1

    # TODO: Break up multi-sensors like PM & GAS as started below
    def _set_all_has_sensor_states(self, set_sensor_state_as):
        self.has_cpu_temperature = set_sensor_state_as
        self.has_env_temperature = set_sensor_state_as
        self.has_pressure = set_sensor_state_as
        self.has_altitude = set_sensor_state_as
        self.has_humidity = set_sensor_state_as
        self.has_distance = set_sensor_state_as
        self.has_gas = set_sensor_state_as
        self.has_particulate_matter = set_sensor_state_as
        self.has_ultra_violet = set_sensor_state_as
        self.has_lumen = set_sensor_state_as
        self.has_color = set_sensor_state_as
        self.has_acc = set_sensor_state_as
        self.has_mag = set_sensor_state_as
        self.has_gyro = set_sensor_state_as


def start_interval_recording_server():
    if app_config_access.interval_recording_config.enable_interval_recording:
        text_name = "Interval Recording"
        function = _interval_recording
        app_cached_variables.interval_recording_thread = CreateMonitoredThread(function, thread_name=text_name)
    else:
        logger.primary_logger.debug("Interval Recording Disabled in the Configuration")


def _interval_recording():
    """ Starts recording all sensor readings to the SQL database every X Seconds (set in config). """
    logger.primary_logger.info(" -- Interval Recording Started")
    app_cached_variables.restart_interval_recording_thread = False
    while not app_cached_variables.restart_interval_recording_thread:
        try:
            new_sensor_data = get_interval_sensor_readings()
            sql_string = "INSERT OR IGNORE INTO IntervalData (" + new_sensor_data[0] + ") VALUES ("
            sql_data = []
            for entry in new_sensor_data[1]:
                sql_string += "?,"
                sql_data.append(str(entry))
            sql_string = sql_string[:-1] + ")"
            sqlite_database.write_to_sql_database(sql_string, sql_data)
        except Exception as error:
            logger.primary_logger.error("Interval Recording Failure: " + str(error))

        sleep_duration_interval = app_config_access.interval_recording_config.sleep_duration_interval
        sleep_fraction_interval = 5
        sleep_total = 0
        while sleep_total < sleep_duration_interval and not app_cached_variables.restart_interval_recording_thread:
            sleep(sleep_fraction_interval)
            sleep_total += sleep_fraction_interval


def get_interval_sensor_readings():
    """
    Returns Interval formatted sensor readings based on installed sensors.
    Format = 'CSV String Installed Sensor Types' + special separator + 'CSV String Sensor Readings'
    """
    sensor_types = [app_cached_variables.database_variables.all_tables_datetime]
    sensor_readings = [datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]]
    if app_config_access.installed_sensors.linux_system:
        sensor_types += [app_cached_variables.database_variables.sensor_name,
                         app_cached_variables.database_variables.ip,
                         app_cached_variables.database_variables.sensor_uptime]
        sensor_readings += [sensor_access.get_hostname(),
                            sensor_access.get_ip(),
                            sensor_access.get_uptime_minutes()]
    if available_sensors.has_cpu_temperature:
        sensor_types.append(app_cached_variables.database_variables.system_temperature)
        sensor_readings.append(sensor_access.get_cpu_temperature())
    if available_sensors.has_env_temperature:
        sensor_types.append(app_cached_variables.database_variables.env_temperature)
        sensor_types.append(app_cached_variables.database_variables.env_temperature_offset)
        sensor_readings.append(sensor_access.get_sensor_temperature())
        if app_config_access.primary_config.enable_custom_temp or \
                app_config_access.primary_config.enable_temperature_comp_factor:
            sensor_readings.append(sensor_access.get_temperature_correction())
        else:
            sensor_readings.append("0.0")
    if available_sensors.has_pressure:
        sensor_types.append(app_cached_variables.database_variables.pressure)
        sensor_readings.append(sensor_access.get_pressure())
    if available_sensors.has_altitude:
        sensor_types.append(app_cached_variables.database_variables.altitude)
        sensor_readings.append(sensor_access.get_altitude())
    if available_sensors.has_humidity:
        sensor_types.append(app_cached_variables.database_variables.humidity)
        sensor_readings.append(sensor_access.get_humidity())
    if available_sensors.has_distance:
        sensor_types.append(app_cached_variables.database_variables.distance)
        sensor_readings.append(sensor_access.get_distance())
    if available_sensors.has_gas:
        gas_readings = sensor_access.get_gas(return_as_dictionary=True)
        for text_name, item_value in gas_readings.items():
            if item_value != app_cached_variables.no_sensor_present:
                sensor_types.append(text_name)
                sensor_readings.append(item_value)
    if available_sensors.has_particulate_matter:
        pm_readings = sensor_access.get_particulate_matter(return_as_dictionary=True)
        for text_name, item_value in pm_readings.items():
            if item_value != app_cached_variables.no_sensor_present:
                sensor_types.append(text_name)
                sensor_readings.append(item_value)
    if available_sensors.has_lumen:
        sensor_types.append(app_cached_variables.database_variables.lumen)
        sensor_readings.append(sensor_access.get_lumen())
    if available_sensors.has_color:
        ems_colours = sensor_access.get_ems_colors(return_as_dictionary=True)
        for text_name, item_value in ems_colours.items():
            if item_value != app_cached_variables.no_sensor_present:
                sensor_types.append(text_name)
                sensor_readings.append(item_value)
    if available_sensors.has_ultra_violet:
        uv_reading = sensor_access.get_ultra_violet(return_as_dictionary=True)
        for text_name, item_value in uv_reading.items():
            if item_value != app_cached_variables.no_sensor_present:
                sensor_types.append(text_name)
                sensor_readings.append(item_value)
    if available_sensors.has_acc:
        accelerometer_readings = sensor_access.get_accelerometer_xyz()

        sensor_types += [app_cached_variables.database_variables.acc_x,
                         app_cached_variables.database_variables.acc_y,
                         app_cached_variables.database_variables.acc_z]
        sensor_readings += [accelerometer_readings[0],
                            accelerometer_readings[1],
                            accelerometer_readings[2]]
    if available_sensors.has_mag:
        magnetometer_readings = sensor_access.get_magnetometer_xyz()

        sensor_types += [app_cached_variables.database_variables.mag_x,
                         app_cached_variables.database_variables.mag_y,
                         app_cached_variables.database_variables.mag_z]
        sensor_readings += [magnetometer_readings[0],
                            magnetometer_readings[1],
                            magnetometer_readings[2]]
    if available_sensors.has_gyro:
        gyroscope_readings = sensor_access.get_gyroscope_xyz()

        sensor_types += [app_cached_variables.database_variables.gyro_x,
                         app_cached_variables.database_variables.gyro_y,
                         app_cached_variables.database_variables.gyro_z]
        sensor_readings += [gyroscope_readings[0],
                            gyroscope_readings[1],
                            gyroscope_readings[2]]

    return_interval_data = [_list_to_csv_string(sensor_types), sensor_readings]
    return return_interval_data


def _list_to_csv_string(list_to_add):
    if len(list_to_add) > 0:
        text_string = ""
        for entry in list_to_add:
            text_string += str(entry) + ","
        return text_string[:-1]
    return ""


def _list_to_csv_string_quoted(list_to_add):
    if len(list_to_add) > 0:
        text_string = ""
        for entry in list_to_add:
            text_string += "'" + str(entry) + "',"
        return text_string[:-1]
    return ""


available_sensors = CreateHasSensorVariables()
