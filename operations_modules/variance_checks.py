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
import socket
from time import sleep
from datetime import datetime
from operations_modules import logger
from operations_modules import configuration_main
from operations_modules import sqlite_database


class CreateTriggerDatabaseData:
    """ Creates a object, holding required data for making a Trigger SQL execute string. """

    def __init__(self, sensor_database_variable):
        self.variance = 99999.99

        if configuration_main.installed_sensors.linux_system:
            self.sql_columns_str = "DateTime,SensorName,IP," + sensor_database_variable
        else:
            self.sql_columns_str_start = "DateTime," + sensor_database_variable

        self.sql_sensor_name = _get_hostname()
        self.sql_ip = _get_ip()
        self.sensor_wait_seconds = ""
        self.sensor_type = ""

        self.reading_and_datetime_stamps = []


class CreateSensorCommands:
    """ Create a object instance holding available network "Get" commands (AKA expecting data back). """

    def __init__(self):
        self.sensor_name = "GetHostName"
        self.system_uptime = "GetSystemUptime"
        self.cpu_temp = "GetCPUTemperature"
        self.environmental_temp = "GetEnvTemperature"
        self.env_temp_offset = "GetTempOffsetEnv"
        self.pressure = "GetPressure"
        self.altitude = "GetAltitude"
        self.humidity = "GetHumidity"
        self.distance = "GetDistance"
        self.gas = "GetAllGas"
        self.lumen = "GetLumen"
        self.electromagnetic_spectrum = "GetEMS"
        self.ultra_violet = "GetAllUltraViolet"
        self.accelerometer_xyz = "GetAccelerometerXYZ"
        self.magnetometer_xyz = "GetMagnetometerXYZ"
        self.gyroscope_xyz = "GetGyroscopeXYZ"
        self.display_text = "DisplayText"


