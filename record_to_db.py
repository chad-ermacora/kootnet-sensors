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
import os
from datetime import datetime
from threading import Thread
from time import sleep

import operations_modules.operations_db as operations_db
from operations_modules import operations_logger
from operations_modules import operations_pre_checks
from operations_modules import operations_sensors
from operations_modules.operations_config import installed_sensors, current_config, trigger_variances, version, \
    get_old_version, sense_hat_show_led_message, trigger_pairs

# Ensure files, database & configurations are OK
operations_pre_checks.check_missing_files()
operations_pre_checks.check_database_structure()

if get_old_version() != version:
    operations_logger.primary_logger.info("Checking files and configuration after upgrade")
    os.system("systemctl start SensorUpgradeChecks")
    # Sleep before loading anything due to needed updates
    # The update service will automatically restart this app when it's done
    while True:
        sleep(10)

operations_logger.primary_logger.info("Sensor Recording to SQLite3 DB Started")

database_variables = operations_db.CreateDatabaseVariables()


def start_interval_recording():
    """ Starts recording all Interval sensor readings to the SQL database every X amount of time (set in config). """
    while True:
        try:
            new_sensor_data = operations_sensors.get_interval_sensor_readings()

            interval_sql_execute = (new_sensor_data.sql_query_start + new_sensor_data.sensor_types +
                                    new_sensor_data.sql_query_values_start + new_sensor_data.sensor_readings +
                                    new_sensor_data.sql_query_values_end)

            operations_db.write_to_sql_database(interval_sql_execute)

            if installed_sensors.raspberry_pi_sense_hat and sense_hat_show_led_message:
                operations_sensors.rp_sense_hat_sensor_access.display_led_message("SQL-Int-Rec")
        except Exception as error:
            operations_logger.primary_logger.error("Interval Failure: " + str(error))

        sleep(current_config.sleep_duration_interval)


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
            operations_db.write_to_sql_database(execute)


def check_write_trigger_data():
    sleep(current_config.sleep_duration_trigger)

    sensor_selection = operations_db.CreateDatabaseVariables()

    threads = [Thread(target=_check_sensor, args=[sensor_selection.acc_x]),
               Thread(target=_check_sensor, args=[sensor_selection.mag_x]),
               Thread(target=_check_sensor, args=[sensor_selection.gyro_x])]

    # for sensor in sensor_selection.get_sensor_columns_list():
    #     threads.append(Thread(target=_check_sensor, args=[sensor]))

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()


