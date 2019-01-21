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
from operations_modules.operations_config import trigger_variances, current_config, installed_sensors, \
    database_variables
from operations_modules.operations_db import CreateTriggerDatabaseData, write_to_sql_database
from operations_modules.operations_variables import trigger_pairs


def check_sensor_uptime():
    if trigger_variances.sensor_uptime_enabled and current_config.enable_trigger_recording:
        while True:
            trigger_data = CreateTriggerDatabaseData()
            trigger_data.sql_columns_str += database_variables.sensor_uptime

            trigger_data.sql_readings1.append(operations_sensors.get_system_uptime())
            trigger_data.sql_readings1_datetime.append(get_datetime_stamp())

            sleep(trigger_variances.sensor_uptime_wait_seconds)

            trigger_data.sql_readings2.append(operations_sensors.get_system_uptime())
            trigger_data.sql_readings2_datetime.append(get_datetime_stamp())

            operations_logger.primary_logger.debug("Sensor Uptime exceeded set trigger")
            for execute in trigger_data.get_sql_write_str():
                write_to_sql_database(execute)


def check_cpu_temperature():
    if installed_sensors.has_cpu_temperature and trigger_variances.cpu_temperature_enabled and current_config.enable_trigger_recording:
        while True:
            trigger_data = CreateTriggerDatabaseData()

            trigger_data.variance = trigger_variances.cpu_temperature_variance
            trigger_data.sql_columns_str += database_variables.system_temperature

            try:
                trigger_data.sql_readings1.append(operations_sensors.get_cpu_temperature())
            except Exception as error:
                operations_logger.primary_logger.warning("Get CPU Temperature Error: " + str(error))
                trigger_data.sql_readings1.append("0")
            trigger_data.sql_readings1_datetime.append(get_datetime_stamp())

            sleep(trigger_variances.cpu_temperature_wait_seconds)

            try:
                trigger_data.sql_readings2.append(operations_sensors.get_cpu_temperature())
            except Exception as error:
                operations_logger.primary_logger.warning("Get CPU Temperature Error: " + str(error))
                trigger_data.sql_readings1.append("0")
            trigger_data.sql_readings2_datetime.append(get_datetime_stamp())

            try:
                difference = abs(float(trigger_data.sql_readings1[0]) - float(trigger_data.sql_readings2[0]))
            except Exception as error:
                operations_logger.primary_logger.warning("CPU Temperature Trigger: " + str(error))
                difference = 0.0

            if difference > trigger_data.variance:
                operations_logger.primary_logger.debug("CPU Temperature exceeded set trigger")
                for execute in trigger_data.get_sql_write_str():
                    write_to_sql_database(execute)


def check_env_temperature():
    if installed_sensors.has_env_temperature and trigger_variances.env_temperature_enabled and current_config.enable_trigger_recording:
        while True:
            trigger_data = CreateTriggerDatabaseData()

            trigger_data.variance = trigger_variances.env_temperature_variance
            trigger_data.sql_columns_str += database_variables.env_temperature

            try:
                trigger_data.sql_readings1.append(operations_sensors.get_sensor_temperature())
            except Exception as error:
                operations_logger.primary_logger.warning("Get Env Temperature Error: " + str(error))
                trigger_data.sql_readings1.append("0")
            trigger_data.sql_readings1_datetime.append(get_datetime_stamp())

            sleep(trigger_variances.env_temperature_wait_seconds)

            try:
                trigger_data.sql_readings2.append(operations_sensors.get_sensor_temperature())
            except Exception as error:
                operations_logger.primary_logger.warning("Get Env Temperature Error: " + str(error))
                trigger_data.sql_readings1.append("0")
            trigger_data.sql_readings2_datetime.append(get_datetime_stamp())

            try:
                difference = abs(float(trigger_data.sql_readings1[0]) - float(trigger_data.sql_readings2[0]))
            except Exception as error:
                operations_logger.primary_logger.warning("Env Temperature Trigger: " + str(error))
                difference = 0.0

            if difference > trigger_data.variance:
                operations_logger.primary_logger.debug("Environment Temperature exceeded set trigger")
                for execute in trigger_data.get_sql_write_str():
                    write_to_sql_database(execute)


