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
from operations_modules import sensors
from operations_modules import logger
from operations_modules import configuration_main
from operations_modules import sqlite_database
from operations_modules import app_variables


def check_sensor_uptime():
    """ If enabled, writes sensor uptime to SQL trigger database per the variance setting. """
    if configuration_main.trigger_variances.sensor_uptime_enabled and \
            configuration_main.current_config.enable_trigger_recording:
        while True:
            trigger_data = sqlite_database.CreateTriggerDatabaseData()
            trigger_data.sql_columns_str += configuration_main.database_variables.sensor_uptime

            trigger_data.sql_readings1.append(sensors.get_system_uptime())
            trigger_data.sql_readings1_datetime.append(get_datetime_stamp())

            sleep(configuration_main.trigger_variances.sensor_uptime_wait_seconds)

            trigger_data.sql_readings2.append(sensors.get_system_uptime())
            trigger_data.sql_readings2_datetime.append(get_datetime_stamp())

            logger.primary_logger.debug("Sensor Uptime exceeded set trigger")
            for execute in trigger_data.get_sql_write_str():
                sqlite_database.write_to_sql_database(execute)


def check_cpu_temperature():
    """ If enabled, writes CPU temperature to SQL trigger database per the variance setting. """
    if configuration_main.installed_sensors.has_cpu_temperature and \
            configuration_main.trigger_variances.cpu_temperature_enabled and \
            configuration_main.current_config.enable_trigger_recording:
        while True:
            trigger_data = sqlite_database.CreateTriggerDatabaseData()

            trigger_data.variance = configuration_main.trigger_variances.cpu_temperature_variance
            trigger_data.sql_columns_str += configuration_main.database_variables.system_temperature

            try:
                trigger_data.sql_readings1.append(sensors.get_cpu_temperature())
            except Exception as error:
                logger.primary_logger.warning("Get CPU Temperature Error: " + str(error))
                trigger_data.sql_readings1.append("0")
            trigger_data.sql_readings1_datetime.append(get_datetime_stamp())

            sleep(configuration_main.trigger_variances.cpu_temperature_wait_seconds)

            try:
                trigger_data.sql_readings2.append(sensors.get_cpu_temperature())
            except Exception as error:
                logger.primary_logger.warning("Get CPU Temperature Error: " + str(error))
                trigger_data.sql_readings1.append("0")
            trigger_data.sql_readings2_datetime.append(get_datetime_stamp())

            try:
                difference = abs(float(trigger_data.sql_readings1[0]) - float(trigger_data.sql_readings2[0]))
            except Exception as error:
                logger.primary_logger.warning("CPU Temperature Trigger: " + str(error))
                difference = 0.0

            if difference > trigger_data.variance:
                logger.primary_logger.debug("CPU Temperature exceeded set trigger")
                for execute in trigger_data.get_sql_write_str():
                    sqlite_database.write_to_sql_database(execute)


def check_env_temperature():
    """ If enabled, writes sensor temperature to SQL trigger database per the variance setting. """
    if configuration_main.installed_sensors.has_env_temperature and \
            configuration_main.trigger_variances.env_temperature_enabled and \
            configuration_main.current_config.enable_trigger_recording:
        while True:
            trigger_data = sqlite_database.CreateTriggerDatabaseData()

            trigger_data.variance = configuration_main.trigger_variances.env_temperature_variance
            trigger_data.sql_columns_str += configuration_main.database_variables.env_temperature

            try:
                trigger_data.sql_readings1.append(sensors.get_sensor_temperature())
            except Exception as error:
                logger.primary_logger.warning("Get Env Temperature Error: " + str(error))
                trigger_data.sql_readings1.append("0")
            trigger_data.sql_readings1_datetime.append(get_datetime_stamp())

            sleep(configuration_main.trigger_variances.env_temperature_wait_seconds)

            try:
                trigger_data.sql_readings2.append(sensors.get_sensor_temperature())
            except Exception as error:
                logger.primary_logger.warning("Get Env Temperature Error: " + str(error))
                trigger_data.sql_readings1.append("0")
            trigger_data.sql_readings2_datetime.append(get_datetime_stamp())

            try:
                difference = abs(float(trigger_data.sql_readings1[0]) - float(trigger_data.sql_readings2[0]))
            except Exception as error:
                logger.primary_logger.warning("Env Temperature Trigger: " + str(error))
                difference = 0.0

            if difference > trigger_data.variance:
                logger.primary_logger.debug("Environment Temperature exceeded set trigger")
                for execute in trigger_data.get_sql_write_str():
                    sqlite_database.write_to_sql_database(execute)