class CreateVarianceRecording:
    def __init__(self, sensor_access):
        self.sensor_types = CreateSensorCommands()
        self.number_of_sets = 2
        self.sensor_access = sensor_access

    def check_sensor_uptime(self):
        """ If enabled, writes sensor uptime to SQL trigger database per the variance setting. """
        if configuration_main.trigger_variances.sensor_uptime_enabled and \
                configuration_main.current_config.enable_trigger_recording:

            trigger_object = CreateTriggerDatabaseData(configuration_main.database_variables.sensor_uptime)
            sensor_wait_seconds = configuration_main.trigger_variances.sensor_uptime_wait_seconds
            sensor_type = self.sensor_types.system_uptime

            while True:
                trigger_object.reading_and_datetime_stamps = self._get_sensor_readings_set(sensor_type,
                                                                                           sensor_wait_seconds)

                execute_str_list = self._readings_to_sql_write_str_single_data(trigger_object)
                sqlite_database.write_to_sql_database(execute_str_list[0])
                logger.primary_logger.debug("Sensor Uptime exceeded set trigger")

    def check_cpu_temperature(self):
        """ If enabled, writes CPU temperature to SQL trigger database per the variance setting. """
        if configuration_main.installed_sensors.has_cpu_temperature and \
                configuration_main.trigger_variances.cpu_temperature_enabled and \
                configuration_main.current_config.enable_trigger_recording:
            trigger_object = CreateTriggerDatabaseData(configuration_main.database_variables.system_temperature)
            trigger_object.variance = configuration_main.trigger_variances.cpu_temperature_variance
            trigger_object.sensor_wait_seconds = configuration_main.trigger_variances.cpu_temperature_wait_seconds
            trigger_object.sensor_type = self.sensor_types.cpu_temp

            self._universal_single_data_check(trigger_object)

    def check_env_temperature(self):
        """ If enabled, writes sensor temperature to SQL trigger database per the variance setting. """
        if configuration_main.installed_sensors.has_env_temperature and \
                configuration_main.trigger_variances.env_temperature_enabled and \
                configuration_main.current_config.enable_trigger_recording:
            trigger_object = CreateTriggerDatabaseData(configuration_main.database_variables.env_temperature)
            trigger_object.variance = configuration_main.trigger_variances.env_temperature_variance
            trigger_object.sensor_wait_seconds = configuration_main.trigger_variances.env_temperature_wait_seconds
            trigger_object.sensor_type = self.sensor_types.environmental_temp

            self._universal_single_data_check(trigger_object)

    def check_pressure(self):
        """ If enabled, writes pressure to SQL trigger database per the variance setting. """
        if configuration_main.installed_sensors.has_pressure and \
                configuration_main.trigger_variances.pressure_enabled and \
                configuration_main.current_config.enable_trigger_recording:
            trigger_object = CreateTriggerDatabaseData(configuration_main.database_variables.pressure)
            trigger_object.variance = configuration_main.trigger_variances.pressure_variance
            trigger_object.sensor_wait_seconds = configuration_main.trigger_variances.pressure_wait_seconds
            trigger_object.sensor_type = self.sensor_types.pressure

            self._universal_single_data_check(trigger_object)

    def check_altitude(self):
        """ If enabled, writes altitude to SQL trigger database per the variance setting. """
        if configuration_main.current_config.enable_trigger_recording and \
                configuration_main.trigger_variances.altitude_enabled and \
                configuration_main.installed_sensors.has_altitude:
            trigger_object = CreateTriggerDatabaseData(configuration_main.database_variables.altitude)
            trigger_object.variance = configuration_main.trigger_variances.altitude_variance
            trigger_object.sensor_wait_seconds = configuration_main.trigger_variances.altitude_wait_seconds
            trigger_object.sensor_type = self.sensor_types.altitude

            self._universal_single_data_check(trigger_object)

    def check_humidity(self):
        """ If enabled, writes humidity to SQL trigger database per the variance setting. """
        if configuration_main.installed_sensors.has_humidity and \
                configuration_main.trigger_variances.humidity_enabled and \
                configuration_main.current_config.enable_trigger_recording:
            trigger_object = CreateTriggerDatabaseData(configuration_main.database_variables.humidity)
            trigger_object.variance = configuration_main.trigger_variances.humidity_variance
            trigger_object.sensor_wait_seconds = configuration_main.trigger_variances.humidity_wait_seconds
            trigger_object.sensor_type = self.sensor_types.humidity

            self._universal_single_data_check(trigger_object)

    def check_distance(self):
        """ If enabled, writes distance to SQL trigger database per the variance setting. """
        if configuration_main.installed_sensors.has_distance and \
                configuration_main.trigger_variances.distance_enabled and \
                configuration_main.current_config.enable_trigger_recording:
            trigger_object = CreateTriggerDatabaseData(configuration_main.database_variables.distance)
            trigger_object.variance = configuration_main.trigger_variances.distance_variance
            trigger_object.sensor_wait_seconds = configuration_main.trigger_variances.distance_wait_seconds
            trigger_object.sensor_type = self.sensor_types.distance

            self._universal_single_data_check(trigger_object)

    def check_lumen(self):
        """ If enabled, writes lumen to SQL trigger database per the variance setting. """
        if configuration_main.installed_sensors.has_lumen and \
                configuration_main.trigger_variances.lumen_enabled and \
                configuration_main.current_config.enable_trigger_recording:
            trigger_object = CreateTriggerDatabaseData(configuration_main.database_variables.lumen)
            trigger_object.variance = configuration_main.trigger_variances.lumen_variance
            trigger_object.sensor_wait_seconds = configuration_main.trigger_variances.lumen_wait_seconds
            trigger_object.sensor_type = self.sensor_types.lumen

            self._universal_single_data_check(trigger_object)

    def check_ems(self):
        """ If enabled, writes available colours (Electromagnetic Spectrum) to SQL trigger database per the variance setting. """
        if configuration_main.current_config.enable_trigger_recording:
            if configuration_main.installed_sensors.has_violet:
                database_sensor_variable = configuration_main.database_variables.red + "," + \
                                           configuration_main.database_variables.orange + "," + \
                                           configuration_main.database_variables.yellow + "," + \
                                           configuration_main.database_variables.green + "," + \
                                           configuration_main.database_variables.blue + "," + \
                                           configuration_main.database_variables.violet

                trigger_object = CreateTriggerDatabaseData(database_sensor_variable)
                trigger_object.variance = [configuration_main.trigger_variances.red_variance,
                                           configuration_main.trigger_variances.orange_variance,
                                           configuration_main.trigger_variances.yellow_variance,
                                           configuration_main.trigger_variances.green_variance,
                                           configuration_main.trigger_variances.blue_variance,
                                           configuration_main.trigger_variances.violet_variance]
                trigger_object.sensor_wait_seconds = configuration_main.trigger_variances.colour_wait_seconds
                trigger_object.sensor_type = self.sensor_types.electromagnetic_spectrum

                self._universal_sextuple_data_check(trigger_object)
            elif configuration_main.installed_sensors.has_red:
                database_sensor_variable = configuration_main.database_variables.red + "," + \
                                           configuration_main.database_variables.green + "," + \
                                           configuration_main.database_variables.blue

                trigger_object = CreateTriggerDatabaseData(database_sensor_variable)
                trigger_object.variance = [configuration_main.trigger_variances.red_variance,
                                           configuration_main.trigger_variances.green_variance,
                                           configuration_main.trigger_variances.blue_variance]
                trigger_object.sensor_wait_seconds = configuration_main.trigger_variances.colour_wait_seconds
                trigger_object.sensor_type = self.sensor_types.electromagnetic_spectrum

                self._universal_triple_data_check(trigger_object)
            else:
                pass

    def check_accelerometer_xyz(self):
        """ If enabled, writes Acceleration to SQL trigger database per the variance setting. """
        if configuration_main.installed_sensors.has_acc and \
                configuration_main.trigger_variances.accelerometer_enabled and \
                configuration_main.current_config.enable_trigger_recording:
            database_sensor_variable = configuration_main.database_variables.acc_x + "," + \
                                       configuration_main.database_variables.acc_y + "," + \
                                       configuration_main.database_variables.acc_z

            trigger_object = CreateTriggerDatabaseData(database_sensor_variable)
            trigger_object.variance = [configuration_main.trigger_variances.accelerometer_x_variance,
                                       configuration_main.trigger_variances.accelerometer_y_variance,
                                       configuration_main.trigger_variances.accelerometer_z_variance]
            trigger_object.sensor_wait_seconds = configuration_main.trigger_variances.accelerometer_wait_seconds
            trigger_object.sensor_type = self.sensor_types.accelerometer_xyz

            self._universal_triple_data_check(trigger_object)

    def check_magnetometer_xyz(self):
        """ If enabled, writes Magnetometer to SQL trigger database per the variance setting. """
        if configuration_main.installed_sensors.has_mag and \
                configuration_main.trigger_variances.magnetometer_enabled and \
                configuration_main.current_config.enable_trigger_recording:
            database_sensor_variable = configuration_main.database_variables.mag_x + "," + \
                                       configuration_main.database_variables.mag_y + "," + \
                                       configuration_main.database_variables.mag_z

            trigger_object = CreateTriggerDatabaseData(database_sensor_variable)
            trigger_object.variance = [configuration_main.trigger_variances.magnetometer_x_variance,
                                       configuration_main.trigger_variances.magnetometer_y_variance,
                                       configuration_main.trigger_variances.magnetometer_z_variance]
            trigger_object.sensor_wait_seconds = configuration_main.trigger_variances.magnetometer_wait_seconds
            trigger_object.sensor_type = self.sensor_types.magnetometer_xyz

            self._universal_triple_data_check(trigger_object)

    def check_gyroscope_xyz(self):
        """ If enabled, writes Gyroscope to SQL trigger database per the variance setting. """
        if configuration_main.installed_sensors.has_gyro and \
                configuration_main.trigger_variances.gyroscope_enabled and \
                configuration_main.current_config.enable_trigger_recording:
            database_sensor_variable = configuration_main.database_variables.gyro_x + "," + \
                                       configuration_main.database_variables.gyro_y + "," + \
                                       configuration_main.database_variables.gyro_z

            trigger_object = CreateTriggerDatabaseData(database_sensor_variable)
            trigger_object.variance = [configuration_main.trigger_variances.gyroscope_x_variance,
                                       configuration_main.trigger_variances.gyroscope_y_variance,
                                       configuration_main.trigger_variances.gyroscope_z_variance]
            trigger_object.sensor_wait_seconds = configuration_main.trigger_variances.gyroscope_wait_seconds
            trigger_object.sensor_type = self.sensor_types.gyroscope_xyz

            self._universal_triple_data_check(trigger_object)

    def get_sensor_reading(self, sensor_type):
        if sensor_type == self.sensor_types.sensor_name:
            return_data = self.sensor_access.get_hostname()
        elif sensor_type == self.sensor_types.system_uptime:
            return_data = self.sensor_access.get_uptime_minutes()
        elif sensor_type == self.sensor_types.cpu_temp:
            return_data = self.sensor_access.get_cpu_temperature()
        elif sensor_type == self.sensor_types.environmental_temp:
            return_data = self.sensor_access.get_sensor_temperature()
        elif sensor_type == self.sensor_types.env_temp_offset:
            return_data = configuration_main.current_config.temperature_offset
        elif sensor_type == self.sensor_types.pressure:
            return_data = self.sensor_access.get_pressure()
        elif sensor_type == self.sensor_types.altitude:
            return_data = self.sensor_access.get_altitude()
        elif sensor_type == self.sensor_types.humidity:
            return_data = self.sensor_access.get_humidity()
        elif sensor_type == self.sensor_types.distance:
            return_data = self.sensor_access.get_distance()
        elif sensor_type == self.sensor_types.gas:
            get_resistance_index = self.sensor_access.get_gas_resistance_index()
            get_resistance_oxidised = self.sensor_access.get_gas_resistance_index()
            get_resistance_reduced = self.sensor_access.get_gas_resistance_index()
            get_resistance_nh3 = self.sensor_access.get_gas_resistance_index()
            return_data = get_resistance_index, get_resistance_oxidised, get_resistance_reduced, get_resistance_nh3
        elif sensor_type == self.sensor_types.lumen:
            return_data = self.sensor_access.get_lumen()
        elif sensor_type == self.sensor_types.electromagnetic_spectrum:
            return_data = self.sensor_access.get_ems()
        elif sensor_type == self.sensor_types.ultra_violet:
            ultra_violet_a = self.sensor_access.get_ultra_violet_a()
            ultra_violet_b = self.sensor_access.get_ultra_violet_b()
            return_data = ultra_violet_a, ultra_violet_b
        elif sensor_type == self.sensor_types.accelerometer_xyz:
            return_data = self.sensor_access.get_accelerometer_xyz()
        elif sensor_type == self.sensor_types.magnetometer_xyz:
            return_data = self.sensor_access.get_magnetometer_xyz()
        elif sensor_type == self.sensor_types.gyroscope_xyz:
            return_data = self.sensor_access.get_gyroscope_xyz()
        else:
            return_data = "Unknown Sensor Request"

        return str(return_data)

    @staticmethod
    def get_datetime_stamp():
        """ Returns current UTC 0 time as a string "%Y-%m-%d %H:%M:%S.%f". """
        return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

    def _get_sensor_readings_set(self, sensor_type, sensor_wait_seconds):
        """ Sends provided string to retrieve sensor data. """
        sensor_reading = []
        datetime_stamps = []

        count = 0
        while count < self.number_of_sets:
            try:
                sensor_reading.append(self.get_sensor_reading(sensor_type))
                logger.primary_logger.debug("Sensor data retrieval OK for: " + sensor_type)
            except Exception as error:
                logger.primary_logger.warning("Sensor data retrieval Failed: " + str(error))
                sensor_reading.append("Failed")

            datetime_stamps.append(self.get_datetime_stamp())
            count += 1
            sleep(sensor_wait_seconds)

        return [sensor_reading, datetime_stamps]

    def _universal_single_data_check(self, trigger_object):
        while True:
            reading_and_datetime_stamps = self._get_sensor_readings_set(trigger_object.sensor_type,
                                                                        trigger_object.sensor_wait_seconds)

            count = 0
            variance_detected = False
            while count < self.number_of_sets:
                try:
                    difference = abs(float(reading_and_datetime_stamps[0][0]) -
                                     float(reading_and_datetime_stamps[0][1]))
                except Exception as error:
                    logger.primary_logger.warning(trigger_object.sensor_type + " Trigger: " + str(error))
                    difference = 0.0

                if difference > trigger_object.variance:
                    # logger.primary_logger.warning(trigger_object.sensor_type + " exceeded set trigger")
                    variance_detected = True

                if variance_detected:
                    trigger_object.reading_and_datetime_stamps = reading_and_datetime_stamps
                    execute_str_list = self._readings_to_sql_write_str_single_data(trigger_object)
                    for sql_execute in execute_str_list:
                        sqlite_database.write_to_sql_database(sql_execute)
                count += 1

    def _universal_triple_data_check(self, trigger_object):
        logger.primary_logger.info(trigger_object.sensor_type + " Starting Checks.  Checking every " +
                                      str(trigger_object.sensor_wait_seconds) + " Seconds")
        while True:
            reading_and_datetime_stamps = self._get_sensor_readings_set(trigger_object.sensor_type,
                                                                            trigger_object.sensor_wait_seconds)

            count = 0
            variance_detected = False
            while count < self.number_of_sets:
                try:
                    difference1 = abs(float(reading_and_datetime_stamps[0][0][1:-1].split(",")[0]) -
                                      float(reading_and_datetime_stamps[0][1][1:-1].split(",")[0]))

                    difference2 = abs(float(reading_and_datetime_stamps[0][0][1:-1].split(",")[1]) -
                                      float(reading_and_datetime_stamps[0][1][1:-1].split(",")[1]))

                    difference3 = abs(float(reading_and_datetime_stamps[0][0][1:-1].split(",")[2]) -
                                      float(reading_and_datetime_stamps[0][1][1:-1].split(",")[2]))
                except Exception as error:
                    logger.primary_logger.warning(trigger_object.sensor_type + " Trigger: " + str(error))
                    difference1 = 0.0
                    difference2 = 0.0
                    difference3 = 0.0

                # logger.primary_logger.warning(trigger_object.sensor_type + " difference1: " + str(difference1))
                # logger.primary_logger.warning(trigger_object.sensor_type + " difference2: " + str(difference2))
                # logger.primary_logger.warning(trigger_object.sensor_type + " difference3: " + str(difference3))

                try:
                    if difference1 > trigger_object.variance[0]:
                        # logger.primary_logger.warning(trigger_object.sensor_type + " 'X' exceeded set trigger")
                        variance_detected = True
                    if difference2 > trigger_object.variance[1]:
                        # logger.primary_logger.warning(trigger_object.sensor_type + " 'Y' exceeded set trigger")
                        variance_detected = True
                    if difference3 > trigger_object.variance[2]:
                        # logger.primary_logger.warning(trigger_object.sensor_type + " 'Z' exceeded set trigger")
                        variance_detected = True
                except Exception as error:
                    variance_detected = False
                    logger.primary_logger.error(trigger_object.sensor_type +
                                                " Trigger difference Failed: " +
                                                str(error))

                try:
                    if variance_detected:
                        trigger_object.reading_and_datetime_stamps = reading_and_datetime_stamps
                        execute_str_list = self._readings_to_sql_write_str_triple_data(trigger_object)
                        for sql_execute in execute_str_list:
                            sqlite_database.write_to_sql_database(sql_execute)
                except Exception as error:
                    logger.primary_logger.warning(trigger_object.sensor_type +
                                                  " Trigger DB Write Failed: " +
                                                  str(error))
                count += 1

    def _universal_sextuple_data_check(self, trigger_object):
        while True:
            reading_and_datetime_stamps = self._get_sensor_readings_set(trigger_object.sensor_type,
                                                                        trigger_object.sensor_wait_seconds)

            count = 0
            variance_detected = False
            while count < self.number_of_sets:
                try:
                    difference1 = abs(float(reading_and_datetime_stamps[0][0][0]) -
                                      float(reading_and_datetime_stamps[0][1][0]))

                    difference2 = abs(float(reading_and_datetime_stamps[0][0][1]) -
                                      float(reading_and_datetime_stamps[0][1][1]))

                    difference3 = abs(float(reading_and_datetime_stamps[0][0][2]) -
                                      float(reading_and_datetime_stamps[0][1][2]))

                    difference4 = abs(float(reading_and_datetime_stamps[0][0][3]) -
                                      float(reading_and_datetime_stamps[0][1][3]))

                    difference5 = abs(float(reading_and_datetime_stamps[0][0][4]) -
                                      float(reading_and_datetime_stamps[0][1][4]))

                    difference6 = abs(float(reading_and_datetime_stamps[0][0][5]) -
                                      float(reading_and_datetime_stamps[0][1][5]))
                except Exception as error:
                    logger.primary_logger.warning(trigger_object.sensor_type + " Trigger: " + str(error))
                    difference1 = 0.0
                    difference2 = 0.0
                    difference3 = 0.0
                    difference4 = 0.0
                    difference5 = 0.0
                    difference6 = 0.0

                if difference1 > trigger_object.variance[0]:
                    # logger.primary_logger.debug(trigger_object.sensor_type + " '1 or x' exceeded set trigger")
                    variance_detected = True
                if difference2 > trigger_object.variance[1]:
                    # logger.primary_logger.debug(trigger_object.sensor_type + " '2 or y' exceeded set trigger")
                    variance_detected = True
                if difference3 > trigger_object.variance[2]:
                    # logger.primary_logger.debug(trigger_object.sensor_type + " '3 or z' exceeded set trigger")
                    variance_detected = True
                if difference4 > trigger_object.variance[3]:
                    # logger.primary_logger.debug(trigger_object.sensor_type + " '4' exceeded set trigger")
                    variance_detected = True
                if difference5 > trigger_object.variance[4]:
                    # logger.primary_logger.debug(trigger_object.sensor_type + " '5' exceeded set trigger")
                    variance_detected = True
                if difference6 > trigger_object.variance[5]:
                    # logger.primary_logger.debug(trigger_object.sensor_type + " '6' exceeded set trigger")
                    variance_detected = True

                if variance_detected:
                    trigger_object.reading_and_datetime_stamps = reading_and_datetime_stamps
                    execute_str_list = self._readings_to_sql_write_str_sextuple_data(trigger_object)
                    for sql_execute in execute_str_list:
                        sqlite_database.write_to_sql_database(sql_execute)
                count += 1

    @staticmethod
    def _readings_to_sql_write_str_single_data(trigger_object):
        """ Takes a Sensor Data Set as input and returns a string for writing the readings to the SQLite Database. """
        sql_query_start = "INSERT OR IGNORE INTO TriggerData ("
        sql_query_values_start = ") VALUES ("
        sql_query_values_end = ")"

        sql_execute_list = []

        count = 0
        for reading in trigger_object.reading_and_datetime_stamps[0]:
            if configuration_main.installed_sensors.linux_system:
                sql_execute_list.append(sql_query_start +
                                        trigger_object.sql_columns_str +
                                        sql_query_values_start + "'" +
                                        trigger_object.reading_and_datetime_stamps[1][count] + "','" +
                                        trigger_object.sql_sensor_name + "','" +
                                        trigger_object.sql_ip + "','" +
                                        reading + "'" +
                                        sql_query_values_end)
            else:
                sql_execute_list.append(sql_query_start +
                                        trigger_object.sql_columns_str +
                                        sql_query_values_start + "'" +
                                        trigger_object.reading_and_datetime_stamps[1][count] + "','" +
                                        reading + "'" +
                                        sql_query_values_end)

            count += 1

        return sql_execute_list

    @staticmethod
    def _readings_to_sql_write_str_triple_data(trigger_object):
        """ Takes a Sensor Data Set as input and returns a string for writing the readings to the SQLite Database. """
        sql_query_start = "INSERT OR IGNORE INTO TriggerData ("
        sql_query_values_start = ") VALUES ("
        sql_query_values_end = ")"

        sql_execute_list = []

        count = 0
        for reading in trigger_object.reading_and_datetime_stamps[0]:
            x, y, z = reading[1:-1].split(",")

            if configuration_main.installed_sensors.linux_system:
                sql_execute_list.append(sql_query_start +
                                        trigger_object.sql_columns_str +
                                        sql_query_values_start + "'" +
                                        trigger_object.reading_and_datetime_stamps[1][count] + "','" +
                                        trigger_object.sql_sensor_name + "','" +
                                        trigger_object.sql_ip + "','" +
                                        x + "','" +
                                        y + "','" +
                                        z + "'" +
                                        sql_query_values_end)
            else:
                sql_execute_list.append(sql_query_start +
                                        trigger_object.sql_columns_str +
                                        sql_query_values_start + "'" +
                                        trigger_object.reading_and_datetime_stamps[1][count] + "','" +
                                        x + "','" +
                                        y + "','" +
                                        z + "'" +
                                        sql_query_values_end)

            count += 1

        return sql_execute_list

    @staticmethod
    def _readings_to_sql_write_str_sextuple_data(trigger_object):
        """ Takes a Sensor Data Set as input and returns a string for writing the readings to the SQLite Database. """
        sql_query_start = "INSERT OR IGNORE INTO TriggerData ("
        sql_query_values_start = ") VALUES ("
        sql_query_values_end = ")"

        sql_execute_list = []

        count = 0
        for reading in trigger_object.reading_and_datetime_stamps[0]:
            data_1, data_2, data_3, data_4, data_5, data_6 = reading[1:-1].split(",")

            if configuration_main.installed_sensors.linux_system:
                sql_execute_list.append(sql_query_start +
                                        trigger_object.sql_columns_str +
                                        sql_query_values_start + "'" +
                                        trigger_object.reading_and_datetime_stamps[1][count] + "','" +
                                        trigger_object.sql_sensor_name + "','" +
                                        trigger_object.sql_ip + "','" +
                                        data_1 + "','" +
                                        data_2 + "','" +
                                        data_3 + "','" +
                                        data_4 + "','" +
                                        data_5 + "','" +
                                        data_6 + "'" +
                                        sql_query_values_end)
            else:
                sql_execute_list.append(sql_query_start +
                                        trigger_object.sql_columns_str +
                                        sql_query_values_start + "'" +
                                        trigger_object.reading_and_datetime_stamps[1][count] + "','" +
                                        data_1 + "','" +
                                        data_2 + "','" +
                                        data_3 + "','" +
                                        data_4 + "','" +
                                        data_5 + "','" +
                                        data_6 + "'" +
                                        sql_query_values_end)

            count += 1

        return sql_execute_list


def _get_ip():
    ip_address = "0.0.0.0"
    if configuration_main.installed_sensors.linux_system:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip_address = (s.getsockname()[0])
            logger.sensors_logger.debug("Sensor IP Retrieval - OK")
        except Exception as error:
            logger.sensors_logger.error("Sensor IP Retrieval - Failed - " + str(error))
    return ip_address


def _get_hostname():
    hostname = "Invalid"
    if configuration_main.installed_sensors.linux_system:
        try:
            hostname = str(socket.gethostname())
            logger.sensors_logger.debug("Sensor Hostname Retrieval - OK")
        except Exception as error:
            logger.sensors_logger.error("Sensor Hostname Retrieval - Failed - " + str(error))
    return hostname