def check_pressure():
    if installed_sensors.has_pressure and trigger_variances.pressure_enabled and current_config.enable_trigger_recording:
        while True:
            trigger_data = CreateTriggerDatabaseData()

            trigger_data.variance = trigger_variances.pressure_variance
            trigger_data.sql_columns_str += database_variables.pressure

            try:
                trigger_data.sql_readings1.append(operations_sensors.get_pressure())
            except Exception as error:
                operations_logger.primary_logger.warning("Get Pressure Error: " + str(error))
                trigger_data.sql_readings1.append("0")
            trigger_data.sql_readings1_datetime.append(get_datetime_stamp())

            sleep(trigger_variances.pressure_wait_seconds)

            try:
                trigger_data.sql_readings2.append(operations_sensors.get_pressure())
            except Exception as error:
                operations_logger.primary_logger.warning("Get Pressure Error: " + str(error))
                trigger_data.sql_readings1.append("0")
            trigger_data.sql_readings2_datetime.append(get_datetime_stamp())

            try:
                difference = abs(float(trigger_data.sql_readings1[0]) - float(trigger_data.sql_readings2[0]))
            except Exception as error:
                operations_logger.primary_logger.warning("Pressure Trigger: " + str(error))
                difference = 0.0

            if difference > trigger_data.variance:
                operations_logger.primary_logger.debug("Pressure exceeded set trigger")
                for execute in trigger_data.get_sql_write_str():
                    write_to_sql_database(execute)


def check_humidity():
    if installed_sensors.has_humidity and trigger_variances.humidity_enabled and current_config.enable_trigger_recording:
        while True:
            trigger_data = CreateTriggerDatabaseData()

            trigger_data.variance = trigger_variances.humidity_variance
            trigger_data.sql_columns_str += database_variables.humidity

            try:
                trigger_data.sql_readings1.append(operations_sensors.get_humidity())
            except Exception as error:
                operations_logger.primary_logger.warning("Get Humidity Error: " + str(error))
                trigger_data.sql_readings1.append("0")
            trigger_data.sql_readings1_datetime.append(get_datetime_stamp())

            sleep(trigger_variances.humidity_wait_seconds)

            try:
                trigger_data.sql_readings2.append(operations_sensors.get_humidity())
            except Exception as error:
                operations_logger.primary_logger.warning("Get Humidity Error: " + str(error))
                trigger_data.sql_readings2.append("0")
            trigger_data.sql_readings2_datetime.append(get_datetime_stamp())

            try:
                difference = abs(float(trigger_data.sql_readings1[0]) - float(trigger_data.sql_readings2[0]))
            except Exception as error:
                operations_logger.primary_logger.warning("Humidity Trigger: " + str(error))
                difference = 0.0

            if difference > trigger_data.variance:
                operations_logger.primary_logger.debug("Humidity exceeded set trigger")
                for execute in trigger_data.get_sql_write_str():
                    write_to_sql_database(execute)


