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
from threading import Thread
from time import sleep

import operations_modules.operations_db as operations_db
import operations_modules.operations_trigger_checks as operations_trigger_checks
from operations_modules import operations_logger
from operations_modules import operations_pre_checks
from operations_modules import operations_sensors
from operations_modules.operations_config import installed_sensors, current_config, version, get_old_version, \
    sense_hat_show_led_message

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


# Load everything in its own thread and sleep.
if installed_sensors.no_sensors is False:
    if current_config.enable_interval_recording:
        interval_recording_thread = Thread(target=start_interval_recording)
        interval_recording_thread.daemon = True
        interval_recording_thread.start()
    else:
        operations_logger.primary_logger.warning("Interval Recording Disabled in Config")

    if current_config.enable_trigger_recording:
        threads = [Thread(target=operations_trigger_checks.check_accelerometer_xyz),
                   Thread(target=operations_trigger_checks.check_magnetometer_xyz),
                   Thread(target=operations_trigger_checks.check_gyroscope_xyz)]

        for thread in threads:
            try:
                thread.daemon = True
                thread.start()
            except Exception as trigger_error:
                operations_logger.primary_logger.error("Trigger check failed to start: " + str(trigger_error))
    else:
        operations_logger.primary_logger.warning("Trigger Recording Disabled in Config")

else:
    operations_logger.primary_logger.warning("Write to Database Disabled in Config or no sensors set")

while True:
    sleep(600)
