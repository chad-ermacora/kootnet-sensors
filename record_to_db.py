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

from operations_modules import operations_config
from operations_modules import operations_db
from operations_modules import operations_logger
from operations_modules import operations_pre_checks
from operations_modules import operations_sensors

# Ensure files, database & configurations are OK
operations_pre_checks.check_missing_files()
operations_pre_checks.check_database_structure()

if operations_config.get_old_version() != operations_config.version:
    operations_logger.primary_logger.info("Checking files and configuration after upgrade")
    os.system("systemctl start SensorUpgradeChecks")
    # Sleep before loading anything due to needed updates
    # The update service will automatically restart this app when it's done
    while True:
        sleep(10)

installed_sensors = operations_config.get_installed_sensors()
current_config = operations_config.get_installed_config()
database_variables = operations_config.CreateDatabaseVariables()

operations_logger.primary_logger.info("Sensor Recording to SQLite3 DB Started")


def start_interval_recording():
    """ Starts recording all Interval sensor readings to the SQL database every X amount of time (set in config). """
    while True:
        try:
            new_sensor_data = operations_sensors.get_interval_sensor_readings()

            interval_sql_execute = (new_sensor_data.sql_query_start + new_sensor_data.sensor_types +
                                    new_sensor_data.sql_query_values_start + new_sensor_data.sensor_readings +
                                    new_sensor_data.sql_query_values_end)

            operations_db.write_to_sql_database(interval_sql_execute)

            if installed_sensors.raspberry_pi_sense_hat and operations_config.sense_hat_show_led_message:
                operations_sensors.rp_sense_hat_sensor_access.display_led_message("SQL-Int-Rec")
        except Exception as error:
            operations_logger.primary_logger.error("Interval Failure: " + str(error))

        sleep(current_config.sleep_duration_interval)


def _check_xyz_variances(trigger_data):
    write_to_db = False
    pair_differences = []

    count = 0
    for reading in trigger_data.sql_readings1:
        readings_old = reading
        readings_new = trigger_data.sql_readings2[count]

        count2 = 0
        if count2 < 3:
            try:
                difference = abs(abs(float(readings_new[count2])) - abs(float(readings_old[count2])))
                pair_differences.append(difference)
            except Exception as error:
                operations_logger.primary_logger.error("Bad readings in XYZ variance checks: " + str(error))
                write_to_db = False

            count += 1

    for difference in pair_differences:
        if difference >= trigger_data.variance:
            operations_logger.primary_logger.debug("DIFFs Triggered")
            write_to_db = True

    if write_to_db:
        operations_logger.primary_logger.debug("Pair Differences: " + str(pair_differences))
        sql_db_executes = trigger_data.get_xyz_sql_write_str()

        for execute in sql_db_executes:
            operations_db.write_to_sql_database(execute)


def check_write_trigger_data():
    operations_logger.primary_logger.debug("Check Triggers")
    sleep(current_config.sleep_duration_trigger)

    threads = []
    if installed_sensors.has_acc:
        threads.append(Thread(target=_acc_check_thread))

    if installed_sensors.has_mag:
        threads.append(Thread(target=_mag_check_thread))

    if installed_sensors.has_gyro:
        threads.append(Thread(target=_gyro_check_thread))

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()


def _acc_check_thread():
    new_trigger_data = operations_db.CreateTriggerDatabaseData(installed_sensors)
    new_trigger_data.variance = current_config.acc_variance
    new_trigger_data.sql_columns_str += database_variables.get_acc_columns_str()

    pair_count = 0
    while pair_count < operations_config.trigger_pairs:
        new_trigger_data.sql_readings1.append(operations_sensors.get_accelerometer_xyz())
        new_trigger_data.sql_readings1_datetime.append(get_datetime_stamp())
        sleep(current_config.sleep_duration_trigger)
        new_trigger_data.sql_readings2.append(operations_sensors.get_accelerometer_xyz())
        new_trigger_data.sql_readings2_datetime.append(get_datetime_stamp())
        pair_count += 1

    _check_xyz_variances(new_trigger_data)


def _mag_check_thread():
    new_trigger_data = operations_db.CreateTriggerDatabaseData(installed_sensors)
    new_trigger_data.variance = current_config.mag_variance
    new_trigger_data.sql_columns_str += database_variables.get_mag_columns_str()

    pair_count = 0
    while pair_count < operations_config.trigger_pairs:
        new_trigger_data.sql_readings1.append(operations_sensors.get_magnetometer_xyz())
        new_trigger_data.sql_readings1_datetime.append(get_datetime_stamp())
        sleep(current_config.sleep_duration_trigger)
        new_trigger_data.sql_readings2.append(operations_sensors.get_magnetometer_xyz())
        new_trigger_data.sql_readings2_datetime.append(get_datetime_stamp())
        pair_count += 1

    _check_xyz_variances(new_trigger_data)


def _gyro_check_thread():
    new_trigger_data = operations_db.CreateTriggerDatabaseData(installed_sensors)
    new_trigger_data.variance = current_config.gyro_variance
    new_trigger_data.sql_columns_str += database_variables.get_gyro_columns_str()

    pair_count = 0
    while pair_count < operations_config.trigger_pairs:
        new_trigger_data.sql_readings1.append(operations_sensors.get_gyroscope_xyz())
        new_trigger_data.sql_readings1_datetime.append(get_datetime_stamp())
        sleep(current_config.sleep_duration_trigger)
        new_trigger_data.sql_readings2.append(operations_sensors.get_gyroscope_xyz())
        new_trigger_data.sql_readings2_datetime.append(get_datetime_stamp())
        pair_count += 1

    _check_xyz_variances(new_trigger_data)


def get_datetime_stamp():
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]


if current_config.write_to_db and installed_sensors.no_sensors is False:
    # Start Interval Recording
    interval_recording_thread = Thread(target=start_interval_recording)
    interval_recording_thread.daemon = True
    interval_recording_thread.start()

    while True:
        check_write_trigger_data()

else:
    operations_logger.primary_logger.warning("Write to Database Disabled in Config or no sensors set")
    while True:
        sleep(600)