def check_lumen():
    if installed_sensors.has_lumen and trigger_variances.lumen_enabled and current_config.enable_trigger_recording:
        while True:
            trigger_data = CreateTriggerDatabaseData()

            trigger_data.variance = trigger_variances.lumen_variance
            trigger_data.sql_columns_str += database_variables.lumen

            try:
                trigger_data.sql_readings1.append(operations_sensors.get_lumen())
            except Exception as error:
                operations_logger.primary_logger.warning("Get Lumen Error: " + str(error))
                trigger_data.sql_readings1.append("0")
            trigger_data.sql_readings1_datetime.append(get_datetime_stamp())

            sleep(trigger_variances.lumen_wait_seconds)

            try:
                trigger_data.sql_readings2.append(operations_sensors.get_lumen())
            except Exception as error:
                operations_logger.primary_logger.warning("Get Lumen Error: " + str(error))
                trigger_data.sql_readings2.append("0")
            trigger_data.sql_readings2_datetime.append(get_datetime_stamp())

            try:
                difference = abs(float(trigger_data.sql_readings1[0]) - float(trigger_data.sql_readings2[0]))
            except Exception as error:
                operations_logger.primary_logger.warning("Lumen Trigger: " + str(error))
                difference = 0.0

            if difference > trigger_data.variance:
                operations_logger.primary_logger.debug("Lumen exceeded set trigger")
                for execute in trigger_data.get_sql_write_str():
                    write_to_sql_database(execute)


def check_ems():
    if current_config.enable_trigger_recording:
        if installed_sensors.has_violet:
            while True:
                _check_6_ems()
        elif installed_sensors.has_red:
            while True:
                _check_3_ems()
        else:
            pass


def _check_3_ems():
    red_trigger_data = CreateTriggerDatabaseData()
    green_trigger_data = CreateTriggerDatabaseData()
    blue_trigger_data = CreateTriggerDatabaseData()

    try:
        sensor_colours = operations_sensors.get_ems()
    except Exception as error:
        operations_logger.primary_logger.warning("Get Colours Error: " + str(error))
        sensor_colours = [0, 0, 0]
    date_stamp1 = get_datetime_stamp()

    sleep(trigger_variances.colour_wait)

    try:
        sensor_colours2 = operations_sensors.get_ems()
    except Exception as error:
        operations_logger.primary_logger.warning("Get Colours Error: " + str(error))
        sensor_colours2 = [0, 0, 0]
    date_stamp2 = get_datetime_stamp()

    red_trigger_data.sql_readings1.append(sensor_colours[0])
    red_trigger_data.sql_readings2.append(sensor_colours2[0])
    red_trigger_data.sql_readings1_datetime.append(date_stamp1)
    red_trigger_data.sql_readings2_datetime.append(date_stamp2)
    _check_red(red_trigger_data)

    green_trigger_data.sql_readings1.append(sensor_colours[1])
    green_trigger_data.sql_readings2.append(sensor_colours2[1])
    green_trigger_data.sql_readings1_datetime.append(date_stamp1)
    green_trigger_data.sql_readings2_datetime.append(date_stamp2)
    _check_green(green_trigger_data)

    blue_trigger_data.sql_readings1.append(sensor_colours[2])
    blue_trigger_data.sql_readings2.append(sensor_colours2[2])
    blue_trigger_data.sql_readings1_datetime.append(date_stamp1)
    blue_trigger_data.sql_readings2_datetime.append(date_stamp2)
    _check_blue(blue_trigger_data)


