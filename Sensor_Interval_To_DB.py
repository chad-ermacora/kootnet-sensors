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
import Operations_Interval
import Operations_DB
import logging
from logging.handlers import RotatingFileHandler

logger = logging.getLogger(__name__)

logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(funcName)s:  %(message)s', '%Y-%m-%d %H:%M:%S')

file_handler = RotatingFileHandler('/home/pi/KootNetSensors/logs/Interval_DB_log.txt', maxBytes=256000, backupCount=5)
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)

interval_db_location = '/home/sensors/data/SensorIntervalDatabase.sqlite'
sql_query_start = "INSERT OR IGNORE INTO IntervalData (DateTime, "
sql_query_values_start = ") VALUES ((CURRENT_TIMESTAMP), "
sql_query_values_end = ")"


def write_interval_readings_to_database(installed_sensors_var):
    interval_sql_data = Operations_DB.SensorData()
    interval_sql_command_data = Operations_DB.SQLCommandData()

    interval_sql_command_data.database_location = interval_db_location

    Operations_DB.check_interval_db(interval_db_location)

    count = 0
    if installed_sensors_var.rp_system:
        rp_sensor_data = Operations_Interval.get_rp_system_readings()
        interval_sql_data.sensor_types = interval_sql_data.sensor_types + rp_sensor_data.sensor_types
        interval_sql_data.sensor_readings = interval_sql_data.sensor_readings + rp_sensor_data.sensor_readings
        count = count + 1

    if installed_sensors_var.rp_sense_hat:
        if count > 0:
            interval_sql_data.sensor_types = interval_sql_data.sensor_types + ", "
            interval_sql_data.sensor_readings = interval_sql_data.sensor_readings + ", "

        rp_sense_hat_data = Operations_Interval.get_rp_sense_hat_readings()
        interval_sql_data.sensor_types = interval_sql_data.sensor_types + rp_sense_hat_data.sensor_types
        interval_sql_data.sensor_readings = interval_sql_data.sensor_readings + rp_sense_hat_data.sensor_readings
        count = count + 1

    if installed_sensors_var.pimoroni_bh1745:
        if count > 0:
            interval_sql_data.sensor_types = interval_sql_data.sensor_types + ", "
            interval_sql_data.sensor_readings = interval_sql_data.sensor_readings + ", "

        bh1745_data = Operations_Interval.get_pimoroni_bh1745_readings()
        interval_sql_data.sensor_types = interval_sql_data.sensor_types + bh1745_data.sensor_types
        interval_sql_data.sensor_readings = interval_sql_data.sensor_readings + bh1745_data.sensor_readings
        count = count + 1

    if installed_sensors_var.pimoroni_bme680:
        if count > 0:
            interval_sql_data.sensor_types = interval_sql_data.sensor_types + ", "
            interval_sql_data.sensor_readings = interval_sql_data.sensor_readings + ", "

        bme680_data = Operations_Interval.get_pimoroni_bme680_readings()
        interval_sql_data.sensor_types = interval_sql_data.sensor_types + bme680_data.sensor_types
        interval_sql_data.sensor_readings = interval_sql_data.sensor_readings + bme680_data.sensor_readings
        count = count + 1

    if installed_sensors_var.pimoroni_enviro:
        if count > 0:
            interval_sql_data.sensor_types = interval_sql_data.sensor_types + ", "
            interval_sql_data.sensor_readings = interval_sql_data.sensor_readings + ", "

        enviro_data = Operations_Interval.get_pimoroni_enviro_readings()
        interval_sql_data.sensor_types = interval_sql_data.sensor_types + enviro_data.sensor_types
        interval_sql_data.sensor_readings = interval_sql_data.sensor_readings + enviro_data.sensor_readings

    interval_sql_command_data.sql_execute = sql_query_start + interval_sql_data.sensor_types + \
        sql_query_values_start + interval_sql_data.sensor_readings + sql_query_values_end

    Operations_DB.write_to_sql_database(interval_sql_command_data)


'''
Start of Program.  Check Sensor Type from file
Then get readings from Said Sensor and write to DB
'''
installed_sensors = Operations_DB.get_installed_sensors()
write_interval_readings_to_database(installed_sensors)