def check_pressure():
    """ If enabled, writes pressure to SQL trigger database per the variance setting. """
    if configuration_main.installed_sensors.has_pressure and \
            configuration_main.trigger_variances.pressure_enabled and \
            configuration_main.current_config.enable_trigger_recording:
        while True:
            trigger_data = sqlite_database.CreateTriggerDatabaseData()

            trigger_data.variance = configuration_main.trigger_variances.pressure_variance
            trigger_data.sql_columns_str += configuration_main.database_variables.pressure

            try:
                trigger_data.sql_readings1.append(sensors.get_pressure())
            except Exception as error:
                logger.primary_logger.warning("Get Pressure Error: " + str(error))
                trigger_data.sql_readings1.append("0")
            trigger_data.sql_readings1_datetime.append(get_datetime_stamp())

            sleep(configuration_main.trigger_variances.pressure_wait_seconds)

            try:
                trigger_data.sql_readings2.append(sensors.get_pressure())
            except Exception as error:
                logger.primary_logger.warning("Get Pressure Error: " + str(error))
                trigger_data.sql_readings1.append("0")
            trigger_data.sql_readings2_datetime.append(get_datetime_stamp())

            try:
                difference = abs(float(trigger_data.sql_readings1[0]) - float(trigger_data.sql_readings2[0]))
            except Exception as error:
                logger.primary_logger.warning("Pressure Trigger: " + str(error))
                difference = 0.0

            if difference > trigger_data.variance:
                logger.primary_logger.debug("Pressure exceeded set trigger")
                for execute in trigger_data.get_sql_write_str():
                    sqlite_database.write_to_sql_database(execute)


def check_humidity():
    """ If enabled, writes humidity to SQL trigger database per the variance setting. """
    if configuration_main.installed_sensors.has_humidity and \
            configuration_main.trigger_variances.humidity_enabled and \
            configuration_main.current_config.enable_trigger_recording:
        while True:
            trigger_data = sqlite_database.CreateTriggerDatabaseData()

            trigger_data.variance = configuration_main.trigger_variances.humidity_variance
            trigger_data.sql_columns_str += configuration_main.database_variables.humidity

            try:
                trigger_data.sql_readings1.append(sensors.get_humidity())
            except Exception as error:
                logger.primary_logger.warning("Get Humidity Error: " + str(error))
                trigger_data.sql_readings1.append("0")
            trigger_data.sql_readings1_datetime.append(get_datetime_stamp())

            sleep(configuration_main.trigger_variances.humidity_wait_seconds)

            try:
                trigger_data.sql_readings2.append(sensors.get_humidity())
            except Exception as error:
                logger.primary_logger.warning("Get Humidity Error: " + str(error))
                trigger_data.sql_readings2.append("0")
            trigger_data.sql_readings2_datetime.append(get_datetime_stamp())

            try:
                difference = abs(float(trigger_data.sql_readings1[0]) - float(trigger_data.sql_readings2[0]))
            except Exception as error:
                logger.primary_logger.warning("Humidity Trigger: " + str(error))
                difference = 0.0

            if difference > trigger_data.variance:
                logger.primary_logger.debug("Humidity exceeded set trigger")
                for execute in trigger_data.get_sql_write_str():
                    sqlite_database.write_to_sql_database(execute)


def check_lumen():
    """ If enabled, writes lumen to SQL trigger database per the variance setting. """
    if configuration_main.installed_sensors.has_lumen and \
            configuration_main.trigger_variances.lumen_enabled and \
            configuration_main.current_config.enable_trigger_recording:
        while True:
            trigger_data = sqlite_database.CreateTriggerDatabaseData()

            trigger_data.variance = configuration_main.trigger_variances.lumen_variance
            trigger_data.sql_columns_str += configuration_main.database_variables.lumen

            try:
                trigger_data.sql_readings1.append(sensors.get_lumen())
            except Exception as error:
                logger.primary_logger.warning("Get Lumen Error: " + str(error))
                trigger_data.sql_readings1.append("0")
            trigger_data.sql_readings1_datetime.append(get_datetime_stamp())

            sleep(configuration_main.trigger_variances.lumen_wait_seconds)

            try:
                trigger_data.sql_readings2.append(sensors.get_lumen())
            except Exception as error:
                logger.primary_logger.warning("Get Lumen Error: " + str(error))
                trigger_data.sql_readings2.append("0")
            trigger_data.sql_readings2_datetime.append(get_datetime_stamp())

            try:
                difference = abs(float(trigger_data.sql_readings1[0]) - float(trigger_data.sql_readings2[0]))
            except Exception as error:
                logger.primary_logger.warning("Lumen Trigger: " + str(error))
                difference = 0.0

            if difference > trigger_data.variance:
                logger.primary_logger.debug("Lumen exceeded set trigger")
                for execute in trigger_data.get_sql_write_str():
                    sqlite_database.write_to_sql_database(execute)


