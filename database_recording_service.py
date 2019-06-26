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
import requests
from time import sleep
from threading import Thread
from operations_modules import sqlite_database
from operations_modules import variance_checks
from operations_modules import logger
from operations_modules import program_start_checks
from operations_modules import configuration_main
from operations_modules import software_version
from operations_modules import app_variables

# Ensure files, database & configurations are OK
program_start_checks.set_file_permissions()
program_start_checks.check_database_structure()

if software_version.old_version != software_version.version:
    logger.primary_logger.info("Checking files and configuration after upgrade")
    os.system("systemctl start SensorUpgradeChecks")
    # Sleep before loading anything due to needed updates
    # The update service will automatically restart this app when it's done
    while True:
        sleep(10)

# Ensure http_server.py is up before starting
sleep(10)
logger.primary_logger.info("Sensor Recording to SQLite3 DB Started")


def get_interval_sensor_data():
    """ Returns requested sensor data (based on the provided command data). """
    url = "http://127.0.0.1:10065/GetIntervalSensorReadings"
    command_data_separator = "[new_data_section]"

    try:
        tmp_return_data = requests.get(url=url)
        logger.primary_logger.debug("* Sensor Interval Data Retrieval OK")
        return_data = tmp_return_data.text.split(command_data_separator)
        sensor_types = str(return_data[0])
        sensor_readings = str(return_data[1])
    except Exception as error:
        sensor_types = "Sensor Offline"
        sensor_readings = "Sensor Offline"
        logger.primary_logger.error("* Sensor Interval Data Retrieval Failed - " + str(error))
    return [sensor_types, sensor_readings]


def display_text_on_sensor(text_message):
    """ Returns requested sensor data (based on the provided command data). """
    url = "http://127.0.0.1:10065/DisplayText"

    try:
        requests.put(url=url, data={'command_data': text_message})
        logger.primary_logger.debug("* Sent Command: " + url + " to Sensor OK")
    except Exception as error:
        logger.primary_logger.error("* Sensor Command Failed: " + url + " - " + str(error))


def start_interval_recording():
    """ Starts recording all Interval sensor readings to the SQL database every X amount of time (set in config). """
    while True:
        try:
            new_sensor_data = get_interval_sensor_data()
            # new_sensor_data = sensors.get_interval_sensor_readings()

            logger.primary_logger.debug(" *** Interval Data: " + str(new_sensor_data[0]) + "\n" +
                                          str(new_sensor_data[1]))
            interval_sql_execute = "INSERT OR IGNORE INTO IntervalData (" + str(new_sensor_data[0]) + ") VALUES (" + str(new_sensor_data[1]) + ")"

            sqlite_database.write_to_sql_database(interval_sql_execute)

            if configuration_main.installed_sensors.raspberry_pi_sense_hat and app_variables.sense_hat_show_led_message:
                display_text_on_sensor("SQL-Int-Rec")
        except Exception as error:
            logger.primary_logger.error("Interval Failure: " + str(error))

        sleep(configuration_main.current_config.sleep_duration_interval)


# Load everything in its own thread and sleep.
if configuration_main.installed_sensors.no_sensors is False:
    if configuration_main.current_config.enable_interval_recording:
        interval_recording_thread = Thread(target=start_interval_recording)
        interval_recording_thread.daemon = True
        interval_recording_thread.start()
    else:
        logger.primary_logger.warning("Interval Recording Disabled in Config")

    if configuration_main.current_config.enable_trigger_recording:
        threads = [Thread(target=variance_checks.check_sensor_uptime),
                   Thread(target=variance_checks.check_cpu_temperature),
                   Thread(target=variance_checks.check_env_temperature),
                   Thread(target=variance_checks.check_pressure),
                   Thread(target=variance_checks.check_humidity),
                   Thread(target=variance_checks.check_lumen),
                   Thread(target=variance_checks.check_ems),
                   Thread(target=variance_checks.check_accelerometer_xyz),
                   Thread(target=variance_checks.check_magnetometer_xyz),
                   Thread(target=variance_checks.check_gyroscope_xyz)]

        for thread in threads:
            try:
                thread.daemon = True
                thread.start()
            except Exception as trigger_error:
                logger.primary_logger.error("Trigger check failed to start: " + str(trigger_error))
    else:
        logger.primary_logger.warning("Trigger Recording Disabled in Config")

else:
    logger.primary_logger.warning("No sensors set in Installed Sensors")

while True:
    sleep(600)
