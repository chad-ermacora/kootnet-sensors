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
from time import sleep, time
from datetime import datetime
from operations_modules import logger
from operations_modules.app_generic_functions import CreateMonitoredThread, thread_function
from configuration_modules import app_config_access
from operations_modules import app_cached_variables
from operations_modules import sqlite_database
from sensor_modules import sensor_access


class CreateTriggerVarianceData:
    def __init__(self, get_sensor_data_function, sensor_database_variable, enabled=1,
                 thread_name="GenericTriggerThread", variance=99999.99, sensor_wait_seconds=10,
                 num_of_readings=1, number_of_reading_sets=3):
        try:
            self.get_sensor_data_function = get_sensor_data_function
            test_sensor_reading = self.get_sensor_data_function()
            self.enabled = enabled
            self.thread_name = thread_name
            self.num_of_readings = num_of_readings
            self.number_of_sets = number_of_reading_sets
            self.variance = variance
            self.sql_sensor_name = sensor_access.get_hostname()
            self.sql_ip = sensor_access.get_ip()
            self.sensor_wait_seconds = sensor_wait_seconds

            self.sensor_database_variable = sensor_database_variable
            self.max_trigger_errors = 10
            self.last_error_time = time()
            self.reset_errors_after = 60.0
            if self.enabled:
                logger.primary_logger.debug(
                    thread_name + " - Enabled: " + str(self.enabled) +
                    " No Sensors: " + str(app_config_access.installed_sensors.no_sensors) +
                    " Test Reading: " + str(test_sensor_reading) +
                    " DB Variable: " + str(sensor_database_variable) +
                    " # Readings: " + str(self.num_of_readings) +
                    " # Sets: " + str(self.number_of_sets) +
                    " Variance: " + str(self.variance) +
                    " Wait Sec: " + str(self.sensor_wait_seconds)
                )
            else:
                logger.primary_logger.debug(thread_name + " - Disabled")
        except Exception as error:
            logger.primary_logger.error(thread_name + " Error Processing Data: " + str(error))


class CreateTriggerVarianceThread:
    """ Creates an object holding a Trigger Variance Monitored Thread (If Enabled). """

    def __init__(self, trigger_data):
        self.running = False

        self.trigger_data = trigger_data
        self.number_of_errors = 0
        if app_config_access.installed_sensors.linux_system:
            self.sql_columns_str = "DateTime,SensorName,IP," + trigger_data.sensor_database_variable
        else:
            self.sql_columns_str_start = "DateTime," + trigger_data.sensor_database_variable

        self.reading_and_datetime_stamps = []
        thread_function(self._start_thread)
        while not app_cached_variables.restart_all_trigger_threads:
            sleep(5)

    def _start_thread(self):
        if self.trigger_data.enabled and not app_config_access.installed_sensors.no_sensors:
            while not self.running:
                try:
                    thread_name = self.trigger_data.thread_name
                    self.monitored_thread = CreateMonitoredThread(self._data_check, thread_name=thread_name)
                    self.running = True
                except Exception as error:
                    log_msg = "Error running Trigger Variance tests on " + self.trigger_data.thread_name + ": "
                    logger.primary_logger.error(log_msg + str(error))
                sleep(10)
        else:
            self.monitored_thread = None

    def _update_sensor_readings_set(self):
        """ Sends provided string to retrieve sensor data. """
        sensor_reading = []
        datetime_stamps = []

        count = 0
        while count < self.trigger_data.number_of_sets and not app_cached_variables.restart_all_trigger_threads:
            try:
                sensor_reading.append(self.trigger_data.get_sensor_data_function())
            except Exception as error:
                logger.primary_logger.warning("Sensor data retrieval Failed: " + str(error))
                sensor_reading.append("Failed")

            datetime_stamps.append(get_datetime_stamp())
            count += 1
            sleep(self.trigger_data.sensor_wait_seconds)
        self.reading_and_datetime_stamps = [sensor_reading, datetime_stamps]

    def _sensor_uptime_check(self):
        while not app_cached_variables.restart_all_trigger_threads:
            self._update_sensor_readings_set()
            execute_str_list = _readings_to_sql_write_str_single_data(self)
            sqlite_database.write_to_sql_database(execute_str_list[0], data_entries=None)

    def _data_check(self):
        log_msg = self.trigger_data.thread_name + " Starting Checks.  Checking every "
        logger.primary_logger.debug(log_msg + str(self.trigger_data.sensor_wait_seconds) + " Seconds")
        while not app_cached_variables.restart_all_trigger_threads:
            if self.number_of_errors > self.trigger_data.max_trigger_errors:
                log_msg = "Max Errors reached for " + self.trigger_data.thread_name + ": Stopping Trigger Thread"
                logger.primary_logger.warning(log_msg)
                while not app_cached_variables.restart_all_trigger_threads:
                    sleep(10)
            if self._check_differences():
                execute_str_list = []
                if self.trigger_data.num_of_readings == 1:
                    execute_str_list = _readings_to_sql_write_str_single_data(self)
                elif self.trigger_data.num_of_readings > 1:
                    execute_str_list = _readings_to_sql_write_str_multiple_data(self)
                for sql_execute in execute_str_list:
                    sqlite_database.write_to_sql_database(sql_execute, data_entries=None)

    def _check_differences(self):
        differences = []
        try:
            self._update_sensor_readings_set()
            if self.trigger_data.num_of_readings == 1:
                if self.reading_and_datetime_stamps[0][0] == app_cached_variables.no_sensor_present:
                    sleep(10)
                else:
                    previous_reading = self.reading_and_datetime_stamps[0][0]
                    for reading in self.reading_and_datetime_stamps[0]:
                        if abs(float(reading) - float(previous_reading)) > self.trigger_data.variance:
                            return True
                        previous_reading = reading
            elif self.trigger_data.num_of_readings > 1:
                if self.reading_and_datetime_stamps[0][0][0] == app_cached_variables.no_sensor_present:
                    sleep(10)
                else:
                    previous_readings = self.reading_and_datetime_stamps[0][0]
                    for reading_list in self.reading_and_datetime_stamps[0]:
                        tmp_differences = []
                        for new_reading, old_reading in zip(reading_list, previous_readings):
                            tmp_differences.append(abs(float(new_reading) - float(old_reading)))
                        differences.append(tmp_differences)

                        for difference_list in differences:
                            count = 0
                            for difference in difference_list:
                                if difference > self.trigger_data.variance[count]:
                                    return True
                                count += 1
                        previous_readings = reading_list
        except Exception as error:
            logger.primary_logger.warning(self.trigger_data.thread_name + " Trigger difference check: " + str(error))
            if (time() - self.trigger_data.last_error_time) > self.trigger_data.reset_errors_after:
                self.number_of_errors = 0
            self.trigger_data.last_error_time = time()
            self.number_of_errors += 1
        return False


