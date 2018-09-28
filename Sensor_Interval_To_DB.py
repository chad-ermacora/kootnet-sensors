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
import Operations_Config
import Operations_DB
import Operations_Sensors
from time import sleep
import logging
from logging.handlers import RotatingFileHandler

logger = logging.getLogger(__name__)

logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(funcName)s:  %(message)s', '%Y-%m-%d %H:%M:%S')

file_handler = RotatingFileHandler('/home/pi/KootNetSensors/logs/Sensors_log.txt', maxBytes=256000, backupCount=5)
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)

interval_db_location = '/home/pi/KootNetSensors/data/SensorIntervalDatabase.sqlite'
sql_query_start = "INSERT OR IGNORE INTO IntervalData (DateTime, "
sql_query_values_start = ") VALUES ((CURRENT_TIMESTAMP), "
sql_query_values_end = ")"

Operations_DB.check_interval_db(interval_db_location)
installed_sensors = Operations_Config.get_installed_sensors()
installed_config = Operations_Config.get_installed_config()


'''
Start of Program.  Check Sensor Type from file
Then get readings from Said Sensor and write to DB
'''
if installed_config.write_to_db == 1:
    while True:

        new_data = Operations_Sensors.get_interval_sensor_readings()
        if len(new_data.sensor_readings) > 0:

            sql_command_data = Operations_DB.CreateSQLCommandData()
            sql_command_data.database_location = interval_db_location

            sql_command_data.sql_execute = sql_query_start + new_data.sensor_types + \
                sql_query_values_start + new_data.sensor_readings + sql_query_values_end

            Operations_DB.write_to_sql_database(sql_command_data)
        else:
            logger.warning("No Sensor Data Provided - Skipping Interval Database Write")
        sleep(installed_config.sleep_duration_interval)
else:
    logger.warning("Database Write Disabled in Config - Skipping Interval Database Write")
