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


def write_sensor_readings_to_database(installed_sensors_var):
    Operations_DB.check_interval_db(interval_db_location)
    sql_query_columns_final = ""
    sql_query_values_final = ""

    count = 0
    if installed_sensors_var.rp_system:
        rp_database_data = Operations_Interval.get_rp_system_readings()
        sql_query_columns_final = sql_query_columns_final + rp_database_data.sensor_types
        sql_query_values_final = sql_query_values_final + rp_database_data.sensor_readings
        count = count + 1

    if installed_sensors_var.rp_sense_hat:
        if count > 0:
            sql_query_columns_final = sql_query_columns_final + ", "
            sql_query_values_final = sql_query_values_final + ", "

        rp_sense_hat_database_data = Operations_Interval.get_rp_sense_hat_readings()
        sql_query_columns_final = sql_query_columns_final + rp_sense_hat_database_data.sensor_types
        sql_query_values_final = sql_query_values_final + rp_sense_hat_database_data.sensor_readings
        count = count + 1

    if installed_sensors_var.pimoroni_bh1745:
        if count > 0:
            sql_query_columns_final = sql_query_columns_final + ", "
            sql_query_values_final = sql_query_values_final + ", "

        bh1745_database_data = Operations_Interval.get_pimoroni_bh1745_readings()
        sql_query_columns_final = sql_query_columns_final + bh1745_database_data.sensor_types
        sql_query_values_final = sql_query_values_final + bh1745_database_data.sensor_readings
        count = count + 1

    if installed_sensors_var.pimoroni_bme680:
        if count > 0:
            sql_query_columns_final = sql_query_columns_final + ", "
            sql_query_values_final = sql_query_values_final + ", "

        bme680_database_data = Operations_Interval.get_pimoroni_bme680_readings()
        sql_query_columns_final = sql_query_columns_final + bme680_database_data.sensor_types
        sql_query_values_final = sql_query_values_final + bme680_database_data.sensor_readings
        count = count + 1

    if installed_sensors_var.pimoroni_enviro:
        if count > 0:
            sql_query_columns_final = sql_query_columns_final + ", "
            sql_query_values_final = sql_query_values_final + ", "

        enviro_database_data = Operations_Interval.get_pimoroni_enviro_readings()
        sql_query_columns_final = sql_query_columns_final + enviro_database_data.sensor_types
        sql_query_values_final = sql_query_values_final + enviro_database_data.sensor_readings
        count = count + 1

    if installed_sensors_var.pimoroni_lsm303d:
        if count > 0:
            sql_query_columns_final = sql_query_columns_final + ", "
            sql_query_values_final = sql_query_values_final + ", "

        lsm303d_database_data = Operations_Interval.get_pimoroni_lsm303d_readings()
        sql_query_columns_final = sql_query_columns_final + lsm303d_database_data.sensor_types
        sql_query_values_final = sql_query_values_final + lsm303d_database_data.sensor_readings

    sql_command = sql_query_start + sql_query_columns_final + sql_query_values_start + \
        sql_query_values_final + sql_query_values_end

    Operations_DB.write_to_sql_database(sql_command, interval_db_location)


'''
Start of Program.  Check Sensor Type from file
Then get readings from Said Sensor and write to DB
'''
installed_sensors = Operations_DB.get_installed_sensors()
write_sensor_readings_to_database(installed_sensors)
