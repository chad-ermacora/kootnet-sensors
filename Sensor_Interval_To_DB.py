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


Supported Sensor list in Order of its "list" ** Updated: Sept 5th, 2018
    New Sensors are added to the bottom of the list
RP_system
RP_senseHAT
Pimoroni_bh1745
Pimoroni_BME680
Pimoroni_Enviro
Pimoroni_LSM303D
"""
import DB_Interval_Operations
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

sensor_db_location = '/home/sensors/data/SensorIntervalDatabase.sqlite'
sensor_ver_file = "/home/pi/KootNetSensors/installed_sensors.txt"
sql_query_start = "INSERT OR IGNORE INTO Sensor_Data (Time, "
sql_query_values_start = ") VALUES ((CURRENT_TIMESTAMP), "
sql_query_values_end = ")"


def get_installed_sensors():
    # See top of file for sensor_list[] order
    try:
        sensor_list_file = open(sensor_ver_file, 'r')
        sensor_list = sensor_list_file.readlines()
        rp_system = sensor_list[1]
        rp_sense_hat = sensor_list[2]
        pimoroni_bh1745 = sensor_list[3]
        pimoroni_bme680 = sensor_list[4]
        pimoroni_enviro = sensor_list[5]
        pimoroni_lsm303d = sensor_list[6]

        sensors_enabled = rp_system[:1], rp_sense_hat[:1], pimoroni_bh1745[:1], \
            pimoroni_bme680[:1], pimoroni_enviro[:1], pimoroni_lsm303d[:1]

        return sensors_enabled
    except Exception as error:
        logger.error("Unable to open: " + sensor_ver_file + " - " + str(error))


def write_sensor_readings_to_database(var_installed_sensors):
    # See top of file for installed_sensors[] order
    DB_Interval_Operations.create_or_check_db(sensor_db_location)
    sql_query_columns_final = ""
    sql_query_values_final = ""

    count = 0
    if int(var_installed_sensors[0]) == 1:
        rp_database_data = DB_Interval_Operations.get_rp_system_readings()
        sql_query_columns_final = sql_query_columns_final + rp_database_data.sensor_types
        sql_query_values_final = sql_query_values_final + rp_database_data.sensor_readings
        count = count + 1

    if int(var_installed_sensors[1]) == 1:
        if count > 0:
            sql_query_columns_final = sql_query_columns_final + ", "
            sql_query_values_final = sql_query_values_final + ", "

        rp_sense_hat_database_data = DB_Interval_Operations.get_rp_sense_hat_readings()
        sql_query_columns_final = sql_query_columns_final + rp_sense_hat_database_data.sensor_types
        sql_query_values_final = sql_query_values_final + rp_sense_hat_database_data.sensor_readings
        count = count + 1

    if int(var_installed_sensors[2]) == 1:
        if count > 0:
            sql_query_columns_final = sql_query_columns_final + ", "
            sql_query_values_final = sql_query_values_final + ", "

        bh1745_database_data = DB_Interval_Operations.get_pimoroni_bh1745_readings()
        sql_query_columns_final = sql_query_columns_final + bh1745_database_data.sensor_types
        sql_query_values_final = sql_query_values_final + bh1745_database_data.sensor_readings
        count = count + 1

    if int(var_installed_sensors[3]) == 1:
        if count > 0:
            sql_query_columns_final = sql_query_columns_final + ", "
            sql_query_values_final = sql_query_values_final + ", "

        bme680_database_data = DB_Interval_Operations.get_pimoroni_bme680_readings()
        sql_query_columns_final = sql_query_columns_final + bme680_database_data.sensor_types
        sql_query_values_final = sql_query_values_final + bme680_database_data.sensor_readings
        count = count + 1

    if int(var_installed_sensors[4]) == 1:
        if count > 0:
            sql_query_columns_final = sql_query_columns_final + ", "
            sql_query_values_final = sql_query_values_final + ", "

        enviro_database_data = DB_Interval_Operations.get_pimoroni_enviro_readings()
        sql_query_columns_final = sql_query_columns_final + enviro_database_data.sensor_types
        sql_query_values_final = sql_query_values_final + enviro_database_data.sensor_readings
        count = count + 1

    if int(var_installed_sensors[5]) == 1:
        if count > 0:
            sql_query_columns_final = sql_query_columns_final + ", "
            sql_query_values_final = sql_query_values_final + ", "

        lsm303d_database_data = DB_Interval_Operations.get_pimoroni_lsm303d_readings()
        sql_query_columns_final = sql_query_columns_final + lsm303d_database_data.sensor_types
        sql_query_values_final = sql_query_values_final + lsm303d_database_data.sensor_readings

    sql_command = sql_query_start + sql_query_columns_final + sql_query_values_start + \
        sql_query_values_final + sql_query_values_end

    DB_Interval_Operations.write_to_sql_database(sql_command, sensor_db_location)


'''
Start of Program.  Check Sensor Type from file
Then get readings from Said Sensor and write to DB
'''
installed_sensors = get_installed_sensors()
write_sensor_readings_to_database(installed_sensors)
