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

import operations_config
import operations_db
import operations_logger
import operations_sensors

installed_sensors = operations_config.get_installed_sensors()
installed_config = operations_config.get_installed_config()
operations_db.check_database_trigger()

operations_logger.primary_logger.info("Sensor Recording by Trigger Started")


def check_acc(new_data, old_data):
    write_to_db = False

    if (float(old_data[2]) - installed_config.acc_variance) > float(new_data[2]) or \
            float(new_data[2]) > (float(old_data[2]) + installed_config.acc_variance):
        write_to_db = True
    elif (float(old_data[3]) - installed_config.acc_variance) > float(new_data[3]) or \
            float(new_data[3]) > (float(old_data[3]) + installed_config.acc_variance):
        write_to_db = True
    elif (float(old_data[4]) - installed_config.acc_variance) > float(new_data[4]) or \
            float(new_data[4]) > (float(old_data[4]) + installed_config.acc_variance):
        write_to_db = True

    return write_to_db


def check_mag(new_data, old_data):
    write_to_db = False

    if (float(old_data[5]) - installed_config.mag_variance) > float(new_data[5]) or \
            float(new_data[5]) > (float(old_data[5]) + installed_config.mag_variance):
        write_to_db = True
    elif (float(old_data[6]) - installed_config.mag_variance) > float(new_data[6]) or \
            float(new_data[6]) > (float(old_data[6]) + installed_config.mag_variance):
        write_to_db = True
    elif (float(old_data[7]) - installed_config.mag_variance) > float(new_data[7]) or \
            float(new_data[7]) > (float(old_data[7]) + installed_config.mag_variance):
        write_to_db = True

    return write_to_db


def check_gyro(new_data, old_data):
    write_to_db = False

    if (float(old_data[8]) - installed_config.gyro_variance) > float(new_data[8]) or \
            float(new_data[8]) > (float(old_data[8]) + installed_config.gyro_variance):
        write_to_db = True
    elif (float(old_data[9]) - installed_config.gyro_variance) > float(new_data[9]) or \
            float(new_data[9]) > (float(old_data[9]) + installed_config.gyro_variance):
        write_to_db = True
    elif (float(old_data[10]) - installed_config.gyro_variance) > float(new_data[10]) or \
            float(new_data[10]) > (float(old_data[10]) + installed_config.gyro_variance):
        write_to_db = True

    return write_to_db


def write_to_database(trigger_data):
    sql_command = operations_db.CreateSQLCommandData()

    sql_command.database_location = trigger_data.database_location
    sql_command.sql_execute = trigger_data.sql_query_start + \
        trigger_data.sensor_types + \
        trigger_data.sql_query_values_start + \
        trigger_data.sensor_readings + \
        trigger_data.sql_query_values_end

    operations_db.write_to_sql_database(sql_command)


if installed_config.write_to_db:
    start_trigger_data = operations_sensors.get_trigger_sensor_readings()
    write_to_database(start_trigger_data)
    print("Sensor Types: " + str(start_trigger_data.sensor_types))
    print("Sensor Readings: " + str(start_trigger_data.sensor_readings))

    while True:
        original_old_trigger_data = operations_sensors.get_trigger_sensor_readings()
        old_trigger_data = original_old_trigger_data.sensor_readings.replace("'", "").split(",")

        sleep(installed_config.sleep_duration_trigger)

        original_new_trigger_data = operations_sensors.get_trigger_sensor_readings()
        new_trigger_data = original_new_trigger_data.sensor_readings.replace("'", "").split(",")

        if installed_sensors.has_acc and check_acc(new_trigger_data, old_trigger_data):
            write_to_database(original_old_trigger_data)
            write_to_database(original_new_trigger_data)

        elif installed_sensors.has_mag and check_mag(new_trigger_data, old_trigger_data):
            write_to_database(original_old_trigger_data)
            write_to_database(original_new_trigger_data)

        elif installed_sensors.has_gyro and check_gyro(new_trigger_data, old_trigger_data):
            write_to_database(original_old_trigger_data)
            write_to_database(original_new_trigger_data)
else:
    operations_logger.primary_logger.warning("Write to Database Disabled in Config")