def _check_6_ems():
    red_trigger_data = CreateTriggerDatabaseData()
    orange_trigger_data = CreateTriggerDatabaseData()
    yellow_trigger_data = CreateTriggerDatabaseData()
    green_trigger_data = CreateTriggerDatabaseData()
    blue_trigger_data = CreateTriggerDatabaseData()
    violet_trigger_data = CreateTriggerDatabaseData()

    try:
        sensor_colours = operations_sensors.get_ems()
    except Exception as error:
        operations_logger.primary_logger.warning("Get Colours Error: " + str(error))
        sensor_colours = [0, 0, 0, 0, 0, 0]

    date_stamp1 = get_datetime_stamp()

    sleep(trigger_variances.colour_wait)

    try:
        sensor_colours2 = operations_sensors.get_ems()
    except Exception as error:
        operations_logger.primary_logger.warning("Get Colours Error: " + str(error))
        sensor_colours2 = [0, 0, 0, 0, 0, 0]

    date_stamp2 = get_datetime_stamp()

    red_trigger_data.sql_readings1.append(str(sensor_colours[0]))
    red_trigger_data.sql_readings2.append(str(sensor_colours2[0]))
    red_trigger_data.sql_readings1_datetime.append(date_stamp1)
    red_trigger_data.sql_readings2_datetime.append(date_stamp2)
    _check_red(red_trigger_data)

    orange_trigger_data.sql_readings1.append(sensor_colours[1])
    orange_trigger_data.sql_readings2.append(sensor_colours2[1])
    orange_trigger_data.sql_readings1_datetime.append(date_stamp1)
    orange_trigger_data.sql_readings2_datetime.append(date_stamp2)
    _check_orange(orange_trigger_data)

    yellow_trigger_data.sql_readings1.append(sensor_colours[2])
    yellow_trigger_data.sql_readings2.append(sensor_colours2[2])
    yellow_trigger_data.sql_readings1_datetime.append(date_stamp1)
    yellow_trigger_data.sql_readings2_datetime.append(date_stamp2)
    _check_yellow(yellow_trigger_data)

    green_trigger_data.sql_readings1.append(sensor_colours[3])
    green_trigger_data.sql_readings2.append(sensor_colours2[3])
    green_trigger_data.sql_readings1_datetime.append(date_stamp1)
    green_trigger_data.sql_readings2_datetime.append(date_stamp2)
    _check_green(green_trigger_data)

    blue_trigger_data.sql_readings1.append(sensor_colours[4])
    blue_trigger_data.sql_readings2.append(sensor_colours2[4])
    blue_trigger_data.sql_readings1_datetime.append(date_stamp1)
    blue_trigger_data.sql_readings2_datetime.append(date_stamp2)
    _check_blue(blue_trigger_data)

    violet_trigger_data.sql_readings1.append(sensor_colours[5])
    violet_trigger_data.sql_readings2.append(sensor_colours2[5])
    violet_trigger_data.sql_readings1_datetime.append(date_stamp1)
    violet_trigger_data.sql_readings2_datetime.append(date_stamp2)
    _check_violet(violet_trigger_data)


def _check_red(trigger_data):
    if trigger_variances.red_enabled:
        trigger_data.variance = trigger_variances.red_variance
        trigger_data.sql_columns_str += database_variables.red

        try:
            difference = abs(float(trigger_data.sql_readings1[0]) - float(trigger_data.sql_readings2[0]))
        except Exception as error:
            operations_logger.primary_logger.warning("Red Trigger: " + str(error))
            difference = 0.0

        if difference > trigger_data.variance:
            operations_logger.primary_logger.debug("Red exceeded set trigger")
            for execute in trigger_data.get_sql_write_str():
                write_to_sql_database(execute)


def _check_orange(trigger_data):
    if trigger_variances.orange_enabled:
        trigger_data.variance = trigger_variances.orange_variance
        trigger_data.sql_columns_str += database_variables.orange

        try:
            difference = abs(float(trigger_data.sql_readings1[0]) - float(trigger_data.sql_readings2[0]))
        except Exception as error:
            operations_logger.primary_logger.warning("Orange Trigger: " + str(error))
            difference = 0.0

        if difference > trigger_data.variance:
            operations_logger.primary_logger.debug("Orange exceeded set trigger")
            for execute in trigger_data.get_sql_write_str():
                write_to_sql_database(execute)


def _check_yellow(trigger_data):
    if trigger_variances.yellow_enabled:
        trigger_data.variance = trigger_variances.yellow_variance
        trigger_data.sql_columns_str += database_variables.yellow

        try:
            difference = abs(float(trigger_data.sql_readings1[0]) - float(trigger_data.sql_readings2[0]))
        except Exception as error:
            operations_logger.primary_logger.warning("Yellow Trigger: " + str(error))
            difference = 0.0

        if difference > trigger_data.variance:
            operations_logger.primary_logger.debug("Yellow exceeded set trigger")
            for execute in trigger_data.get_sql_write_str():
                write_to_sql_database(execute)