def get_datetime_stamp():
    """ Returns current UTC 0 time as a string "%Y-%m-%d %H:%M:%S.%f". """
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]


def _readings_to_sql_write_str_single_data(trigger_object):
    """ Takes a Sensor Data Set as input and returns a string for writing the readings to the SQLite Database. """
    sql_query_start = "INSERT OR IGNORE INTO TriggerData ("
    sql_query_values_start = ") VALUES ("
    sql_query_values_end = ")"

    sql_execute_list = []
    try:
        for reading, datetime_var in zip(trigger_object.reading_and_datetime_stamps[0],
                                         trigger_object.reading_and_datetime_stamps[1]):
            execute_string = sql_query_start + trigger_object.sql_columns_str + \
                             sql_query_values_start + "'" + datetime_var + "','"
            if app_config_access.installed_sensors.linux_system:
                execute_string += trigger_object.trigger_data.sql_sensor_name + "','" + \
                                  trigger_object.trigger_data.sql_ip + "','"
            execute_string += str(reading) + "'" + sql_query_values_end
            sql_execute_list.append(execute_string)
    except Exception as error:
        logger.primary_logger.error("Triggers Single Reading - Get string for write to DB Error: " + str(error))
    return sql_execute_list


def _readings_to_sql_write_str_multiple_data(trigger_object):
    """ Takes a Sensor Data Set as input and returns a string for writing the readings to the SQLite Database. """
    sql_query_start = "INSERT OR IGNORE INTO TriggerData ("
    sql_query_values_start = ") VALUES ("
    sql_query_values_end = ")"

    sql_execute_list = []

    count = 0
    try:
        for reading_set in trigger_object.reading_and_datetime_stamps[0]:
            execute_string = sql_query_start + trigger_object.sql_columns_str + sql_query_values_start + "'" + \
                             str(trigger_object.reading_and_datetime_stamps[1][count]) + "','"
            if app_config_access.installed_sensors.linux_system:
                execute_string += trigger_object.trigger_data.sql_sensor_name + "','" + \
                                  trigger_object.trigger_data.sql_ip + "','"
            for reading in reading_set:
                execute_string += str(reading) + "','"

            execute_string = execute_string[:-2]
            execute_string += sql_query_values_end
            sql_execute_list.append(execute_string)
            count += 1
    except Exception as error:
        logger.primary_logger.error("Triggers Sextuplet Readings - Get string for write to DB Error: " + str(error))
    return sql_execute_list


