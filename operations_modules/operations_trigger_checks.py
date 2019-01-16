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
from datetime import datetime
from time import sleep

import operations_modules.operations_sensors as operations_sensors
from operations_modules import operations_logger
from operations_modules.operations_config import trigger_variances, trigger_pairs, current_config, installed_sensors, \
    database_variables
from operations_modules.operations_db import CreateTriggerDatabaseData, write_to_sql_database


def check_sensor_name():
    if trigger_variances.sensor_name:
        while True:
            trigger_data = CreateTriggerDatabaseData()

            trigger_data.variance = trigger_variances.sensor_name
            trigger_data.sql_columns_str += database_variables.sensor_name

            trigger_data.sql_readings1.append(operations_sensors.get_hostname())
            trigger_data.sql_readings1_datetime.append(get_datetime_stamp())

            sleep(trigger_variances.sensor_name_wait_seconds)

            trigger_data.sql_readings2.append(operations_sensors.get_hostname())
            trigger_data.sql_readings2_datetime.append(get_datetime_stamp())

            if trigger_data.sql_readings1[0] is not trigger_data.sql_readings2[0]:
                if current_config.write_to_db:
                    operations_logger.primary_logger.debug("Sensor Name Change Detected")
                    # Need to re-think, since every SQL write has name and IP automatically
                    # write_to_sql_database(trigger_data.get_sql_write_str())


def check_ip():
    if trigger_variances.ip:
        while True:
            trigger_data = CreateTriggerDatabaseData()

            trigger_data.variance = trigger_variances.ip
            trigger_data.sql_columns_str += database_variables.ip

            trigger_data.sql_readings1.append(operations_sensors.get_ip())
            trigger_data.sql_readings1_datetime.append(get_datetime_stamp())

            sleep(trigger_variances.ip_wait_seconds)

            trigger_data.sql_readings2.append(operations_sensors.get_ip())
            trigger_data.sql_readings2_datetime.append(get_datetime_stamp())

            if trigger_data.sql_readings1[0] is not trigger_data.sql_readings2[0]:
                if current_config.write_to_db:
                    operations_logger.primary_logger.debug("Sensor IP Change Detected")
                    # Need to re-think, since every SQL write has name and IP automatically
                    # write_to_sql_database(trigger_data.get_sql_write_str())


def check_sensor_uptime():
    if trigger_variances.sensor_uptime:
        loop_uptime = float(trigger_variances.sensor_uptime)
        while True:
            trigger_data = CreateTriggerDatabaseData()

            trigger_data.variance = loop_uptime
            trigger_data.sql_columns_str += database_variables.sensor_uptime

            trigger_data.sql_readings1.append(operations_sensors.get_system_uptime())
            trigger_data.sql_readings1_datetime.append(get_datetime_stamp())

            sleep(trigger_variances.sensor_uptime_wait_seconds)

            trigger_data.sql_readings2.append(operations_sensors.get_system_uptime())
            trigger_data.sql_readings2_datetime.append(get_datetime_stamp())

            if trigger_data.sql_readings2[0] > trigger_data.variance:
                loop_uptime = float(trigger_data.sql_readings2[0]) + float(trigger_variances.sensor_uptime)
                if current_config.write_to_db:
                    operations_logger.primary_logger.debug("Sensor Uptime Change Detected")
                    write_to_sql_database(trigger_data.get_sql_write_str())


def check_cpu_temperature():
    if trigger_variances.cpu_temperature:
        while True:
            trigger_data = CreateTriggerDatabaseData()

            trigger_data.variance = trigger_variances.cpu_temperature
            trigger_data.sql_columns_str += database_variables.system_temperature

            trigger_data.sql_readings1.append(operations_sensors.get_cpu_temperature())
            trigger_data.sql_readings1_datetime.append(get_datetime_stamp())

            sleep(trigger_variances.cpu_temperature_wait_seconds)

            trigger_data.sql_readings2.append(operations_sensors.get_cpu_temperature())
            trigger_data.sql_readings2_datetime.append(get_datetime_stamp())

            if trigger_data.sql_readings1[0] > trigger_data.variance or \
                    trigger_data.sql_readings2[0] > trigger_data.variance:
                if current_config.write_to_db:
                    operations_logger.primary_logger.debug("Sensor CPU Temperature exceeded set trigger")
                    write_to_sql_database(trigger_data.get_sql_write_str())


