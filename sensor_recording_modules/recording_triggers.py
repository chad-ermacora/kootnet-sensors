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
from datetime import datetime
from operations_modules import logger
from operations_modules.app_generic_functions import thread_function, CreateMonitoredThread
from configuration_modules import app_config_access
from operations_modules.app_cached_variables import database_variables
from operations_modules import app_cached_variables
from operations_modules.sqlite_database import write_to_sql_database
from sensor_modules import sensor_access
from sensor_recording_modules.recording_interval import available_sensors

installed_sensors = app_config_access.installed_sensors
trigger_variances = app_config_access.trigger_variances


class StartTriggerVariance:
    def __init__(self, get_sensor_readings, sql_column_name_list, sleep_time, variances_list):
        self.readings_per_sensor_get = len(sql_column_name_list)
        sleep_fraction_interval = 1
        if sleep_fraction_interval > sleep_time:
            sleep_fraction_interval = sleep_time

        while not app_cached_variables.restart_all_trigger_threads:
            readings1 = get_sensor_readings()
            datetime_stamp1 = get_datetime_stamp()
            sleep_total = 0
            while sleep_total < sleep_time and not app_cached_variables.restart_all_trigger_threads:
                sleep(sleep_fraction_interval)
                sleep_total += sleep_fraction_interval
            readings2 = get_sensor_readings()
            datetime_stamp2 = get_datetime_stamp()
            if self.readings_per_sensor_get == 1:
                if abs(readings2 - readings1) > variances_list[0]:
                    self.record_trigger(readings1, sql_column_name_list[0], datetime_stamp1)
                    self.record_trigger(readings2, sql_column_name_list[0], datetime_stamp2)
            else:
                for reading1, reading2, variance, sql_column_name in zip(
                        readings1, readings2, variances_list, sql_column_name_list
                ):
                    if abs(reading1 - reading2) > variance:
                        self.record_trigger(reading1, sql_column_name, datetime_stamp1)
                        self.record_trigger(reading2, sql_column_name, datetime_stamp2)

    @staticmethod
    def record_trigger(reading, sql_column_name, datetime_stamp):
        sql_query = "INSERT OR IGNORE INTO TriggerData ("

        sql_data_list = [datetime_stamp]
        if installed_sensors.linux_system:
            sql_query += "DateTime,SensorName,IP," + sql_column_name + ") VALUES ("
            sql_data_list.append(sensor_access.get_hostname())
            sql_data_list.append(sensor_access.get_ip())
        else:
            sql_query += "DateTime," + sql_column_name + ") VALUES ("

        sql_data_list.append(str(reading))

        for _ in range(len(sql_data_list)):
            sql_query += "?,"
        sql_query = sql_query[:-1] + ");"

        write_to_sql_database(sql_query, sql_data_list)


def start_trigger_variance_recording_server():
    if trigger_variances.enable_trigger_variance:
        thread_function(_trigger_variance_recording)
    else:
        logger.primary_logger.debug("Trigger Variance Recording Disabled in Configuration")


