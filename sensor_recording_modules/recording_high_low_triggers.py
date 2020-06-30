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
from operations_modules.app_generic_functions import thread_function, CreateMonitoredThread as CMT
from operations_modules import app_cached_variables
from configuration_modules import app_config_access
from operations_modules import sqlite_database
from sensor_modules import sensor_access

database_variables = app_cached_variables.database_variables


class _CreateHighLowTriggerThreadData:
    def __init__(self):
        config_high_low_triggers = app_config_access.trigger_high_low

        self.system_temperature = {
            "enabled": config_high_low_triggers.cpu_temperature_enabled,
            "get_reading_func": sensor_access.get_cpu_temperature,
            "sleep_duration": config_high_low_triggers.cpu_temperature_wait_seconds,
            "database_column": database_variables.system_temperature,
            "low_trigger": config_high_low_triggers.cpu_temperature_low,
            "high_trigger": config_high_low_triggers.cpu_temperature_high
        }
        self.env_temperature = {
            "enabled": config_high_low_triggers.env_temperature_enabled,
            "get_reading_func": sensor_access.get_sensor_temperature,
            "sleep_duration": config_high_low_triggers.env_temperature_wait_seconds,
            "database_column": database_variables.env_temperature,
            "low_trigger": config_high_low_triggers.env_temperature_low,
            "high_trigger": config_high_low_triggers.env_temperature_high
        }
        self.pressure = {
            "enabled": config_high_low_triggers.pressure_enabled,
            "get_reading_func": sensor_access.get_pressure,
            "sleep_duration": config_high_low_triggers.pressure_wait_seconds,
            "database_column": database_variables.pressure,
            "low_trigger": config_high_low_triggers.pressure_low,
            "high_trigger": config_high_low_triggers.pressure_high
        }
        self.humidity = {
            "enabled": config_high_low_triggers.humidity_enabled,
            "get_reading_func": sensor_access.get_humidity,
            "sleep_duration": config_high_low_triggers.humidity_wait_seconds,
            "database_column": database_variables.humidity,
            "low_trigger": config_high_low_triggers.humidity_low,
            "high_trigger": config_high_low_triggers.humidity_high
        }
        self.altitude = {
            "enabled": config_high_low_triggers.altitude_enabled,
            "get_reading_func": sensor_access.get_altitude,
            "sleep_duration": config_high_low_triggers.altitude_wait_seconds,
            "database_column": database_variables.altitude,
            "low_trigger": config_high_low_triggers.altitude_low,
            "high_trigger": config_high_low_triggers.altitude_high
        }
        self.distance = {
            "enabled": config_high_low_triggers.distance_enabled,
            "get_reading_func": sensor_access.get_distance,
            "sleep_duration": config_high_low_triggers.distance_wait_seconds,
            "database_column": database_variables.distance,
            "low_trigger": config_high_low_triggers.distance_low,
            "high_trigger": config_high_low_triggers.distance_high
        }
        self.lumen = {
            "enabled": config_high_low_triggers.lumen_enabled,
            "get_reading_func": sensor_access.get_lumen,
            "sleep_duration": config_high_low_triggers.lumen_wait_seconds,
            "database_column": database_variables.lumen,
            "low_trigger": config_high_low_triggers.lumen_low,
            "high_trigger": config_high_low_triggers.lumen_high
        }

        self.colours = {
            "enabled": config_high_low_triggers.colour_enabled,
            "get_reading_func": sensor_access.get_ems_colors,
            "sleep_duration": config_high_low_triggers.colour_wait_seconds,
            "database_column": [database_variables.red, database_variables.orange, database_variables.yellow,
                                database_variables.green, database_variables.blue, database_variables.violet],
            "low_trigger": [config_high_low_triggers.red_low, config_high_low_triggers.orange_low,
                            config_high_low_triggers.yellow_low,
                            config_high_low_triggers.green_low, config_high_low_triggers.blue_low,
                            config_high_low_triggers.violet_low],
            "high_trigger": [config_high_low_triggers.red_high, config_high_low_triggers.orange_high,
                             config_high_low_triggers.yellow_high,
                             config_high_low_triggers.green_high, config_high_low_triggers.blue_high,
                             config_high_low_triggers.violet_high]
        }
        self.ultra_violet = {
            "enabled": config_high_low_triggers.ultra_violet_enabled,
            "get_reading_func": sensor_access.get_ultra_violet,
            "sleep_duration": config_high_low_triggers.ultra_violet_wait_seconds,
            "database_column": [database_variables.ultra_violet_a,
                                database_variables.ultra_violet_b],
            "low_trigger": [config_high_low_triggers.ultra_violet_a_low,
                            config_high_low_triggers.ultra_violet_b_low],
            "high_trigger": [config_high_low_triggers.ultra_violet_a_high,
                             config_high_low_triggers.ultra_violet_b_high]
        }
        self.gas_resistance = {
            "enabled": config_high_low_triggers.gas_enabled,
            "get_reading_func": sensor_access.get_gas,
            "sleep_duration": config_high_low_triggers.gas_wait_seconds,
            "database_column": [database_variables.gas_resistance_index,
                                database_variables.gas_oxidising,
                                database_variables.gas_reducing,
                                database_variables.gas_nh3],
            "low_trigger": [config_high_low_triggers.gas_resistance_index_low,
                            config_high_low_triggers.gas_oxidising_low,
                            config_high_low_triggers.gas_reducing_low,
                            config_high_low_triggers.gas_nh3_low],
            "high_trigger": [config_high_low_triggers.gas_resistance_index_high,
                             config_high_low_triggers.gas_oxidising_high,
                             config_high_low_triggers.gas_reducing_high,
                             config_high_low_triggers.gas_nh3_high]
        }
        self.particulate_matter = {
            "enabled": config_high_low_triggers.particulate_matter_enabled,
            "get_reading_func": sensor_access.get_particulate_matter,
            "sleep_duration": config_high_low_triggers.particulate_matter_wait_seconds,
            "database_column": [database_variables.particulate_matter_1,
                                database_variables.particulate_matter_2_5,
                                database_variables.particulate_matter_4,
                                database_variables.particulate_matter_10],
            "low_trigger": [config_high_low_triggers.particulate_matter_1_low,
                            config_high_low_triggers.particulate_matter_2_5_low,
                            config_high_low_triggers.particulate_matter_4_low,
                            config_high_low_triggers.particulate_matter_10_low],
            "high_trigger": [config_high_low_triggers.particulate_matter_1_high,
                             config_high_low_triggers.particulate_matter_2_5_high,
                             config_high_low_triggers.particulate_matter_4_high,
                             config_high_low_triggers.particulate_matter_10_high]
        }

        self.accelerometer = {
            "enabled": config_high_low_triggers.accelerometer_enabled,
            "get_reading_func": sensor_access.get_accelerometer_xyz,
            "sleep_duration": config_high_low_triggers.accelerometer_wait_seconds,
            "database_column": [database_variables.acc_x,
                                database_variables.acc_y,
                                database_variables.acc_z],
            "low_trigger": [config_high_low_triggers.accelerometer_x_low,
                            config_high_low_triggers.accelerometer_y_low,
                            config_high_low_triggers.accelerometer_z_low],
            "high_trigger": [config_high_low_triggers.accelerometer_x_high,
                             config_high_low_triggers.accelerometer_y_high,
                             config_high_low_triggers.accelerometer_z_high]
        }
        self.magnetometer = {
            "enabled": config_high_low_triggers.magnetometer_enabled,
            "get_reading_func": sensor_access.get_magnetometer_xyz,
            "sleep_duration": config_high_low_triggers.magnetometer_wait_seconds,
            "database_column": [database_variables.mag_x,
                                database_variables.mag_y,
                                database_variables.mag_z],
            "low_trigger": [config_high_low_triggers.magnetometer_x_low,
                            config_high_low_triggers.magnetometer_y_low,
                            config_high_low_triggers.magnetometer_z_low],
            "high_trigger": [config_high_low_triggers.magnetometer_x_high,
                             config_high_low_triggers.magnetometer_y_high,
                             config_high_low_triggers.magnetometer_z_high]
        }
        self.gyroscope = {
            "enabled": config_high_low_triggers.gyroscope_enabled,
            "get_reading_func": sensor_access.get_gyroscope_xyz,
            "sleep_duration": config_high_low_triggers.gyroscope_wait_seconds,
            "database_column": [database_variables.gyro_x,
                                database_variables.gyro_y,
                                database_variables.gyro_z],
            "low_trigger": [config_high_low_triggers.gyroscope_x_low,
                            config_high_low_triggers.gyroscope_y_low,
                            config_high_low_triggers.gyroscope_z_low],
            "high_trigger": [config_high_low_triggers.gyroscope_x_high,
                             config_high_low_triggers.gyroscope_y_high,
                             config_high_low_triggers.gyroscope_z_high]
        }


