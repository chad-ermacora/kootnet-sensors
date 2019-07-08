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
from time import sleep
from threading import Thread
from operations_modules import sqlite_database
from operations_modules import variance_checks
from operations_modules import logger
from operations_modules import program_start_checks
from operations_modules import configuration_main
from operations_modules import software_version
from operations_modules import app_variables
from sensor_modules import sensor_access

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

# Start the HTTP Server for remote access
sensor_http_server_thread = Thread(target=sensor_access.CreateSensorHTTP)
sensor_http_server_thread.daemon = True
sensor_http_server_thread.start()
# Sleep to make sure HTTP server is up first
sleep(4)

logger.primary_logger.info("Sensor Recording Programs Starting ...")


def start_interval_recording():
    """ Starts recording all Interval sensor readings to the SQL database every X amount of time (set in config). """
    logger.primary_logger.info("Interval Recoding Started")
    while True:
        try:
            new_sensor_data = sensor_access.sensors.get_interval_sensor_readings().split(configuration_main.command_data_separator)

            logger.primary_logger.debug(" *** Interval Data: " + str(new_sensor_data[0]) + "\n" +
                                          str(new_sensor_data[1]))
            interval_sql_execute = "INSERT OR IGNORE INTO IntervalData (" + str(new_sensor_data[0]) + ") VALUES (" + str(new_sensor_data[1]) + ")"

            sqlite_database.write_to_sql_database(interval_sql_execute)

            if configuration_main.installed_sensors.has_display and app_variables.sense_hat_show_led_message:
                sensor_access.sensors.display_message("SQL-Int-Rec")
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
        sensor_variance_checks = variance_checks.CreateVarianceRecording(sensor_access.sensors)

        threads = [Thread(target=sensor_variance_checks.check_sensor_uptime),
                   Thread(target=sensor_variance_checks.check_cpu_temperature),
                   Thread(target=sensor_variance_checks.check_env_temperature),
                   Thread(target=sensor_variance_checks.check_pressure),
                   Thread(target=sensor_variance_checks.check_altitude),
                   Thread(target=sensor_variance_checks.check_humidity),
                   Thread(target=sensor_variance_checks.check_distance),
                   Thread(target=sensor_variance_checks.check_lumen),
                   Thread(target=sensor_variance_checks.check_ems),
                   Thread(target=sensor_variance_checks.check_accelerometer_xyz),
                   Thread(target=sensor_variance_checks.check_magnetometer_xyz),
                   Thread(target=sensor_variance_checks.check_gyroscope_xyz)]

        for thread in threads:
            try:
                thread.daemon = True
                thread.start()
            except Exception as trigger_error:
                logger.primary_logger.error("Trigger check failed to start: " + str(trigger_error))

        logger.primary_logger.info("Trigger Recoding Started")
    else:
        logger.primary_logger.warning("Trigger Recording Disabled in Config")

else:
    logger.primary_logger.warning("No sensors set in Installed Sensors")

while True:
    sleep(600)