def _check_sensor(sensor_type):
    sensor_selection = operations_db.CreateDatabaseVariables()
    trigger_data = operations_db.CreateTriggerDatabaseData(installed_sensors)

    if sensor_type == sensor_selection.sensor_name:
        trigger_data.variance = trigger_variances.sensor_name
        trigger_data.sql_columns_str += database_variables.sensor_name

        pair_count = 0
        while pair_count < trigger_pairs:
            trigger_data.sql_readings1.append(operations_sensors.get_hostname())
            trigger_data.sql_readings1_datetime.append(get_datetime_stamp())

            sleep(current_config.sleep_duration_trigger)

            trigger_data.sql_readings2.append(operations_sensors.get_hostname())
            trigger_data.sql_readings2_datetime.append(get_datetime_stamp())

            pair_count += 1
        # Need to create a new detection for this one
        # _check_against_variance(trigger_data)
    elif sensor_type == sensor_selection.ip:
        trigger_data.variance = trigger_variances.ip
        trigger_data.sql_columns_str += database_variables.ip

        pair_count = 0
        while pair_count < trigger_pairs:
            trigger_data.sql_readings1.append(operations_sensors.get_ip())
            trigger_data.sql_readings1_datetime.append(get_datetime_stamp())

            sleep(current_config.sleep_duration_trigger)

            trigger_data.sql_readings2.append(operations_sensors.get_ip())
            trigger_data.sql_readings2_datetime.append(get_datetime_stamp())

            pair_count += 1
        # Need to create a new detection for this one
        # _check_against_variance(trigger_data)
    elif sensor_type == sensor_selection.sensor_uptime:
        trigger_data.variance = trigger_variances.sensor_uptime
        trigger_data.sql_columns_str += database_variables.sensor_uptime

        pair_count = 0
        while pair_count < trigger_pairs:
            trigger_data.sql_readings1.append(operations_sensors.get_system_uptime())
            trigger_data.sql_readings1_datetime.append(get_datetime_stamp())

            sleep(current_config.sleep_duration_trigger)

            trigger_data.sql_readings2.append(operations_sensors.get_system_uptime())
            trigger_data.sql_readings2_datetime.append(get_datetime_stamp())

            pair_count += 1
        # Need to create a new detection for this one
        # _check_against_variance(trigger_data)
    elif sensor_type == sensor_selection.system_temperature:
        trigger_data.variance = trigger_variances.cpu_temperature
        trigger_data.sql_columns_str += database_variables.system_temperature

        pair_count = 0
        while pair_count < trigger_pairs:
            trigger_data.sql_readings1.append(operations_sensors.get_cpu_temperature())
            trigger_data.sql_readings1_datetime.append(get_datetime_stamp())

            sleep(current_config.sleep_duration_trigger)

            trigger_data.sql_readings2.append(operations_sensors.get_cpu_temperature())
            trigger_data.sql_readings2_datetime.append(get_datetime_stamp())

            pair_count += 1
        # Need to create a new detection for this one
        # _check_against_variance(trigger_data)
    elif sensor_type == sensor_selection.env_temperature:
        trigger_data.variance = trigger_variances.env_temperature
        trigger_data.sql_columns_str += database_variables.env_temperature

        pair_count = 0
        while pair_count < trigger_pairs:
            trigger_data.sql_readings1.append(operations_sensors.get_sensor_temperature())
            trigger_data.sql_readings1_datetime.append(get_datetime_stamp())

            sleep(current_config.sleep_duration_trigger)

            trigger_data.sql_readings2.append(operations_sensors.get_sensor_temperature())
            trigger_data.sql_readings2_datetime.append(get_datetime_stamp())

            pair_count += 1
        # Need to create a new detection for this one
        # _check_against_variance(trigger_data)
    elif sensor_type == sensor_selection.pressure:
        trigger_data.variance = trigger_variances.pressure
        trigger_data.sql_columns_str += database_variables.pressure

        pair_count = 0
        while pair_count < trigger_pairs:
            trigger_data.sql_readings1.append(operations_sensors.get_pressure())
            trigger_data.sql_readings1_datetime.append(get_datetime_stamp())

            sleep(current_config.sleep_duration_trigger)

            trigger_data.sql_readings2.append(operations_sensors.get_pressure())
            trigger_data.sql_readings2_datetime.append(get_datetime_stamp())

            pair_count += 1
        # Need to create a new detection for this one
        # _check_against_variance(trigger_data)
    elif sensor_type == sensor_selection.humidity:
        trigger_data.variance = trigger_variances.humidity
        trigger_data.sql_columns_str += database_variables.humidity

        pair_count = 0
        while pair_count < trigger_pairs:
            trigger_data.sql_readings1.append(operations_sensors.get_humidity())
            trigger_data.sql_readings1_datetime.append(get_datetime_stamp())

            sleep(current_config.sleep_duration_trigger)

            trigger_data.sql_readings2.append(operations_sensors.get_humidity())
            trigger_data.sql_readings2_datetime.append(get_datetime_stamp())

            pair_count += 1
        # Need to create a new detection for this one
        # _check_against_variance(trigger_data)
    elif sensor_type == sensor_selection.lumen:
        trigger_data.variance = trigger_variances.lumen
        trigger_data.sql_columns_str += database_variables.lumen

        pair_count = 0
        while pair_count < trigger_pairs:
            trigger_data.sql_readings1.append(operations_sensors.get_lumen())
            trigger_data.sql_readings1_datetime.append(get_datetime_stamp())

            sleep(current_config.sleep_duration_trigger)

            trigger_data.sql_readings2.append(operations_sensors.get_lumen())
            trigger_data.sql_readings2_datetime.append(get_datetime_stamp())

            pair_count += 1
        # Need to create a new detection for this one
        # _check_against_variance(trigger_data)
    elif sensor_type == sensor_selection.red:
        pass
    elif sensor_type == sensor_selection.orange:
        pass
    elif sensor_type == sensor_selection.yellow:
        pass
    elif sensor_type == sensor_selection.green:
        pass
    elif sensor_type == sensor_selection.blue:
        pass
    elif sensor_type == sensor_selection.violet:
        pass
    elif sensor_type == sensor_selection.acc_x:
        if installed_sensors.has_acc:
            _check_xyz_thread(sensor_type)
    elif sensor_type == sensor_selection.mag_x:
        if installed_sensors.has_mag:
            _check_xyz_thread(sensor_type)
    elif sensor_type == sensor_selection.gyro_x:
        if installed_sensors.has_gyro:
            _check_xyz_thread(sensor_type)