class _SingleTriggerThread:
    def __init__(self, custom_trigger_variables):
        self.current_state = "Disabled"

        self.custom_trigger_variables = custom_trigger_variables
        if self.custom_trigger_variables["enabled"]:
            self.current_state = "Starting"
            if self.custom_trigger_variables["get_reading_func"]() != app_cached_variables.no_sensor_present:
                self.low_trigger = self.custom_trigger_variables["low_trigger"]
                self.high_trigger = self.custom_trigger_variables["high_trigger"]

                while not app_cached_variables.restart_all_trigger_threads:
                    try:
                        sensor_reading = self.custom_trigger_variables["get_reading_func"]()
                        reading_taken_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                        if self.high_trigger > sensor_reading > self.low_trigger:
                            if self.current_state != "Normal":
                                self.current_state = "Normal"
                            self._write_readings_to_sql(reading_taken_at, sensor_reading, self.current_state)
                        elif sensor_reading < self.low_trigger:
                            if self.current_state != "Low":
                                self.current_state = "Low"
                                self._write_readings_to_sql(reading_taken_at, sensor_reading, self.current_state)
                        elif sensor_reading > self.high_trigger:
                            if self.current_state != "High":
                                self.current_state = "High"
                                self._write_readings_to_sql(reading_taken_at, sensor_reading, self.current_state)
                    except Exception as error:
                        log_msg = "Trigger problem in '" + str(self.custom_trigger_variables["database_column"])
                        logger.primary_logger.error(log_msg + "' Trigger Thread: " + str(error))

                    sleep_fraction_interval = 5
                    if self.custom_trigger_variables["sleep_duration"] < 5:
                        sleep_fraction_interval = self.custom_trigger_variables["sleep_duration"]
                    sleep_total = 0
                    while sleep_total < self.custom_trigger_variables["sleep_duration"] \
                            and not app_cached_variables.restart_all_trigger_threads:
                        sleep(sleep_fraction_interval)
                        sleep_total += sleep_fraction_interval
            else:
                self.current_state = "Sensor Missing"

    def _write_readings_to_sql(self, reading_datetime, reading, trigger_state):
        try:
            sql_data = [str(reading_datetime), app_cached_variables.hostname, str(reading), trigger_state]
            sql_string = "INSERT OR IGNORE INTO TriggerData (" + \
                         database_variables.all_tables_datetime + "," + \
                         database_variables.sensor_name + "," + \
                         self.custom_trigger_variables["database_column"] + "," + \
                         database_variables.trigger_state + \
                         ") VALUES (?,?,?,?)"
            sqlite_database.write_to_sql_database(sql_string, sql_data)
        except Exception as error:
            log_msg = "Trigger '" + str(self.custom_trigger_variables["database_column"])
            logger.primary_logger.error(log_msg + "' Recording Failure: " + str(error))