def check_ems():
    """ If enabled, writes available colours (Electromagnetic Spectrum) to SQL trigger database per the variance setting. """
    if configuration_main.current_config.enable_trigger_recording:
        if configuration_main.installed_sensors.has_violet:
            while True:
                _check_6_ems()
        elif configuration_main.installed_sensors.has_red:
            while True:
                _check_3_ems()
        else:
            pass


def _check_3_ems():
    """ Checks Red, Green, Blue EMS. """
    red_trigger_data = sqlite_database.CreateTriggerDatabaseData()
    green_trigger_data = sqlite_database.CreateTriggerDatabaseData()
    blue_trigger_data = sqlite_database.CreateTriggerDatabaseData()

    try:
        sensor_colours = sensors.get_ems()
    except Exception as error:
        logger.primary_logger.warning("Get Colours Error: " + str(error))
        sensor_colours = [0, 0, 0]
    date_stamp1 = get_datetime_stamp()

    sleep(configuration_main.trigger_variances.colour_wait)

    try:
        sensor_colours2 = sensors.get_ems()
    except Exception as error:
        logger.primary_logger.warning("Get Colours Error: " + str(error))
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
    """ Checks Red, Orange, Yellow, Green, Blue, Violet EMS. """
    red_trigger_data = sqlite_database.CreateTriggerDatabaseData()
    orange_trigger_data = sqlite_database.CreateTriggerDatabaseData()
    yellow_trigger_data = sqlite_database.CreateTriggerDatabaseData()
    green_trigger_data = sqlite_database.CreateTriggerDatabaseData()
    blue_trigger_data = sqlite_database.CreateTriggerDatabaseData()
    violet_trigger_data = sqlite_database.CreateTriggerDatabaseData()

    try:
        sensor_colours = sensors.get_ems()
    except Exception as error:
        logger.primary_logger.warning("Get Colours Error: " + str(error))
        sensor_colours = [0, 0, 0, 0, 0, 0]

    date_stamp1 = get_datetime_stamp()

    sleep(configuration_main.trigger_variances.colour_wait)

    try:
        sensor_colours2 = sensors.get_ems()
    except Exception as error:
        logger.primary_logger.warning("Get Colours Error: " + str(error))
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
    if configuration_main.trigger_variances.red_enabled:
        trigger_data.variance = configuration_main.trigger_variances.red_variance
        trigger_data.sql_columns_str += configuration_main.database_variables.red

        try:
            difference = abs(float(trigger_data.sql_readings1[0]) - float(trigger_data.sql_readings2[0]))
        except Exception as error:
            logger.primary_logger.warning("Red Trigger: " + str(error))
            difference = 0.0

        if difference > trigger_data.variance:
            logger.primary_logger.debug("Red exceeded set trigger")
            for execute in trigger_data.get_sql_write_str():
                sqlite_database.write_to_sql_database(execute)


def _check_orange(trigger_data):
    if configuration_main.trigger_variances.orange_enabled:
        trigger_data.variance = configuration_main.trigger_variances.orange_variance
        trigger_data.sql_columns_str += configuration_main.database_variables.orange

        try:
            difference = abs(float(trigger_data.sql_readings1[0]) - float(trigger_data.sql_readings2[0]))
        except Exception as error:
            logger.primary_logger.warning("Orange Trigger: " + str(error))
            difference = 0.0

        if difference > trigger_data.variance:
            logger.primary_logger.debug("Orange exceeded set trigger")
            for execute in trigger_data.get_sql_write_str():
                sqlite_database.write_to_sql_database(execute)


