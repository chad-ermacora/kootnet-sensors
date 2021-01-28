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

installed_sensors = app_config_access.installed_sensors
trigger_variances = app_config_access.trigger_variances


class StartTriggerVariance:
    def __init__(self, get_sensor_readings, sql_column_name_list, sleep_time, variances_list):
        self.readings_per_sensor_get = len(sql_column_name_list)
        sleep_fraction_interval = 1
        if sleep_fraction_interval > sleep_time:
            sleep_fraction_interval = sleep_time
        if get_sensor_readings() is not None:
            while not app_cached_variables.restart_all_trigger_threads:
                try:
                    readings1 = get_sensor_readings()
                    datetime_stamp1 = get_datetime_stamp()
                    sleep_total = 0
                    while sleep_total < sleep_time and not app_cached_variables.restart_all_trigger_threads:
                        sleep(sleep_fraction_interval)
                        sleep_total += sleep_fraction_interval
                    readings2 = get_sensor_readings()
                    datetime_stamp2 = get_datetime_stamp()
                    if self.readings_per_sensor_get == 1:
                        readings1 = readings1[sql_column_name_list[0]]
                        readings2 = readings2[sql_column_name_list[0]]
                        if abs(readings2 - readings1) > variances_list[0]:
                            self.record_trigger(readings1, sql_column_name_list[0], datetime_stamp1)
                            self.record_trigger(readings2, sql_column_name_list[0], datetime_stamp2)
                    else:
                        for reading_db_name, reading in readings1.items():
                            index = 0
                            db_col = reading_db_name
                            column_found = False
                            for i, column in enumerate(sql_column_name_list):
                                if column == reading_db_name:
                                    column_found = True
                                    index = i
                                    db_col = column
                            if column_found:
                                readings_cur_1 = readings1[db_col]
                                readings_cur_2 = readings2[db_col]
                                variance = variances_list[index]
                                if abs(readings_cur_1 - readings_cur_2) > variance:
                                    self.record_trigger(readings_cur_1, db_col, datetime_stamp1)
                                    self.record_trigger(readings_cur_2, db_col, datetime_stamp2)
                except Exception as error:
                    log_msg = "Trigger Variance Recording Error in " + str(sql_column_name_list)
                    logger.primary_logger.error(log_msg + ": " + str(error))
                    sleep(60)
        else:
            logger.primary_logger.warning("Triggers: " + str(sql_column_name_list) + ": Sensor Missing")
            while not app_cached_variables.restart_all_trigger_threads:
                sleep(10)

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
    if trigger_variances.cpu_temperature_enabled:
        sensor_get_function = sensor_access.get_cpu_temperature
        sql_column_name_list = [database_variables.system_temperature]
        sleep_time = trigger_variances.cpu_temperature_wait_seconds
        variances_list = [trigger_variances.cpu_temperature_variance]
        app_cached_variables.trigger_variance_thread_cpu_temp = CreateMonitoredThread(
            StartTriggerVariance, thread_name="CPU Temperature Trigger Variance",
            args=(sensor_get_function, sql_column_name_list, sleep_time, variances_list)
        )
    if trigger_variances.env_temperature_enabled:
        sensor_get_function = sensor_access.get_environment_temperature
        sql_column_name_list = [database_variables.env_temperature]
        sleep_time = trigger_variances.env_temperature_wait_seconds
        variances_list = [trigger_variances.env_temperature_variance]
        app_cached_variables.trigger_variance_thread_env_temp = CreateMonitoredThread(
            StartTriggerVariance, thread_name="Environmental Temperature Trigger Variance",
            args=(sensor_get_function, sql_column_name_list, sleep_time, variances_list)
        )
    if trigger_variances.pressure_enabled:
        sensor_get_function = sensor_access.get_pressure
        sql_column_name_list = [database_variables.pressure]
        sleep_time = trigger_variances.pressure_wait_seconds
        variances_list = [trigger_variances.pressure_variance]
        app_cached_variables.trigger_variance_thread_pressure = CreateMonitoredThread(
            StartTriggerVariance, thread_name="Pressure Trigger Variance",
            args=(sensor_get_function, sql_column_name_list, sleep_time, variances_list)
        )
    if trigger_variances.altitude_enabled:
        sensor_get_function = sensor_access.get_altitude
        sql_column_name_list = [database_variables.altitude]
        sleep_time = trigger_variances.altitude_wait_seconds
        variances_list = [trigger_variances.altitude_variance]
        app_cached_variables.trigger_variance_thread_altitude = CreateMonitoredThread(
            StartTriggerVariance, thread_name="Altitude Trigger Variance",
            args=(sensor_get_function, sql_column_name_list, sleep_time, variances_list)
        )
    if trigger_variances.humidity_enabled:
        sensor_get_function = sensor_access.get_humidity
        sql_column_name_list = [database_variables.humidity]
        sleep_time = trigger_variances.humidity_wait_seconds
        variances_list = [trigger_variances.humidity_variance]
        app_cached_variables.trigger_variance_thread_humidity = CreateMonitoredThread(
            StartTriggerVariance, thread_name="Humidity Trigger Variance",
            args=(sensor_get_function, sql_column_name_list, sleep_time, variances_list)
        )
    if trigger_variances.distance_enabled:
        sensor_get_function = sensor_access.get_distance
        sql_column_name_list = [database_variables.distance]
        sleep_time = trigger_variances.distance_wait_seconds
        variances_list = [trigger_variances.distance_variance]
        app_cached_variables.trigger_variance_thread_distance = CreateMonitoredThread(
            StartTriggerVariance, thread_name="Distance Trigger Variance",
            args=(sensor_get_function, sql_column_name_list, sleep_time, variances_list)
        )
    if trigger_variances.gas_enabled:
        sensor_get_function = sensor_access.get_gas
        sql_column_name_list = [database_variables.gas_resistance_index, database_variables.gas_oxidising,
                                database_variables.gas_reducing, database_variables.gas_nh3]
        variances_list = [trigger_variances.gas_resistance_index_variance, trigger_variances.gas_oxidising_variance,
                          trigger_variances.gas_reducing_variance, trigger_variances.gas_nh3_variance]
        sleep_time = trigger_variances.gas_wait_seconds
        app_cached_variables.trigger_variance_thread_gas = CreateMonitoredThread(
            StartTriggerVariance, thread_name="GAS Trigger Variance",
            args=(sensor_get_function, sql_column_name_list, sleep_time, variances_list)
        )
    if trigger_variances.particulate_matter_enabled:
        sensor_get_function = sensor_access.get_particulate_matter
        sql_column_name_list = [database_variables.particulate_matter_1, database_variables.particulate_matter_2_5,
                                database_variables.particulate_matter_4, database_variables.particulate_matter_10]
        variances_list = [trigger_variances.particulate_matter_1_variance,
                          trigger_variances.particulate_matter_2_5_variance,
                          trigger_variances.particulate_matter_4_variance,
                          trigger_variances.particulate_matter_10_variance]

        sleep_time = trigger_variances.particulate_matter_wait_seconds
        app_cached_variables.trigger_variance_thread_particulate_matter = CreateMonitoredThread(
            StartTriggerVariance, thread_name="Particulate Matter Trigger Variance",
            args=(sensor_get_function, sql_column_name_list, sleep_time, variances_list)
        )
    if trigger_variances.lumen_enabled:
        sensor_get_function = sensor_access.get_lumen
        sql_column_name_list = [database_variables.lumen]
        sleep_time = trigger_variances.lumen_wait_seconds
        variances_list = [trigger_variances.lumen_variance]
        app_cached_variables.trigger_variance_thread_lumen = CreateMonitoredThread(
            StartTriggerVariance, thread_name="Lumen Trigger Variance",
            args=(sensor_get_function, sql_column_name_list, sleep_time, variances_list)
        )
    if trigger_variances.colour_enabled:
        sensor_get_function = sensor_access.get_ems_colors
        sleep_time = trigger_variances.colour_wait_seconds

        sql_column_name_list = [database_variables.red, database_variables.orange, database_variables.yellow,
                                database_variables.green, database_variables.blue, database_variables.violet]
        variances_list = [trigger_variances.red_variance, trigger_variances.orange_variance,
                          trigger_variances.yellow_variance, trigger_variances.green_variance,
                          trigger_variances.blue_variance, trigger_variances.violet_variance]

        app_cached_variables.trigger_variance_thread_visible_ems = CreateMonitoredThread(
            StartTriggerVariance, thread_name="EMS Colours Trigger Variance",
            args=(sensor_get_function, sql_column_name_list, sleep_time, variances_list)
        )
    if trigger_variances.ultra_violet_enabled:
        sensor_get_function = sensor_access.get_ultra_violet
        sql_column_name_list = [database_variables.ultra_violet_a, database_variables.ultra_violet_b]
        sleep_time = trigger_variances.ultra_violet_wait_seconds
        variances_list = [trigger_variances.ultra_violet_a_variance, trigger_variances.ultra_violet_b_variance]
        app_cached_variables.trigger_variance_thread_ultra_violet = CreateMonitoredThread(
            StartTriggerVariance, thread_name="Ultra Violet Trigger Variance",
            args=(sensor_get_function, sql_column_name_list, sleep_time, variances_list)
        )
    if trigger_variances.accelerometer_enabled:
        sensor_get_function = sensor_access.get_accelerometer_xyz
        sql_column_name_list = [database_variables.acc_x, database_variables.acc_y, database_variables.acc_z]
        sleep_time = trigger_variances.accelerometer_wait_seconds
        variances_list = [trigger_variances.accelerometer_x_variance,
                          trigger_variances.accelerometer_y_variance,
                          trigger_variances.accelerometer_z_variance]
        app_cached_variables.trigger_variance_thread_accelerometer = CreateMonitoredThread(
            StartTriggerVariance, thread_name="Accelerometer Trigger Variance",
            args=(sensor_get_function, sql_column_name_list, sleep_time, variances_list)
        )
    if trigger_variances.magnetometer_enabled:
        sensor_get_function = sensor_access.get_magnetometer_xyz
        sql_column_name_list = [database_variables.mag_x, database_variables.mag_y, database_variables.mag_z]
        sleep_time = trigger_variances.magnetometer_wait_seconds
        variances_list = [trigger_variances.magnetometer_x_variance,
                          trigger_variances.magnetometer_y_variance,
                          trigger_variances.magnetometer_z_variance]
        app_cached_variables.trigger_variance_thread_magnetometer = CreateMonitoredThread(
            StartTriggerVariance, thread_name="Magnetometer Trigger Variance",
            args=(sensor_get_function, sql_column_name_list, sleep_time, variances_list)
        )
    if trigger_variances.gyroscope_enabled:
        sensor_get_function = sensor_access.get_gyroscope_xyz
        sql_column_name_list = [database_variables.gyro_x, database_variables.gyro_y, database_variables.gyro_z]
        sleep_time = trigger_variances.gyroscope_wait_seconds
        variances_list = [trigger_variances.gyroscope_x_variance,
                          trigger_variances.gyroscope_y_variance,
                          trigger_variances.gyroscope_z_variance]
        app_cached_variables.trigger_variance_thread_gyroscope = CreateMonitoredThread(
            StartTriggerVariance, thread_name="Gyroscope Trigger Variance",
            args=(sensor_get_function, sql_column_name_list, sleep_time, variances_list)
        )


def get_datetime_stamp():
    """ Returns current UTC 0 time as a string "%Y-%m-%d %H:%M:%S.%f" (%f to 3 decimal places). """
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