# TODO: Recording works just fine, but need to add a state for each reading in the readings
class _MultiTriggerThread:
    def __init__(self, custom_trigger_variables):
        self.current_state = []
        for _ in custom_trigger_variables["database_column"]:
            self.current_state.append("Disabled")
        if custom_trigger_variables["enabled"]:
            for index, _ in enumerate(custom_trigger_variables["database_column"]):
                self.current_state[index] = "Starting"
            if custom_trigger_variables["get_reading_func"]() != app_cached_variables.no_sensor_present:
                while not app_cached_variables.restart_all_trigger_threads:
                    try:
                        sensor_readings = custom_trigger_variables["get_reading_func"]()
                        reading_taken_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                        db_col_list = custom_trigger_variables["database_column"]
                        trig_low_list = custom_trigger_variables["low_trigger"]
                        trig_high_list = custom_trigger_variables["high_trigger"]
                        for reading, trig_high, trig_low, db_col in zip(sensor_readings, trig_high_list,
                                                                        trig_low_list, enumerate(db_col_list)):
                            index = db_col[0]
                            db_col = db_col[1]
                            if str(reading) != app_cached_variables.no_sensor_present:
                                if trig_low < reading < trig_high:
                                    if self.current_state[index] != "Normal":
                                        self.current_state[index] = "Normal"
                                        self._write_readings_to_sql(reading_taken_at, reading,
                                                                    self.current_state[index], db_col)
                                elif trig_low > reading:
                                    if self.current_state[index] != "Low":
                                        self.current_state[index] = "Low"
                                        self._write_readings_to_sql(reading_taken_at, reading,
                                                                    self.current_state[index], db_col)
                                elif trig_high < reading:
                                    if self.current_state[index] != "High":
                                        self.current_state[index] = "High"
                                        self._write_readings_to_sql(reading_taken_at, reading,
                                                                    self.current_state[index], db_col)
                    except Exception as error:
                        log_msg = "Trigger problem in '" + str(custom_trigger_variables["database_column"])
                        logger.primary_logger.error(log_msg + "' Trigger Thread: " + str(error))

                    sleep_fraction_interval = 5
                    if custom_trigger_variables["sleep_duration"] < 5:
                        sleep_fraction_interval = custom_trigger_variables["sleep_duration"]
                    sleep_total = 0
                    while sleep_total < custom_trigger_variables["sleep_duration"] \
                            and not app_cached_variables.restart_all_trigger_threads:
                        sleep(sleep_fraction_interval)
                        sleep_total += sleep_fraction_interval
            else:
                self.current_state = "Sensor Missing"

    @staticmethod
    def _write_readings_to_sql(reading_datetime, reading, trigger_state, database_column):
        try:
            sql_data = [str(reading_datetime), app_cached_variables.hostname, str(reading), trigger_state]
            sql_string = "INSERT OR IGNORE INTO TriggerData (" + \
                         database_variables.all_tables_datetime + "," + \
                         database_variables.sensor_name + "," + \
                         database_column + "," + \
                         database_variables.trigger_state + \
                         ") VALUES (?,?,?,?)"
            sqlite_database.write_to_sql_database(sql_string, sql_data)
        except Exception as error:
            log_msg = "Trigger '" + str(database_column) + "' Recording Failure: " + str(error)
            logger.primary_logger.error(log_msg)


