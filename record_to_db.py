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

import operations_checks
import operations_config
import operations_db
import operations_logger
import operations_sensors

# Ensure files, database & configurations are OK
operations_checks.run_checks_and_updates()

installed_sensors = operations_config.get_installed_sensors()
current_config = operations_config.get_installed_config()
operations_logger.primary_logger.info("Sensor Recording to SQLite3 DB Started")


def start_interval_recording():
    """ Starts recording all Interval sensor readings to the SQL database every X amount of time (set in config). """
    while True:
        try:
            new_sensor_data = operations_sensors.get_interval_sensor_readings()

            sql_execute = (new_sensor_data.sql_query_start + new_sensor_data.sensor_types +
                           new_sensor_data.sql_query_values_start + new_sensor_data.sensor_readings +
                           new_sensor_data.sql_query_values_end)

            operations_db.write_to_sql_database(sql_execute)

            if installed_sensors.raspberry_pi_sense_hat and operations_config.sense_hat_show_led_message:
                operations_sensors.rp_sense_hat_sensor_access.display_led_message("SQL-Int-Rec")
        except Exception as error:
            operations_logger.primary_logger.error("Interval Failure: " + str(error))

        sleep(current_config.sleep_duration_interval)


def get_readings_set():
    """ Returns 5 'pairs' of Trigger readings in a list, with a sleep delay between each reading (set in config). """
    try:
        readings_set = []

        count = 0
        while count < 5:
            reading_pair = [operations_sensors.get_trigger_sensor_readings()]
            sleep(current_config.sleep_duration_trigger)
            reading_pair.append(operations_sensors.get_trigger_sensor_readings())
            sleep(current_config.sleep_duration_trigger)

            readings_set.append(reading_pair)
            count = count + 1

        return readings_set
    except Exception as error:
        operations_logger.primary_logger.error("Trigger get reading set failed: " + str(error))


def check_xyz_set_against_variance(sensor_readings_set):
    """ Checks provided trigger XYZ readings against their respective variances (set in config). """
    write_to_db = False
    for reading_pair in sensor_readings_set:
        if write_to_db is False:
            readings_old = reading_pair[0].sensor_readings.replace("'", "").split(",")
            readings_new = reading_pair[1].sensor_readings.replace("'", "").split(",")

            if installed_sensors.has_acc and write_to_db is False:
                if float(readings_new[3]) < (float(readings_old[3]) - current_config.acc_variance) or \
                        float(readings_new[3]) > (float(readings_old[3]) + current_config.acc_variance):
                    write_to_db = True
                elif float(readings_new[4]) < (float(readings_old[4]) - current_config.acc_variance) or \
                        float(readings_new[4]) > (float(readings_old[4]) + current_config.acc_variance):
                    write_to_db = True
                elif float(readings_new[5]) < (float(readings_old[5]) - current_config.acc_variance) or \
                        float(readings_new[5]) > (float(readings_old[5]) + current_config.acc_variance):
                    write_to_db = True

            if installed_sensors.has_mag and write_to_db is False:
                if float(readings_new[6]) < (float(readings_old[6]) - current_config.mag_variance) or \
                        float(readings_new[6]) > (float(readings_old[6]) + current_config.mag_variance):
                    write_to_db = True
                elif float(readings_new[7]) < (float(readings_old[7]) - current_config.mag_variance) or \
                        float(readings_new[7]) > (float(readings_old[7]) + current_config.mag_variance):
                    write_to_db = True
                elif float(readings_new[8]) < (float(readings_old[8]) - current_config.mag_variance) or \
                        float(readings_new[8]) > (float(readings_old[8]) + current_config.mag_variance):
                    write_to_db = True

            if installed_sensors.has_gyro and write_to_db is False:
                if float(readings_new[9]) < (float(readings_old[9]) - current_config.gyro_variance) or \
                        float(readings_new[9]) > (float(readings_old[9]) + current_config.gyro_variance):
                    write_to_db = True
                elif float(readings_new[10]) < (float(readings_old[10]) - current_config.gyro_variance) or \
                        float(readings_new[10]) > (float(readings_old[10]) + current_config.gyro_variance):
                    write_to_db = True
                elif float(readings_new[11]) < (float(readings_old[11]) - current_config.gyro_variance) or \
                        float(readings_new[11]) > (float(readings_old[11]) + current_config.gyro_variance):
                    write_to_db = True

    if write_to_db:
        write_trigger_to_database(sensor_readings_set)


def write_trigger_to_database(sensor_readings_set):
    """ Writes the provided trigger reading pairs into the SQL Database. """
    for reading_pair in sensor_readings_set:
        for trigger_data in reading_pair:
            sql_execute = (trigger_data.sql_query_start +
                           trigger_data.sensor_types +
                           trigger_data.sql_query_values_start +
                           trigger_data.sensor_readings +
                           trigger_data.sql_query_values_end)

            operations_db.write_to_sql_database(sql_execute)


if current_config.write_to_db and installed_sensors.no_sensors is False:
    # Start Interval Recording
    interval_recording_thread = Thread(target=start_interval_recording)
    interval_recording_thread.daemon = True
    interval_recording_thread.start()

    # Write first reading to Database, then start monitoring Triggers
    initial_trigger_set = get_readings_set()
    write_trigger_to_database(initial_trigger_set)

    while True:
        new_trigger_set = get_readings_set()
        check_xyz_set_against_variance(new_trigger_set)

else:
    operations_logger.primary_logger.warning("Write to Database Disabled in Config or no sensors set")
    while True:
        sleep(600)