def _check_xyz_thread(sensor_type):
    sensor_selection = operations_db.CreateDatabaseVariables()
    x_trigger_data = operations_db.CreateTriggerDatabaseData(installed_sensors)
    y_trigger_data = operations_db.CreateTriggerDatabaseData(installed_sensors)
    z_trigger_data = operations_db.CreateTriggerDatabaseData(installed_sensors)
    if sensor_type == sensor_selection.acc_x:
        x_trigger_data.variance = current_config.acc_variance
        x_trigger_data.sql_columns_str += database_variables.acc_x
        y_trigger_data.variance = current_config.acc_variance
        y_trigger_data.sql_columns_str += database_variables.acc_y
        z_trigger_data.variance = current_config.acc_variance
        z_trigger_data.sql_columns_str += database_variables.acc_z
    elif sensor_type == sensor_selection.mag_x:
        x_trigger_data.variance = current_config.mag_variance
        x_trigger_data.sql_columns_str += database_variables.mag_x
        y_trigger_data.variance = current_config.mag_variance
        y_trigger_data.sql_columns_str += database_variables.mag_y
        z_trigger_data.variance = current_config.mag_variance
        z_trigger_data.sql_columns_str += database_variables.mag_z
    elif sensor_type == sensor_selection.gyro_x:
        x_trigger_data.variance = current_config.gyro_variance
        x_trigger_data.sql_columns_str += database_variables.gyro_x
        y_trigger_data.variance = current_config.gyro_variance
        y_trigger_data.sql_columns_str += database_variables.gyro_y
        z_trigger_data.variance = current_config.gyro_variance
        z_trigger_data.sql_columns_str += database_variables.gyro_z

    pair_count = 0
    while pair_count < trigger_pairs:
        if sensor_type == sensor_selection.acc_x:
            xyz = operations_sensors.get_accelerometer_xyz()
        elif sensor_type == sensor_selection.mag_x:
            xyz = operations_sensors.get_magnetometer_xyz()
        elif sensor_type == sensor_selection.gyro_x:
            xyz = operations_sensors.get_gyroscope_xyz()
        else:
            xyz = [0, 0, 0]

        x_trigger_data.sql_readings1.append(xyz[0])
        x_trigger_data.sql_readings1_datetime.append(get_datetime_stamp())
        y_trigger_data.sql_readings1.append(xyz[1])
        y_trigger_data.sql_readings1_datetime.append(get_datetime_stamp())
        z_trigger_data.sql_readings1.append(xyz[2])
        z_trigger_data.sql_readings1_datetime.append(get_datetime_stamp())

        sleep(current_config.sleep_duration_trigger)

        if sensor_type == sensor_selection.acc_x:
            xyz = operations_sensors.get_accelerometer_xyz()
        elif sensor_type == sensor_selection.mag_x:
            xyz = operations_sensors.get_magnetometer_xyz()
        elif sensor_type == sensor_selection.gyro_x:
            xyz = operations_sensors.get_gyroscope_xyz()
        else:
            xyz = [0, 0, 0]

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


def get_datetime_stamp():
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]


if current_config.write_to_db and installed_sensors.no_sensors is False:
    if current_config.enable_interval_recording:
        # Start Interval Recording
        interval_recording_thread = Thread(target=start_interval_recording)
        interval_recording_thread.daemon = True
        interval_recording_thread.start()
    else:
        operations_logger.primary_logger.warning("Interval Recording Disabled in Config")
        while True:
            sleep(600)

    if current_config.enable_trigger_recording:
        while True:
            check_write_trigger_data()
    else:
        operations_logger.primary_logger.warning("Trigger Recording Disabled in Config")
        while True:
            sleep(600)

else:
    operations_logger.primary_logger.warning("Write to Database Disabled in Config or no sensors set")
    while True:
        sleep(600)
