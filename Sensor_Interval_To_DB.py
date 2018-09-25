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
import Operations_DB
import sensor_modules.Pimoroni_BH1745
import sensor_modules.Pimoroni_BME680
import sensor_modules.Pimoroni_Enviro
import sensor_modules.Linux_OS
import sensor_modules.RaspberryPi_System
import sensor_modules.RaspberryPi_SenseHAT
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

interval_db_location = '/home/pi/KootNetSensors/data/SensorIntervalDatabase.sqlite'

sql_query_start = "INSERT OR IGNORE INTO IntervalData (DateTime, "
sql_query_values_start = ") VALUES ((CURRENT_TIMESTAMP), "
sql_query_values_end = ")"


def write_interval_readings_to_database(installed_sensors_var):
    interval_sql_data = Operations_DB.SensorData()
    interval_sql_command_data = Operations_DB.SQLCommandData()

    interval_sql_command_data.database_location = interval_db_location

    Operations_DB.check_interval_db(interval_db_location)

    count = 0
    if installed_sensors_var.linux_system:
        sensor_os = sensor_modules.Linux_OS.CreateLinuxSystem()
        sensor_system = sensor_modules.RaspberryPi_System.CreateRPSystem()

        tmp_sensor_types = "SensorName, IP, SensorUpTime, SystemTemp"

        tmp_sensor_readings = "'" + str(sensor_os.get_hostname()) + "', '" + \
                              str(sensor_os.get_ip()) + "', '" + \
                              str(sensor_os.get_uptime()) + "', '" + \
                              str(sensor_system.cpu_temperature()) + "'"

        interval_sql_data.sensor_types = interval_sql_data.sensor_types + tmp_sensor_types
        interval_sql_data.sensor_readings = interval_sql_data.sensor_readings + tmp_sensor_readings
        count = count + 1

    if installed_sensors_var.raspberry_pi_sense_hat:
        sensor_access = sensor_modules.RaspberryPi_SenseHAT.CreateRPSystem()

        if count > 0:
            interval_sql_data.sensor_types = interval_sql_data.sensor_types + ", "
            interval_sql_data.sensor_readings = interval_sql_data.sensor_readings + ", "

        tmp_sensor_types = "EnvironmentTemp, Pressure, Humidity"

        tmp_sensor_readings = "'" + str(sensor_access.temperature()) + "', '" + \
                              str(sensor_access.pressure()) + "', '" + \
                              str(sensor_access.humidity()) + "'"

        interval_sql_data.sensor_types = interval_sql_data.sensor_types + tmp_sensor_types
        interval_sql_data.sensor_readings = interval_sql_data.sensor_readings + tmp_sensor_readings
        count = count + 1

    if installed_sensors_var.pimoroni_bh1745:
        sensor_access = sensor_modules.Pimoroni_BH1745.CreateBH1745()

        if count > 0:
            interval_sql_data.sensor_types = interval_sql_data.sensor_types + ", "
            interval_sql_data.sensor_readings = interval_sql_data.sensor_readings + ", "

        tmp_sensor_types = "Lumen, Red, Green, Blue"

        rgb_colour = sensor_access.rgb()
        tmp_sensor_readings = "'" + str(sensor_access.lumen()) + "', '" + \
                              str(rgb_colour[0]) + "', '" + \
                              str(rgb_colour[1]) + "', '" + \
                              str(rgb_colour[2]) + "'"

        interval_sql_data.sensor_types = interval_sql_data.sensor_types + tmp_sensor_types
        interval_sql_data.sensor_readings = interval_sql_data.sensor_readings + tmp_sensor_readings
        count = count + 1

    if installed_sensors_var.pimoroni_bme680:
        sensor_access = sensor_modules.Pimoroni_BME680.CreateBME680()

        if count > 0:
            interval_sql_data.sensor_types = interval_sql_data.sensor_types + ", "
            interval_sql_data.sensor_readings = interval_sql_data.sensor_readings + ", "

        tmp_sensor_types = "EnvironmentTemp, Pressure, Humidity"

        tmp_sensor_readings = "'" + str(sensor_access.temperature()) + "', '" + \
                              str(sensor_access.pressure()) + "', '" + \
                              str(sensor_access.humidity()) + "'"

        interval_sql_data.sensor_types = interval_sql_data.sensor_types + tmp_sensor_types
        interval_sql_data.sensor_readings = interval_sql_data.sensor_readings + tmp_sensor_readings
        count = count + 1

    if installed_sensors_var.pimoroni_enviro:
        sensor_access = sensor_modules.Pimoroni_Enviro.CreateEnviro()

        if count > 0:
            interval_sql_data.sensor_types = interval_sql_data.sensor_types + ", "
            interval_sql_data.sensor_readings = interval_sql_data.sensor_readings + ", "

        tmp_sensor_types = "EnvironmentTemp, Pressure, Lumen, Red, Green, Blue"

        rgb_colour = sensor_access.rgb()
        tmp_sensor_readings = "'" + str(sensor_access.temperature()) + "', '" + \
                              str(sensor_access.pressure()) + "', '" + \
                              str(sensor_access.lumen()) + "', '" + \
                              str(rgb_colour[0]) + "', '" + \
                              str(rgb_colour[1]) + "', '" + \
                              str(rgb_colour[2]) + "'"

        interval_sql_data.sensor_types = interval_sql_data.sensor_types + tmp_sensor_types
        interval_sql_data.sensor_readings = interval_sql_data.sensor_readings + tmp_sensor_readings

    interval_sql_command_data.sql_execute = sql_query_start + interval_sql_data.sensor_types + \
        sql_query_values_start + interval_sql_data.sensor_readings + sql_query_values_end

    Operations_DB.write_to_sql_database(interval_sql_command_data)


'''
Start of Program.  Check Sensor Type from file
Then get readings from Said Sensor and write to DB
'''
installed_sensors = Operations_DB.get_installed_sensors()
write_interval_readings_to_database(installed_sensors)
