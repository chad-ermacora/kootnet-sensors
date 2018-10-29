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
import operations_config
import operations_db
import operations_sensors
from time import sleep
import operations_logger

installed_sensors = operations_config.get_installed_sensors()
installed_config = operations_config.get_installed_config()
operations_db.check_database_interval()

operations_logger.primary_logger.info("Sensor Recording by Interval Started")


'''
Start of Program.  Check Sensor Type from file
Then get readings from Said Sensor and write to DB
'''
# Write installed sensors back to file, to add new sensor support when program gets them
operations_config.write_installed_sensors_to_file(installed_sensors)
operations_config.write_config_to_file(installed_config)

if installed_config.write_to_db == 1:
    first_sensor_data = operations_sensors.get_interval_sensor_readings()
    print("Sensor Types: " + first_sensor_data.sensor_types + "\n\n" +
          "Sensor Readings: " + first_sensor_data.sensor_readings + "\n")

    while True:
        new_sensor_data = operations_sensors.get_interval_sensor_readings()

        if len(new_sensor_data.sensor_readings) > 0:
            sql_command_data = operations_db.CreateSQLCommandData()

            sql_command_data.database_location = new_sensor_data.database_location
            sql_command_data.sql_execute = new_sensor_data.sql_query_start + \
                new_sensor_data.sensor_types + new_sensor_data.sql_query_values_start + \
                new_sensor_data.sensor_readings + new_sensor_data.sql_query_values_end

            operations_db.write_to_sql_database(sql_command_data)
        else:
            operations_logger.primary_logger.warning("No Sensor Data Provided - Skipping Interval Database Write")
        sleep(installed_config.sleep_duration_interval)
else:
    operations_logger.primary_logger.warning("Database Write Disabled in Config - Skipping Interval Database Write")
