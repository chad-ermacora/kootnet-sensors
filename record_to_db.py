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
from threading import Thread
from time import sleep

import operations_config
import operations_db
import operations_logger
import operations_sensors

installed_sensors = operations_config.get_installed_sensors()
current_config = operations_config.get_installed_config()
operations_db.check_database_structure()
operations_logger.primary_logger.info("Sensor Recording to SQLite3 DB Started")

# Write installed sensors back to file. This is used to add new sensor support
operations_config.write_installed_sensors_to_file(installed_sensors)
operations_config.write_config_to_file(current_config)


def start_interval_recording():
    while True:
        new_sensor_data = operations_sensors.get_interval_sensor_readings()

        if len(new_sensor_data.sensor_readings) > 0:
            sql_command_data = operations_db.CreateSQLCommandData()

            sql_command_data.database_location = new_sensor_data.database_location
            sql_command_data.sql_execute = (new_sensor_data.sql_query_start + new_sensor_data.sensor_types +
                                            new_sensor_data.sql_query_values_start + new_sensor_data.sensor_readings +
                                            new_sensor_data.sql_query_values_end)

            operations_db.write_to_sql_database(sql_command_data)
        else:
            operations_logger.primary_logger.warning("No Sensor Data Provided - Skipping Interval Database Write")

        sleep(current_config.sleep_duration_interval)


def get_readings_set():
    reading_pair = [operations_sensors.get_trigger_sensor_readings()]
    sleep(current_config.sleep_duration_trigger)
    reading_pair.append(operations_sensors.get_trigger_sensor_readings())
    readings_set = [reading_pair]

    reading_pair = [operations_sensors.get_trigger_sensor_readings()]
    sleep(current_config.sleep_duration_trigger)
    reading_pair.append(operations_sensors.get_trigger_sensor_readings())
    readings_set.append(reading_pair)

    reading_pair = [operations_sensors.get_trigger_sensor_readings()]
    sleep(current_config.sleep_duration_trigger)
    reading_pair.append(operations_sensors.get_trigger_sensor_readings())
    readings_set.append(reading_pair)

    reading_pair = [operations_sensors.get_trigger_sensor_readings()]
    sleep(current_config.sleep_duration_trigger)
    reading_pair.append(operations_sensors.get_trigger_sensor_readings())
    readings_set.append(reading_pair)

    reading_pair = [operations_sensors.get_trigger_sensor_readings()]
    sleep(current_config.sleep_duration_trigger)
    reading_pair.append(operations_sensors.get_trigger_sensor_readings())
    readings_set.append(reading_pair)

    return readings_set


def check_xyz(sensor_readings_set):
    write_to_db = False

    for reading_pair in sensor_readings_set:
        sensor_readings_new = reading_pair[1].sensor_readings.replace("'", "").split(",")
        sensor_readings_old = reading_pair[0].sensor_readings.replace("'", "").split(",")

        if float(sensor_readings_new[2]) < (float(sensor_readings_old[2]) - current_config.acc_variance) or \
                float(sensor_readings_new[2]) > (float(sensor_readings_old[2]) + current_config.acc_variance):
            write_to_db = True
        elif float(sensor_readings_new[3]) < (float(sensor_readings_old[3]) - current_config.acc_variance) or \
                float(sensor_readings_new[3]) > (float(sensor_readings_old[3]) + current_config.acc_variance):
            write_to_db = True
        elif float(sensor_readings_new[4]) < (float(sensor_readings_old[4]) - current_config.acc_variance) or \
                float(sensor_readings_new[4]) > (float(sensor_readings_old[4]) + current_config.acc_variance):
            write_to_db = True
        elif float(sensor_readings_new[5]) < (float(sensor_readings_old[5]) - current_config.mag_variance) or \
                float(sensor_readings_new[5]) > (float(sensor_readings_old[5]) + current_config.mag_variance):
            write_to_db = True
        elif float(sensor_readings_new[6]) < (float(sensor_readings_old[6]) - current_config.mag_variance) or \
                float(sensor_readings_new[6]) > (float(sensor_readings_old[6]) + current_config.mag_variance):
            write_to_db = True
        elif float(sensor_readings_new[7]) < (float(sensor_readings_old[7]) - current_config.mag_variance) or \
                float(sensor_readings_new[7]) > (float(sensor_readings_old[7]) + current_config.mag_variance):
            write_to_db = True
        elif float(sensor_readings_new[8]) < (float(sensor_readings_old[8]) - current_config.gyro_variance) or \
                float(sensor_readings_new[8]) > (float(sensor_readings_old[8]) + current_config.gyro_variance):
            write_to_db = True
        elif float(sensor_readings_new[9]) < (float(sensor_readings_old[9]) - current_config.gyro_variance) or \
                float(sensor_readings_new[9]) > (float(sensor_readings_old[9]) + current_config.gyro_variance):
            write_to_db = True
        elif float(sensor_readings_new[10]) < (float(sensor_readings_old[10]) - current_config.gyro_variance) or \
                float(sensor_readings_new[10]) > (float(sensor_readings_old[10]) + current_config.gyro_variance):
            write_to_db = True

    if write_to_db:
        write_trigger_to_database(sensor_readings_set)


def write_trigger_to_database(sensor_readings_set):
    sql_command_data = operations_db.CreateSQLCommandData()
    sql_command_data.database_location = sensor_readings_set[0][0].database_location

    for reading_pair in sensor_readings_set:
        for trigger_data in reading_pair:
            sql_command_data.sql_execute = (trigger_data.sql_query_start + trigger_data.sensor_types +
                                            trigger_data.sql_query_values_start + trigger_data.sensor_readings +
                                            trigger_data.sql_query_values_end)

            operations_db.write_to_sql_database(sql_command_data)


if current_config.write_to_db:
    # Start Interval Recording
    interval_thread = Thread(target=start_interval_recording)
    interval_thread.daemon = True
    interval_thread.start()

    # Write first reading to Database, then start monitoring Triggers
    start_readings_set = get_readings_set()
    write_trigger_to_database(start_readings_set)

    while True:
        new_readings_set = get_readings_set()
        check_xyz(new_readings_set)

else:
    operations_logger.primary_logger.warning("Write to Database Disabled in Config - Skipping Trigger Database Write")
    while True:
        sleep(600)