def _trigger_variance_recording():
    """ Starts recording all enabled sensors to the SQL database based on set trigger variances (set in config). """
    logger.primary_logger.debug("Trigger Thread(s) Starting")
    if trigger_variances.cpu_temperature_enabled and available_sensors.has_cpu_temperature:
        sensor_get_function = sensor_access.get_cpu_temperature
        sql_column_name_list = [database_variables.system_temperature]
        sleep_time = trigger_variances.cpu_temperature_wait_seconds
        variances_list = [trigger_variances.cpu_temperature_variance]
        app_cached_variables.trigger_variance_thread_cpu_temp = CreateMonitoredThread(
            StartTriggerVariance, thread_name="CPU Temperature Trigger Variance",
            args=(sensor_get_function, sql_column_name_list, sleep_time, variances_list)
        )
    if trigger_variances.env_temperature_enabled and available_sensors.has_env_temperature:
        sensor_get_function = sensor_access.get_sensor_temperature
        sql_column_name_list = [database_variables.env_temperature]
        sleep_time = trigger_variances.env_temperature_wait_seconds
        variances_list = [trigger_variances.env_temperature_variance]
        app_cached_variables.trigger_variance_thread_env_temp = CreateMonitoredThread(
            StartTriggerVariance, thread_name="Environmental Temperature Trigger Variance",
            args=(sensor_get_function, sql_column_name_list, sleep_time, variances_list)
        )
    if trigger_variances.pressure_enabled and available_sensors.has_pressure:
        sensor_get_function = sensor_access.get_pressure
        sql_column_name_list = [database_variables.pressure]
        sleep_time = trigger_variances.pressure_wait_seconds
        variances_list = [trigger_variances.pressure_variance]
        app_cached_variables.trigger_variance_thread_pressure = CreateMonitoredThread(
            StartTriggerVariance, thread_name="Pressure Trigger Variance",
            args=(sensor_get_function, sql_column_name_list, sleep_time, variances_list)
        )
    if trigger_variances.altitude_enabled and available_sensors.has_altitude:
        sensor_get_function = sensor_access.get_altitude
        sql_column_name_list = [database_variables.altitude]
        sleep_time = trigger_variances.altitude_wait_seconds
        variances_list = [trigger_variances.altitude_variance]
        app_cached_variables.trigger_variance_thread_altitude = CreateMonitoredThread(
            StartTriggerVariance, thread_name="Altitude Trigger Variance",
            args=(sensor_get_function, sql_column_name_list, sleep_time, variances_list)
        )
    if trigger_variances.humidity_enabled and available_sensors.has_humidity:
        sensor_get_function = sensor_access.get_humidity
        sql_column_name_list = [database_variables.humidity]
        sleep_time = trigger_variances.humidity_wait_seconds
        variances_list = [trigger_variances.humidity_variance]
        app_cached_variables.trigger_variance_thread_humidity = CreateMonitoredThread(
            StartTriggerVariance, thread_name="Humidity Trigger Variance",
            args=(sensor_get_function, sql_column_name_list, sleep_time, variances_list)
        )
    if trigger_variances.distance_enabled and available_sensors.has_distance:
        sensor_get_function = sensor_access.get_distance
        sql_column_name_list = [database_variables.distance]
        sleep_time = trigger_variances.distance_wait_seconds
        variances_list = [trigger_variances.distance_variance]
        app_cached_variables.trigger_variance_thread_distance = CreateMonitoredThread(
            StartTriggerVariance, thread_name="Distance Trigger Variance",
            args=(sensor_get_function, sql_column_name_list, sleep_time, variances_list)
        )
    if trigger_variances.gas_enabled and available_sensors.has_gas:
        sensor_get_function = sensor_access.get_gas
        readings_test = sensor_get_function(return_as_dictionary=True)
        sql_column_name_list = []
        variances_list = []
        for key, value in readings_test.items():
            sql_column_name_list.append(key)
            if key == database_variables.gas_resistance_index:
                variances_list.append(trigger_variances.gas_resistance_index_variance)
            elif key == database_variables.gas_oxidising:
                variances_list.append(trigger_variances.gas_oxidising_variance)
            elif key == database_variables.gas_reducing:
                variances_list.append(trigger_variances.gas_reducing_variance)
            elif key == database_variables.gas_nh3:
                variances_list.append(trigger_variances.gas_nh3_variance)
        sleep_time = trigger_variances.gas_wait_seconds
        app_cached_variables.trigger_variance_thread_gas = CreateMonitoredThread(
            StartTriggerVariance, thread_name="GAS Trigger Variance",
            args=(sensor_get_function, sql_column_name_list, sleep_time, variances_list)
        )
    if trigger_variances.particulate_matter_enabled and available_sensors.has_particulate_matter:
        sensor_get_function = sensor_access.get_particulate_matter

        readings_test = sensor_get_function(return_as_dictionary=True)
        sql_column_name_list = []
        variances_list = []
        for key, value in readings_test.items():
            if value != app_cached_variables.no_sensor_present:
                sql_column_name_list.append(key)
                if key == database_variables.particulate_matter_1:
                    variances_list.append(trigger_variances.particulate_matter_1_variance)
                elif key == database_variables.particulate_matter_2_5:
                    variances_list.append(trigger_variances.particulate_matter_2_5_variance)
                elif key == database_variables.particulate_matter_4:
                    variances_list.append(trigger_variances.particulate_matter_4_variance)
                elif key == database_variables.particulate_matter_10:
                    variances_list.append(trigger_variances.particulate_matter_10_variance)

        sleep_time = trigger_variances.particulate_matter_wait_seconds
        app_cached_variables.trigger_variance_thread_particulate_matter = CreateMonitoredThread(
            StartTriggerVariance, thread_name="Particulate Matter Trigger Variance",
            args=(sensor_get_function, sql_column_name_list, sleep_time, variances_list)
        )
    if trigger_variances.lumen_enabled and available_sensors.has_lumen:
        sensor_get_function = sensor_access.get_lumen
        sql_column_name_list = [database_variables.lumen]
        sleep_time = trigger_variances.lumen_wait_seconds
        variances_list = [trigger_variances.lumen_variance]
        app_cached_variables.trigger_variance_thread_lumen = CreateMonitoredThread(
            StartTriggerVariance, thread_name="Lumen Trigger Variance",
            args=(sensor_get_function, sql_column_name_list, sleep_time, variances_list)
        )
    if trigger_variances.colour_enabled and available_sensors.has_color:
        sensor_get_function = sensor_access.get_ems_colors
        sql_column_name_list = [
            database_variables.red, database_variables.green, database_variables.blue
        ]
        sleep_time = trigger_variances.colour_wait_seconds
        variances_list = [
            trigger_variances.red_variance, trigger_variances.green_variance, trigger_variances.blue_variance
        ]

        if installed_sensors.pimoroni_as7262 or installed_sensors.kootnet_dummy_sensor:
            sql_column_name_list = [
                database_variables.red, database_variables.orange, database_variables.yellow,
                database_variables.green, database_variables.blue, database_variables.violet
            ]
            variances_list = [
                trigger_variances.red_variance, trigger_variances.orange_variance, trigger_variances.yellow_variance,
                trigger_variances.green_variance, trigger_variances.blue_variance, trigger_variances.violet_variance
            ]

        app_cached_variables.trigger_variance_thread_visible_ems = CreateMonitoredThread(
            StartTriggerVariance, thread_name="EMS Colours Trigger Variance",
            args=(sensor_get_function, sql_column_name_list, sleep_time, variances_list)
        )
    if trigger_variances.ultra_violet_enabled and available_sensors.has_ultra_violet:
        sensor_get_function = sensor_access.get_ultra_violet
        sql_column_name_list = [database_variables.ultra_violet_a, database_variables.ultra_violet_b]
        sleep_time = trigger_variances.ultra_violet_wait_seconds
        variances_list = [trigger_variances.ultra_violet_a_variance, trigger_variances.ultra_violet_b_variance]
        app_cached_variables.trigger_variance_thread_ultra_violet = CreateMonitoredThread(
            StartTriggerVariance, thread_name="Ultra Violet Trigger Variance",
            args=(sensor_get_function, sql_column_name_list, sleep_time, variances_list)
        )
    if trigger_variances.accelerometer_enabled and available_sensors.has_acc:
        sensor_get_function = sensor_access.get_accelerometer_xyz
        sql_column_name_list = [
            database_variables.acc_x, database_variables.acc_y, database_variables.acc_z
        ]
        sleep_time = trigger_variances.accelerometer_wait_seconds
        variances_list = [
            trigger_variances.accelerometer_x_variance,
            trigger_variances.accelerometer_y_variance,
            trigger_variances.accelerometer_z_variance
        ]
        app_cached_variables.trigger_variance_thread_accelerometer = CreateMonitoredThread(
            StartTriggerVariance, thread_name="Accelerometer Trigger Variance",
            args=(sensor_get_function, sql_column_name_list, sleep_time, variances_list)
        )
    if trigger_variances.magnetometer_enabled and available_sensors.has_mag:
        sensor_get_function = sensor_access.get_magnetometer_xyz
        sql_column_name_list = [
            database_variables.mag_x, database_variables.mag_y, database_variables.mag_z
        ]
        sleep_time = trigger_variances.magnetometer_wait_seconds
        variances_list = [
            trigger_variances.magnetometer_x_variance,
            trigger_variances.magnetometer_y_variance,
            trigger_variances.magnetometer_z_variance
        ]
        app_cached_variables.trigger_variance_thread_magnetometer = CreateMonitoredThread(
            StartTriggerVariance, thread_name="Magnetometer Trigger Variance",
            args=(sensor_get_function, sql_column_name_list, sleep_time, variances_list)
        )
    if trigger_variances.gyroscope_enabled and available_sensors.has_gyro:
        sensor_get_function = sensor_access.get_gyroscope_xyz
        sql_column_name_list = [
            database_variables.gyro_x, database_variables.gyro_y, database_variables.gyro_z
        ]
        sleep_time = trigger_variances.gyroscope_wait_seconds
        variances_list = [
            trigger_variances.gyroscope_x_variance,
            trigger_variances.gyroscope_y_variance,
            trigger_variances.gyroscope_z_variance
        ]
        app_cached_variables.trigger_variance_thread_gyroscope = CreateMonitoredThread(
            StartTriggerVariance, thread_name="Gyroscope Trigger Variance",
            args=(sensor_get_function, sql_column_name_list, sleep_time, variances_list)
        )


def get_datetime_stamp():
    """ Returns current UTC 0 time as a string "%Y-%m-%d %H:%M:%S.%f" (%f to 3 decimal places). """
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
