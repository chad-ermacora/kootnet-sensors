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
from operations_modules.app_generic_functions import CreateMonitoredThread
from operations_modules import app_config_access
from operations_modules.app_cached_variables import normal_state, low_state, high_state, no_sensor_present
from operations_modules import sqlite_database
from sensor_modules import sensor_access


class CreateTriggerVarianceData:
    def __init__(self, get_sensor_data_function, sensor_database_variable, enabled=1,
                 thread_name="GenericTriggerThread", variance=99999.99, sensor_wait_seconds=10,
                 num_of_readings=1, number_of_reading_sets=3):
        self.get_sensor_data_function = get_sensor_data_function
        self.has_sensor = 1
        test_sensor_reading = self.get_sensor_data_function()
        if test_sensor_reading == no_sensor_present:
            self.has_sensor = 0
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
            logger.primary_logger.debug(thread_name + " - Enabled: " + str(self.enabled) +
                                        " Has Sensor: " + str(self.has_sensor) +
                                        " Test Reading: " + str(test_sensor_reading) +
                                        " DB Variable: " + str(sensor_database_variable) +
                                        " # Readings: " + str(self.num_of_readings) +
                                        " # Sets: " + str(self.number_of_sets) +
                                        " Variance: " + str(self.variance) +
                                        " Wait Sec: " + str(self.sensor_wait_seconds))
        else:
            logger.primary_logger.debug(thread_name + " - Disabled")


class CreateTriggerVarianceThread:
    """ Creates an object holding a Trigger Variance Monitored Thread (If Enabled). """

    def __init__(self, trigger_data, sensor_uptime=False):
        self.trigger_data = trigger_data
        self.number_of_errors = 0
        if app_config_access.installed_sensors.linux_system:
            self.sql_columns_str = "DateTime,SensorName,IP," + trigger_data.sensor_database_variable
        else:
            self.sql_columns_str_start = "DateTime," + trigger_data.sensor_database_variable

        self.reading_and_datetime_stamps = []
        if self.trigger_data.enabled and self.trigger_data.has_sensor:
            if sensor_uptime:
                self.monitored_thread = CreateMonitoredThread(self._sensor_uptime_check,
                                                              thread_name=self.trigger_data.thread_name)
            else:
                self.monitored_thread = CreateMonitoredThread(self._data_check,
                                                              thread_name=self.trigger_data.thread_name)
        else:
            logger.primary_logger.debug(self.trigger_data.thread_name + " disabled or missing sensor")
            self.monitored_thread = None

    def _update_sensor_readings_set(self):
        """ Sends provided string to retrieve sensor data. """
        sensor_reading = []
        datetime_stamps = []

        count = 0
        while count < self.trigger_data.number_of_sets:
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
        while True:
            self._update_sensor_readings_set()
            execute_str_list = _readings_to_sql_write_str_single_data(self)
            sqlite_database.write_to_sql_database(execute_str_list[0])

    def _data_check(self):
        log_msg = self.trigger_data.thread_name + " Starting Checks.  Checking every "
        logger.primary_logger.debug(log_msg + str(self.trigger_data.sensor_wait_seconds) + " Seconds")
        while True:
            if self.number_of_errors > self.trigger_data.max_trigger_errors:
                log_msg = "Max Errors reached for " + self.trigger_data.thread_name + ": Stopping Trigger Thread"
                logger.primary_logger.warning(log_msg)
                while True:
                    sleep(3600)
            if self._check_differences():
                execute_str_list = []
                if self.trigger_data.num_of_readings == 1:
                    execute_str_list = _readings_to_sql_write_str_single_data(self)
                elif self.trigger_data.num_of_readings > 1:
                    execute_str_list = _readings_to_sql_write_str_multiple_data(self)
                for sql_execute in execute_str_list:
                    sqlite_database.write_to_sql_database(sql_execute)

    def _check_differences(self):
        differences = []
        try:
            self._update_sensor_readings_set()
            if self.trigger_data.num_of_readings == 1:
                previous_reading = self.reading_and_datetime_stamps[0][0]
                for reading in self.reading_and_datetime_stamps[0]:
                    if abs(float(reading) - float(previous_reading)) > self.trigger_data.variance:
                        return True
                    previous_reading = reading
            elif self.trigger_data.num_of_readings > 1:
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


def _get_trigger_state(reading, low_trigger, high_trigger):
    if reading < low_trigger:
        return low_state
    elif reading > high_trigger:
        return high_state
    return normal_state


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