def _check_yellow(trigger_data):
    if configuration_main.trigger_variances.yellow_enabled:
        trigger_data.variance = configuration_main.trigger_variances.yellow_variance
        trigger_data.sql_columns_str += configuration_main.database_variables.yellow

        try:
            difference = abs(float(trigger_data.sql_readings1[0]) - float(trigger_data.sql_readings2[0]))
        except Exception as error:
            logger.primary_logger.warning("Yellow Trigger: " + str(error))
            difference = 0.0

        if difference > trigger_data.variance:
            logger.primary_logger.debug("Yellow exceeded set trigger")
            for execute in trigger_data.get_sql_write_str():
                sqlite_database.write_to_sql_database(execute)


def _check_green(trigger_data):
    if configuration_main.trigger_variances.green_enabled:
        trigger_data.variance = configuration_main.trigger_variances.green_variance
        trigger_data.sql_columns_str += configuration_main.database_variables.green

        try:
            difference = abs(float(trigger_data.sql_readings1[0]) - float(trigger_data.sql_readings2[0]))
        except Exception as error:
            logger.primary_logger.warning("Green Trigger: " + str(error))
            difference = 0.0

        if difference > trigger_data.variance:
            logger.primary_logger.debug("Green exceeded set trigger")
            for execute in trigger_data.get_sql_write_str():
                sqlite_database.write_to_sql_database(execute)


def _check_blue(trigger_data):
    if configuration_main.trigger_variances.blue_enabled:
        trigger_data.variance = configuration_main.trigger_variances.blue_variance
        trigger_data.sql_columns_str += configuration_main.database_variables.blue

        try:
            difference = abs(float(trigger_data.sql_readings1[0]) - float(trigger_data.sql_readings2[0]))
        except Exception as error:
            logger.primary_logger.warning("Blue Trigger: " + str(error))
            difference = 0.0

        if difference > trigger_data.variance:
            logger.primary_logger.debug("Blue exceeded set trigger")
            for execute in trigger_data.get_sql_write_str():
                sqlite_database.write_to_sql_database(execute)


def _check_violet(trigger_data):
    if configuration_main.trigger_variances.violet_enabled:
        trigger_data.variance = configuration_main.trigger_variances.violet_variance
        trigger_data.sql_columns_str += configuration_main.database_variables.violet

        try:
            difference = abs(float(trigger_data.sql_readings1[0]) - float(trigger_data.sql_readings2[0]))
        except Exception as error:
            logger.primary_logger.warning("Violet Trigger: " + str(error))
            difference = 0.0

        if difference > trigger_data.variance:
            logger.primary_logger.debug("Violet exceeded set trigger")
            for execute in trigger_data.get_sql_write_str():
                sqlite_database.write_to_sql_database(execute)


def check_accelerometer_xyz():
    """ If enabled, writes Acceleration to SQL trigger database per the variance setting. """
    if configuration_main.installed_sensors.has_acc and \
            configuration_main.trigger_variances.accelerometer_enabled and \
            configuration_main.current_config.enable_trigger_recording:
        while True:
            x_trigger_data = sqlite_database.CreateTriggerDatabaseData()
            y_trigger_data = sqlite_database.CreateTriggerDatabaseData()
            z_trigger_data = sqlite_database.CreateTriggerDatabaseData()

            x_trigger_data.variance = configuration_main.trigger_variances.accelerometer_variance
            x_trigger_data.sql_columns_str += configuration_main.database_variables.acc_x
            y_trigger_data.variance = configuration_main.trigger_variances.accelerometer_variance
            y_trigger_data.sql_columns_str += configuration_main.database_variables.acc_y
            z_trigger_data.variance = configuration_main.trigger_variances.accelerometer_variance
            z_trigger_data.sql_columns_str += configuration_main.database_variables.acc_z

            pair_count = 0
            while pair_count < app_variables.trigger_pairs:
                xyz = sensors.get_accelerometer_xyz()

                x_trigger_data.sql_readings1.append(xyz[0])
                x_trigger_data.sql_readings1_datetime.append(get_datetime_stamp())
                y_trigger_data.sql_readings1.append(xyz[1])
                y_trigger_data.sql_readings1_datetime.append(get_datetime_stamp())
                z_trigger_data.sql_readings1.append(xyz[2])
                z_trigger_data.sql_readings1_datetime.append(get_datetime_stamp())

                sleep(configuration_main.trigger_variances.accelerometer_wait_seconds)

                xyz = sensors.get_accelerometer_xyz()

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
        logger.primary_logger.debug("Accelerometer checks disabled in variances configuration file")


