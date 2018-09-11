# -*- coding: utf-8 -*-
'''
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
'''
import sensor_modules.pimoroni_VL53L1X as pimoroni_VL53L1X

sql_query_start = "INSERT OR IGNORE INTO Motion_Data (Time, "
sql_query_values_start = ") VALUES ((CURRENT_TIMESTAMP), "
sql_query_values_end = ")"

sensorDB_Location = '/home/sensors/data/SensorTriggerDatabase.sqlite'


def init_sensors_to_db(installed_sensors):
    '''
    Supported Sensor list in Order of its "list" *Needs editing*
    RP_system
    RP_senseHAT
    Pimoroni_bh1745
    Pimoroni_BME680
    Pimoroni_Enviro
    Pimoroni_LSM303D
    Pimoroni_VL53L1X
    '''
    sql_query_columns_final = ""
    sql_query_values_final = ""


def write_all_to_DB(command_line):
    skipdatabase = "Get from config n stuff..."
    if skipdatabase == 1:
        print("Don't forget to add / finish this")

    try:
        conn = sqlite3.connect(sensorDB_Location)
        c = conn.cursor()
        c.execute(command_line)
        conn.commit()
        print("Write to DataBase - OK")
        conn.close()
    except:
        print("Write to DataBase - Failed")


def get_pimoroni_VL53L1X():
    sql_query_columns = ""
    sql_query_values = str() + \
                       ", " + str() + \
                       ", " + str()

    return sql_query_columns, sql_query_values