def check_env_temperature():
    if trigger_variances.env_temperature:
        while True:
            trigger_data = CreateTriggerDatabaseData()

            trigger_data.variance = trigger_variances.env_temperature
            trigger_data.sql_columns_str += database_variables.env_temperature

            trigger_data.sql_readings1.append(operations_sensors.get_sensor_temperature())
            trigger_data.sql_readings1_datetime.append(get_datetime_stamp())

            sleep(trigger_variances.env_temperature_wait_seconds)

            trigger_data.sql_readings2.append(operations_sensors.get_sensor_temperature())
            trigger_data.sql_readings2_datetime.append(get_datetime_stamp())

            if trigger_data.sql_readings1[0] > trigger_data.variance or \
                    trigger_data.sql_readings2[0] > trigger_data.variance:
                if current_config.write_to_db:
                    operations_logger.primary_logger.debug("Sensor Environment Temperature exceeded set trigger")
                    write_to_sql_database(trigger_data.get_sql_write_str())


def check_pressure():
    if trigger_variances.pressure:
        while True:
            trigger_data = CreateTriggerDatabaseData()

            trigger_data.variance = trigger_variances.pressure
            trigger_data.sql_columns_str += database_variables.pressure

            trigger_data.sql_readings1.append(operations_sensors.get_pressure())
            trigger_data.sql_readings1_datetime.append(get_datetime_stamp())

            sleep(trigger_variances.pressure_wait_seconds)

            trigger_data.sql_readings2.append(operations_sensors.get_pressure())
            trigger_data.sql_readings2_datetime.append(get_datetime_stamp())

            if trigger_data.sql_readings1[0] > trigger_data.variance or \
                    trigger_data.sql_readings2[0] > trigger_data.variance:
                if current_config.write_to_db:
                    operations_logger.primary_logger.debug("Sensor Pressure exceeded set trigger")
                    write_to_sql_database(trigger_data.get_sql_write_str())


def check_humidity():
    if trigger_variances.humidity:
        while True:
            trigger_data = CreateTriggerDatabaseData()

            trigger_data.variance = trigger_variances.humidity
            trigger_data.sql_columns_str += database_variables.humidity

            trigger_data.sql_readings1.append(operations_sensors.get_humidity())
            trigger_data.sql_readings1_datetime.append(get_datetime_stamp())

            sleep(trigger_variances.humidity_wait_seconds)

            trigger_data.sql_readings2.append(operations_sensors.get_humidity())
            trigger_data.sql_readings2_datetime.append(get_datetime_stamp())

            if trigger_data.sql_readings1[0] > trigger_data.variance or \
                    trigger_data.sql_readings2[0] > trigger_data.variance:
                if current_config.write_to_db:
                    operations_logger.primary_logger.debug("Sensor Humidity exceeded set trigger")
                    write_to_sql_database(trigger_data.get_sql_write_str())


def check_accelerometer_xyz():
    if installed_sensors.has_acc and trigger_variances.accelerometer:
        while True:
            x_trigger_data = CreateTriggerDatabaseData()
            y_trigger_data = CreateTriggerDatabaseData()
            z_trigger_data = CreateTriggerDatabaseData()

            x_trigger_data.variance = trigger_variances.accelerometer
            x_trigger_data.sql_columns_str += database_variables.acc_x
            y_trigger_data.variance = trigger_variances.accelerometer
            y_trigger_data.sql_columns_str += database_variables.acc_y
            z_trigger_data.variance = trigger_variances.accelerometer
            z_trigger_data.sql_columns_str += database_variables.acc_z

            pair_count = 0
            while pair_count < trigger_pairs:
                xyz = operations_sensors.get_accelerometer_xyz()

                x_trigger_data.sql_readings1.append(xyz[0])
                x_trigger_data.sql_readings1_datetime.append(get_datetime_stamp())
                y_trigger_data.sql_readings1.append(xyz[1])
                y_trigger_data.sql_readings1_datetime.append(get_datetime_stamp())
                z_trigger_data.sql_readings1.append(xyz[2])
                z_trigger_data.sql_readings1_datetime.append(get_datetime_stamp())

                sleep(trigger_variances.accelerometer_wait_seconds)

                xyz = operations_sensors.get_accelerometer_xyz()

                x_trigger_data.sql_readings2.append(xyz[0])
                x_trigger_data.sql_readings2_datetime.append(get_datetime_stamp())
                y_trigger_data.sql_readings2.append(xyz[1])
                y_trigger_data.sql_readings2_datetime.append(get_datetime_stamp())
                z_trigger_data.sql_readings2.append(xyz[2])
                z_trigger_data.sql_readings2_datetime.append(get_datetime_stamp())

                pair_count += 1

            _check_against_variance(x_trigger_data)
            _check_against_variance(y_trigger_data)
            _check_against_variance(z_trigger_data)
    else:
        operations_logger.primary_logger.debug("Accelerometer checks disabled in variances configuration file")