def check_magnetometer_xyz():
    """ If enabled, writes Magnetometer to SQL trigger database per the variance setting. """
    if configuration_main.installed_sensors.has_mag and \
            configuration_main.trigger_variances.magnetometer_enabled and \
            configuration_main.current_config.enable_trigger_recording:
        while True:
            x_trigger_data = sqlite_database.CreateTriggerDatabaseData()
            y_trigger_data = sqlite_database.CreateTriggerDatabaseData()
            z_trigger_data = sqlite_database.CreateTriggerDatabaseData()

            x_trigger_data.variance = configuration_main.trigger_variances.magnetometer_variance
            x_trigger_data.sql_columns_str += configuration_main.database_variables.mag_x
            y_trigger_data.variance = configuration_main.trigger_variances.magnetometer_variance
            y_trigger_data.sql_columns_str += configuration_main.database_variables.mag_y
            z_trigger_data.variance = configuration_main.trigger_variances.magnetometer_variance
            z_trigger_data.sql_columns_str += configuration_main.database_variables.mag_z

            pair_count = 0
            while pair_count < app_variables.trigger_pairs:
                xyz = sensors.get_magnetometer_xyz()

                x_trigger_data.sql_readings1.append(xyz[0])
                x_trigger_data.sql_readings1_datetime.append(get_datetime_stamp())
                y_trigger_data.sql_readings1.append(xyz[1])
                y_trigger_data.sql_readings1_datetime.append(get_datetime_stamp())
                z_trigger_data.sql_readings1.append(xyz[2])
                z_trigger_data.sql_readings1_datetime.append(get_datetime_stamp())

                sleep(configuration_main.trigger_variances.magnetometer_wait_seconds)

                xyz = sensors.get_magnetometer_xyz()

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
        logger.primary_logger.debug("Magnetometer checks disabled in variances configuration file")


def check_gyroscope_xyz():
    """ If enabled, writes Gyroscope to SQL trigger database per the variance setting. """
    if configuration_main.installed_sensors.has_gyro and \
            configuration_main.trigger_variances.gyroscope_enabled and \
            configuration_main.current_config.enable_trigger_recording:
        while True:
            x_trigger_data = sqlite_database.CreateTriggerDatabaseData()
            y_trigger_data = sqlite_database.CreateTriggerDatabaseData()
            z_trigger_data = sqlite_database.CreateTriggerDatabaseData()

            x_trigger_data.variance = configuration_main.trigger_variances.gyroscope_variance
            x_trigger_data.sql_columns_str += configuration_main.database_variables.gyro_x
            y_trigger_data.variance = configuration_main.trigger_variances.gyroscope_variance
            y_trigger_data.sql_columns_str += configuration_main.database_variables.gyro_y
            z_trigger_data.variance = configuration_main.trigger_variances.gyroscope_variance
            z_trigger_data.sql_columns_str += configuration_main.database_variables.gyro_z

            pair_count = 0
            while pair_count < app_variables.trigger_pairs:
                xyz = sensors.get_gyroscope_xyz()

                x_trigger_data.sql_readings1.append(xyz[0])
                x_trigger_data.sql_readings1_datetime.append(get_datetime_stamp())
                y_trigger_data.sql_readings1.append(xyz[1])
                y_trigger_data.sql_readings1_datetime.append(get_datetime_stamp())
                z_trigger_data.sql_readings1.append(xyz[2])
                z_trigger_data.sql_readings1_datetime.append(get_datetime_stamp())

                sleep(configuration_main.trigger_variances.gyroscope_wait_seconds)

                xyz = sensors.get_gyroscope_xyz()

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
        logger.primary_logger.debug("Gyroscopic checks disabled in variances configuration file")


def _check_against_variance(trigger_data):
    """ Checks provided sensor differences to variance and writes it to the SQL database if it exceeds the variance. """
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
            logger.primary_logger.error("Bad readings in Single variance checks: " + str(error))
            write_to_db = False
        count += 1

    for difference in pair_differences:
        if difference >= trigger_data.variance:
            write_to_db = True

    if write_to_db:
        logger.primary_logger.debug("Pair Differences: " + str(pair_differences))
        sql_db_executes = trigger_data.get_sql_write_str()

        for execute in sql_db_executes:
            sqlite_database.write_to_sql_database(execute)


def get_datetime_stamp():
    """ Returns current UTC 0 time as a string "%Y-%m-%d %H:%M:%S.%f". """
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