def _check_green(trigger_data):
    if trigger_variances.green_enabled:
        trigger_data.variance = trigger_variances.green_variance
        trigger_data.sql_columns_str += database_variables.green

        try:
            difference = abs(float(trigger_data.sql_readings1[0]) - float(trigger_data.sql_readings2[0]))
        except Exception as error:
            operations_logger.primary_logger.warning("Green Trigger: " + str(error))
            difference = 0.0

        if difference > trigger_data.variance:
            operations_logger.primary_logger.debug("Green exceeded set trigger")
            for execute in trigger_data.get_sql_write_str():
                write_to_sql_database(execute)


def _check_blue(trigger_data):
    if trigger_variances.blue_enabled:
        trigger_data.variance = trigger_variances.blue_variance
        trigger_data.sql_columns_str += database_variables.blue

        try:
            difference = abs(float(trigger_data.sql_readings1[0]) - float(trigger_data.sql_readings2[0]))
        except Exception as error:
            operations_logger.primary_logger.warning("Blue Trigger: " + str(error))
            difference = 0.0

        if difference > trigger_data.variance:
            operations_logger.primary_logger.debug("Blue exceeded set trigger")
            for execute in trigger_data.get_sql_write_str():
                write_to_sql_database(execute)


def _check_violet(trigger_data):
    if trigger_variances.violet_enabled:
        trigger_data.variance = trigger_variances.violet_variance
        trigger_data.sql_columns_str += database_variables.violet

        try:
            difference = abs(float(trigger_data.sql_readings1[0]) - float(trigger_data.sql_readings2[0]))
        except Exception as error:
            operations_logger.primary_logger.warning("Violet Trigger: " + str(error))
            difference = 0.0

        if difference > trigger_data.variance:
            operations_logger.primary_logger.debug("Violet exceeded set trigger")
            for execute in trigger_data.get_sql_write_str():
                write_to_sql_database(execute)


def check_accelerometer_xyz():
    if installed_sensors.has_acc and trigger_variances.accelerometer_enabled and current_config.enable_trigger_recording:
        while True:
            x_trigger_data = CreateTriggerDatabaseData()
            y_trigger_data = CreateTriggerDatabaseData()
            z_trigger_data = CreateTriggerDatabaseData()

            x_trigger_data.variance = trigger_variances.accelerometer_variance
            x_trigger_data.sql_columns_str += database_variables.acc_x
            y_trigger_data.variance = trigger_variances.accelerometer_variance
            y_trigger_data.sql_columns_str += database_variables.acc_y
            z_trigger_data.variance = trigger_variances.accelerometer_variance
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
    if installed_sensors.has_mag and trigger_variances.magnetometer_enabled and current_config.enable_trigger_recording:
        while True:
            x_trigger_data = CreateTriggerDatabaseData()
            y_trigger_data = CreateTriggerDatabaseData()
            z_trigger_data = CreateTriggerDatabaseData()

            x_trigger_data.variance = trigger_variances.magnetometer_variance
            x_trigger_data.sql_columns_str += database_variables.mag_x
            y_trigger_data.variance = trigger_variances.magnetometer_variance
            y_trigger_data.sql_columns_str += database_variables.mag_y
            z_trigger_data.variance = trigger_variances.magnetometer_variance
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
    if installed_sensors.has_gyro and trigger_variances.gyroscope_enabled and current_config.enable_trigger_recording:
        while True:
            x_trigger_data = CreateTriggerDatabaseData()
            y_trigger_data = CreateTriggerDatabaseData()
            z_trigger_data = CreateTriggerDatabaseData()

            x_trigger_data.variance = trigger_variances.gyroscope_variance
            x_trigger_data.sql_columns_str += database_variables.gyro_x
            y_trigger_data.variance = trigger_variances.gyroscope_variance
            y_trigger_data.sql_columns_str += database_variables.gyro_y
            z_trigger_data.variance = trigger_variances.gyroscope_variance
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