def check_magnetometer_xyz():
    if installed_sensors.has_mag and trigger_variances.magnetometer:
        while True:
            x_trigger_data = CreateTriggerDatabaseData()
            y_trigger_data = CreateTriggerDatabaseData()
            z_trigger_data = CreateTriggerDatabaseData()

            x_trigger_data.variance = trigger_variances.magnetometer
            x_trigger_data.sql_columns_str += database_variables.mag_x
            y_trigger_data.variance = trigger_variances.magnetometer
            y_trigger_data.sql_columns_str += database_variables.mag_y
            z_trigger_data.variance = trigger_variances.magnetometer
            z_trigger_data.sql_columns_str += database_variables.mag_z

            pair_count = 0
            while pair_count < trigger_pairs:
                xyz = operations_sensors.get_magnetometer_xyz()

                x_trigger_data.sql_readings1.append(xyz[0])
                x_trigger_data.sql_readings1_datetime.append(get_datetime_stamp())
                y_trigger_data.sql_readings1.append(xyz[1])
                y_trigger_data.sql_readings1_datetime.append(get_datetime_stamp())
                z_trigger_data.sql_readings1.append(xyz[2])
                z_trigger_data.sql_readings1_datetime.append(get_datetime_stamp())

                sleep(trigger_variances.magnetometer_wait_seconds)

                xyz = operations_sensors.get_magnetometer_xyz()

                x_trigger_data.sql_readings2.append(xyz[0])
                x_trigger_data.sql_readings2_datetime.append(get_datetime_stamp())
                y_trigger_data.sql_readings2.append(xyz[1])
                y_trigger_data.sql_readings2_datetime.append(get_datetime_stamp())
                z_trigger_data.sql_readings2.append(xyz[2])
                z_trigger_data.sql_readings2_datetime.append(get_datetime_stamp())

                pair_count += 1

            _check_against_variance(x_trigger_data)
            _check_against_variance(y_trigger_data)
            _check_against_variance(z_trigger_data)
    else:
        operations_logger.primary_logger.debug("Magnetometer checks disabled in variances configuration file")


def check_gyroscope_xyz():
    if installed_sensors.has_gyro and trigger_variances.gyroscope:
        while True:
            x_trigger_data = CreateTriggerDatabaseData()
            y_trigger_data = CreateTriggerDatabaseData()
            z_trigger_data = CreateTriggerDatabaseData()

            x_trigger_data.variance = trigger_variances.gyroscope
            x_trigger_data.sql_columns_str += database_variables.gyro_x
            y_trigger_data.variance = trigger_variances.gyroscope
            y_trigger_data.sql_columns_str += database_variables.gyro_y
            z_trigger_data.variance = trigger_variances.gyroscope
            z_trigger_data.sql_columns_str += database_variables.gyro_z

            pair_count = 0
            while pair_count < trigger_pairs:
                xyz = operations_sensors.get_gyroscope_xyz()

                x_trigger_data.sql_readings1.append(xyz[0])
                x_trigger_data.sql_readings1_datetime.append(get_datetime_stamp())
                y_trigger_data.sql_readings1.append(xyz[1])
                y_trigger_data.sql_readings1_datetime.append(get_datetime_stamp())
                z_trigger_data.sql_readings1.append(xyz[2])
                z_trigger_data.sql_readings1_datetime.append(get_datetime_stamp())

                sleep(trigger_variances.gyroscope_wait_seconds)

                xyz = operations_sensors.get_gyroscope_xyz()

                x_trigger_data.sql_readings2.append(xyz[0])
                x_trigger_data.sql_readings2_datetime.append(get_datetime_stamp())
                y_trigger_data.sql_readings2.append(xyz[1])
                y_trigger_data.sql_readings2_datetime.append(get_datetime_stamp())
                z_trigger_data.sql_readings2.append(xyz[2])
                z_trigger_data.sql_readings2_datetime.append(get_datetime_stamp())

                pair_count += 1

            _check_against_variance(x_trigger_data)
            _check_against_variance(y_trigger_data)
            _check_against_variance(z_trigger_data)
    else:
        operations_logger.primary_logger.debug("Gyroscopic checks disabled in variances configuration file")


def _check_against_variance(trigger_data):
    write_to_db = False
    pair_differences = []

    count = 0
    for reading in trigger_data.sql_readings1:
        readings_old = reading
        readings_new = trigger_data.sql_readings2[count]
        try:
            difference = abs(abs(float(readings_new)) - abs(float(readings_old)))
            pair_differences.append(difference)
        except Exception as error:
            operations_logger.primary_logger.error("Bad readings in Single variance checks: " + str(error))
            write_to_db = False
        count += 1

    for difference in pair_differences:
        if difference >= trigger_data.variance:
            write_to_db = True

    if write_to_db:
        operations_logger.primary_logger.debug("Pair Differences: " + str(pair_differences))
        sql_db_executes = trigger_data.get_sql_write_str()

        for execute in sql_db_executes:
            write_to_sql_database(execute)


def get_datetime_stamp():
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