def auto_set_triggers_wait_time(config, multiplier=10.0, set_lowest=False):
    sensor_names_list = [
        "cpu_temperature", "environment_temperature", "pressure", "altitude", "humidity", "distance", "gas",
        "particulate_matter", "lumen", "colours", "ultra_violet", "accelerometer_xyz", "magnetometer_xyz",
        "gyroscope_xyz"
    ]
    sensor_latencies = {
        "cpu_temperature": 0, "environment_temperature": 0, "pressure": 0, "altitude": 0, "humidity": 0,
        "distance": 0, "gas": 0, "particulate_matter": 0, "lumen": 0, "colours": 0, "ultra_violet": 0,
        "accelerometer_xyz": 0, "magnetometer_xyz": 0, "gyroscope_xyz": 0
    }

    multi_latency_sets = [
        sensor_access.get_sensors_latency(), sensor_access.get_sensors_latency(), sensor_access.get_sensors_latency(),
        sensor_access.get_sensors_latency(), sensor_access.get_sensors_latency(), sensor_access.get_sensors_latency()
    ]

    for sensor_name in sensor_names_list:
        for sensor_latency_pull in multi_latency_sets:
            if sensor_latency_pull[sensor_name] is not None:
                if sensor_latency_pull[sensor_name] > sensor_latencies[sensor_name]:
                    try:
                        sensor_latencies[sensor_name] = sensor_latency_pull[sensor_name] * multiplier
                    except Exception as error:
                        logger.primary_logger.error("Unable to set " + sensor_name + " wait time: " + str(error))
            else:
                sensor_latencies[sensor_name] = 999.999

    _set_trigger_config_seconds(config, sensor_latencies, set_lowest)


def _set_trigger_config_seconds(config, sensor_latencies, set_lowest):
    config.cpu_temperature_wait_seconds = round(sensor_latencies["cpu_temperature"], 6)
    config.env_temperature_wait_seconds = round(sensor_latencies["environment_temperature"], 6)
    config.pressure_wait_seconds = round(sensor_latencies["pressure"], 6)
    config.altitude_wait_seconds = round(sensor_latencies["altitude"], 6)
    config.humidity_wait_seconds = round(sensor_latencies["humidity"], 6)
    config.distance_wait_seconds = round(sensor_latencies["distance"], 6)
    config.gas_wait_seconds = round(sensor_latencies["gas"], 6)
    config.particulate_matter_wait_seconds = round(sensor_latencies["particulate_matter"], 6)
    config.lumen_wait_seconds = round(sensor_latencies["lumen"], 6)
    config.colour_wait_seconds = round(sensor_latencies["colours"], 6)
    config.ultra_violet_wait_seconds = round(sensor_latencies["ultra_violet"], 6)
    config.accelerometer_wait_seconds = round(sensor_latencies["accelerometer_xyz"], 6)
    config.magnetometer_wait_seconds = round(sensor_latencies["magnetometer_xyz"], 6)
    config.gyroscope_wait_seconds = round(sensor_latencies["gyroscope_xyz"], 6)

    if not set_lowest:
        _check_default_triggers(config)

    config.update_configuration_settings_list()
    config.save_config_to_file()


def _check_default_triggers(config):
    if config.cpu_temperature_wait_seconds < 15:
        config.cpu_temperature_wait_seconds = 15
    if config.env_temperature_wait_seconds < 15:
        config.env_temperature_wait_seconds = 15
    if config.pressure_wait_seconds < 30:
        config.pressure_wait_seconds = 30
    if config.altitude_wait_seconds < 30:
        config.altitude_wait_seconds = 30
    if config.humidity_wait_seconds < 15:
        config.humidity_wait_seconds = 15
    if config.distance_wait_seconds < 1:
        config.distance_wait_seconds = 1
    if config.gas_wait_seconds < 30:
        config.gas_wait_seconds = 30
    if config.particulate_matter_wait_seconds < 30:
        config.particulate_matter_wait_seconds = 30
    if config.lumen_wait_seconds < 1:
        config.lumen_wait_seconds = 1
    if config.colour_wait_seconds < 1:
        config.colour_wait_seconds = 1
    if config.ultra_violet_wait_seconds < 1:
        config.ultra_violet_wait_seconds = 1
    if config.accelerometer_wait_seconds < 0.25:
        config.accelerometer_wait_seconds = 0.25
    if config.magnetometer_wait_seconds < 0.25:
        config.magnetometer_wait_seconds = 0.25
    if config.gyroscope_wait_seconds < 0.25:
        config.gyroscope_wait_seconds = 0.25
