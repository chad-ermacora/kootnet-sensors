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
from operations_modules import logger
from operations_modules import configuration_main
from operations_modules import sqlite_database


class CreateIntervalRecording:
    logger.primary_logger.debug("Created Interval Recording Server")

    def __init__(self, sensor_access):
        self.sensor_access = sensor_access
        self.start_interval_recording()

    def start_interval_recording(self):
        """ Starts recording all Interval sensor readings to the SQL database every X amount of time (set in config). """
        logger.primary_logger.info("Interval Recoding Started")
        while True:
            try:
                new_sensor_data = self.sensor_access.get_interval_sensor_readings().split(
                    configuration_main.command_data_separator)

                logger.primary_logger.debug(" *** Interval Data: " + str(new_sensor_data[0]) + "\n" +
                                            str(new_sensor_data[1]))
                interval_sql_execute = "INSERT OR IGNORE INTO IntervalData (" + str(
                    new_sensor_data[0]) + ") VALUES (" + str(new_sensor_data[1]) + ")"

                sqlite_database.write_to_sql_database(interval_sql_execute)
            except Exception as error:
                logger.primary_logger.error("Interval Failure: " + str(error))

            sleep(configuration_main.current_config.sleep_duration_interval)