def start_trigger_high_low_recording_server():
    if app_config_access.trigger_high_low.enable_high_low_trigger_recording:
        tmp_tv = _CreateHighLowTriggerThreadData()

        if app_config_access.trigger_high_low.cpu_temperature_enabled:
            app_cached_variables.trigger_high_low_cpu_temp = CMT(
                _SingleTriggerThread,
                args=[tmp_tv.system_temperature],
                thread_name="High/Low Trigger CPU Temperature"
            )

        if app_config_access.trigger_high_low.env_temperature_enabled:
            app_cached_variables.trigger_high_low_env_temp = CMT(
                _SingleTriggerThread,
                args=[tmp_tv.env_temperature],
                thread_name="High/Low Trigger Env Temperature"
            )

        if app_config_access.trigger_high_low.pressure_enabled:
            app_cached_variables.trigger_high_low_pressure = CMT(
                _SingleTriggerThread,
                args=[tmp_tv.pressure],
                thread_name="High/Low Trigger Pressure"
            )

        if app_config_access.trigger_high_low.humidity_enabled:
            app_cached_variables.trigger_high_low_humidity = CMT(
                _SingleTriggerThread,
                args=[tmp_tv.humidity],
                thread_name="High/Low Trigger Humidity"
            )

        if app_config_access.trigger_high_low.altitude_enabled:
            app_cached_variables.trigger_high_low_altitude = CMT(
                _SingleTriggerThread,
                args=[tmp_tv.altitude],
                thread_name="High/Low Trigger Altitude"
            )

        if app_config_access.trigger_high_low.distance_enabled:
            app_cached_variables.trigger_high_low_distance = CMT(
                _SingleTriggerThread,
                args=[tmp_tv.distance],
                thread_name="High/Low Trigger Distance"
            )

        if app_config_access.trigger_high_low.lumen_enabled:
            app_cached_variables.trigger_high_low_lumen = CMT(
                _SingleTriggerThread,
                args=[tmp_tv.lumen],
                thread_name="High/Low Trigger Lumen"
            )

        if app_config_access.trigger_high_low.colour_enabled:
            app_cached_variables.trigger_high_low_visible_colours = CMT(
                _MultiTriggerThread,
                args=[tmp_tv.colours],
                thread_name="High/Low Trigger Colours"
            )

        if app_config_access.trigger_high_low.ultra_violet_enabled:
            app_cached_variables.trigger_high_low_ultra_violet = CMT(
                _MultiTriggerThread,
                args=[tmp_tv.ultra_violet],
                thread_name="High/Low Trigger Ultra Violet"
            )

        if app_config_access.trigger_high_low.gas_enabled:
            app_cached_variables.trigger_high_low_gas = CMT(
                _MultiTriggerThread,
                args=[tmp_tv.gas_resistance],
                thread_name="High/Low Trigger Gas"
            )

        if app_config_access.trigger_high_low.particulate_matter_enabled:
            app_cached_variables.trigger_high_low_particulate_matter = CMT(
                _MultiTriggerThread,
                args=[tmp_tv.particulate_matter],
                thread_name="High/Low Trigger Particulate Matter"
            )

        if app_config_access.trigger_high_low.accelerometer_enabled:
            app_cached_variables.trigger_high_low_accelerometer = CMT(
                _MultiTriggerThread,
                args=[tmp_tv.accelerometer],
                thread_name="High/Low Trigger Accelerometer"
            )

        if app_config_access.trigger_high_low.magnetometer_enabled:
            app_cached_variables.trigger_high_low_magnetometer = CMT(
                _MultiTriggerThread,
                args=[tmp_tv.magnetometer],
                thread_name="High/Low Trigger Magnetometer"
            )

        if app_config_access.trigger_high_low.gyroscope_enabled:
            app_cached_variables.trigger_high_low_gyroscope = CMT(
                _MultiTriggerThread,
                args=[tmp_tv.gyroscope],
                thread_name="High/Low Trigger Gyroscope"
            )
        logger.primary_logger.info(" -- High/Low Trigger Recording Threads Started")
    else:
        logger.primary_logger.debug("High/Low Trigger Recording Disabled in Configuration")


def restart_high_low_trigger_threads():
    thread_function(_restart_high_low_worker)


def _restart_high_low_worker():
    if app_config_access.trigger_high_low.enable_high_low_trigger_recording:
        logger.primary_logger.info(" -- All Enabled High/Low Trigger Recording Threads ReStarted")
        app_cached_variables.restart_all_trigger_threads = True
        sleep(10)
        app_cached_variables.restart_all_trigger_threads = False
        start_trigger_high_low_recording_server()