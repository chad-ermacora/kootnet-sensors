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
import sqlite3
import sensor_modules.pimoroni_bh1745 as pimoroni_bh1745
import sensor_modules.pimoroni_BME680 as pimoroni_BME680
import sensor_modules.pimoroni_enviro as pimoroni_enviro
import sensor_modules.pimoroni_LSM303D as pimoroni_LSM303D
import sensor_modules.RP_system as RP_system
import sensor_modules.RP_senseHAT as RP_senseHAT

sensorDB_Location = '/home/sensors/data/SensorIntervalDatabase.sqlite'


def create_or_check_DB():
    '''
    Connect to DB, and if nessisary, create it and or its columns
    Each Column is tried individually to ensure they are ALL checked
    Any new columns will be automatically added to DataBase
    '''
    try:
        conn = sqlite3.connect(sensorDB_Location)
        c = conn.cursor()
    except:
        print("DB Connection Failed")

    try:
        c.execute('CREATE TABLE {tn} ({nf} {ft})'\
            .format(tn='Sensor_Data', nf='Time', ft='TEXT'))
        print("Table 'Sensor_Data' - Created")
    except:
        print("Table 'Sensor_Data' - OK")

    try:
        c.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}"\
                  .format(tn='Sensor_Data', cn='hostName', ct='TEXT'))
        print("COLUMN hostName - Created")
    except:
        print("COLUMN hostName - OK")

    try:
        c.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}"\
                .format(tn='Sensor_Data', cn='uptime', ct='TEXT'))
        print("COLUMN uptime - Created")
    except:
        print("COLUMN uptime - OK")

    try:
        c.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}"\
                .format(tn='Sensor_Data', cn='ip', ct='TEXT'))
        print("COLUMN ip - Created")
    except:
        print("COLUMN ip - OK")

    try:
        c.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}"\
                .format(tn='Sensor_Data', cn='cpuTemp', ct='TEXT'))
        print("COLUMN cpuTemp -  Created")
    except:
        print("COLUMN cpuTemp - OK")

    try:
        c.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}"\
                .format(tn='Sensor_Data', cn='hatTemp', ct='TEXT'))
        print("COLUMN hatTemp - Created")
    except:
        print("COLUMN hatTemp - OK")

    try:
        c.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}"\
                .format(tn='Sensor_Data', cn='pressure', ct='TEXT'))
        print("COLUMN pressure - Created")
    except:
        print("COLUMN pressure - OK")

    try:
        c.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}"\
                .format(tn='Sensor_Data', cn='humidity', ct='TEXT'))
        print("COLUMN humidity - Created")
    except:
        print("COLUMN humidity - OK")

    try:
        c.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}"\
                .format(tn='Sensor_Data', cn='lumens', ct='TEXT'))
        print("COLUMN lumens - Created")
    except:
        print("COLUMN lumens - OK")

    try:
        c.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}"\
                .format(tn='Sensor_Data', cn='red', ct='TEXT'))
        print("COLUMN red - Created")
    except:
        print("COLUMN red - OK")

    try:
        c.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}"\
                .format(tn='Sensor_Data', cn='green', ct='TEXT'))
        print("COLUMN green - Created")
    except:
        print("COLUMN green - OK")

    try:
        c.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}"\
                .format(tn='Sensor_Data', cn='blue', ct='TEXT'))
        print("COLUMN blue - Created")
    except:
        print("COLUMN blue - OK")

    try:
        c.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}"\
                .format(tn='Sensor_Data', cn='mg_X', ct='TEXT'))
        print("COLUMN mg_X - Created")
    except:
        print("COLUMN mg_X - OK")

    try:
        c.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}"\
                .format(tn='Sensor_Data', cn='mg_Y', ct='TEXT'))
        print("COLUMN mg_Y - Created")
    except:
        print("COLUMN mg_Y - OK")

    try:
        c.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}"\
                .format(tn='Sensor_Data', cn='mg_Z', ct='TEXT'))
        print("COLUMN mg_Z - Created")
    except:
        print("COLUMN mg_Z - OK")
    
    conn.commit()
    conn.close()


def get_RP_system_readings():
    sql_database_columns = "hostName, ip, uptime, cpuTemp"
    sql_database_values = "'" + str(RP_system.get_hostname()) + \
                       "', '" + str(RP_system.get_ip()) + \
                       "', '" + str(RP_system.get_uptime()) + \
                       "', '" + str(RP_system.cpu_temperature()) + "'"

    return sql_database_columns, sql_database_values


def get_RP_senseHAT_readings():
    sql_database_columns = "hatTemp, pressure, humidity, mg_X, mg_Y, mg_Z"

    mg_XYZ = RP_senseHAT.magnetometer_XYZ()
    sql_database_values = "'" + str(RP_senseHAT.temperature()) + \
                       "', '" + str(RP_senseHAT.pressure()) + \
                       "', '" + str(RP_senseHAT.humidity()) + \
                       "', '" + str(mg_XYZ[0]) + \
                       "', '" + str(mg_XYZ[1]) + \
                       "', '" + str(mg_XYZ[2]) + "'"

    return sql_database_columns, sql_database_values


def get_pimoroni_bh1745_readings():
    sql_database_columns = "lumens, red, green, blue"

    colour_RGB = pimoroni_bh1745.RGB()
    sql_database_values = "'" + str(pimoroni_bh1745.lumens()) + \
                       "', '" + str(colour_RGB[0]) + \
                       "', '" + str(colour_RGB[1]) + \
                       "', '" + str(colour_RGB[2]) + "'"

    return sql_database_columns, sql_database_values


def get_pimoroni_BME680_readings():
    sql_database_columns = "hatTemp, pressure, humidity"
    sql_database_values = "'" + str(pimoroni_BME680.temperature()) + \
                       "', '" + str(pimoroni_BME680.pressure()) + \
                       "', '" + str(pimoroni_BME680.humidity()) + "'"

    return sql_database_columns, sql_database_values


def get_pimoroni_Enviro_readings():
    sql_database_columns = "hatTemp, pressure, lumens, red, green, blue, " + \
                        "mg_X, mg_Y, mg_Z"

    colour_RGB = pimoroni_enviro.RGB()
    mg_XYZ = pimoroni_enviro.magnetometer_XYZ()
    sql_database_values = "'" + str(pimoroni_enviro.temperature()) + \
                       "', '" + str(pimoroni_enviro.pressure()) + \
                       "', '" + str(pimoroni_enviro.lumens()) + \
                       "', '" + str(colour_RGB[0]) + \
                       "', '" + str(colour_RGB[1]) + \
                       "', '" + str(colour_RGB[2]) + \
                       "', '" + str(mg_XYZ[0]) + \
                       "', '" + str(mg_XYZ[1]) + \
                       "', '" + str(mg_XYZ[2]) + "'"

    return sql_database_columns, sql_database_values


def get_pimoroni_LSM303D_readings():
    sql_database_columns = "mg_X, mg_Y, mg_Z"

    mg_XYZ = pimoroni_LSM303D.magnetometer_XYZ()
    sql_database_values = "'" + str(mg_XYZ[0]) + \
                       "', '" + str(mg_XYZ[1]) + \
                       "', '" + str(mg_XYZ[2]) + "'"

    return sql_database_columns, sql_database_values


def write_to_sql_database(sql_command):
    print("\nSQL String to execute\n'''\n" + str(sql_command) + "\n'''\n")
#    skipdatabase = "Get from config n stuff..."
#    if skipdatabase == 1:
#        print("Don't forget to add / finish this")
    try:
        conn = sqlite3.connect(sensorDB_Location)
        c = conn.cursor()
        c.execute(sql_command)
        conn.commit()
        print("Write to DataBase - OK")
        conn.close()
    except:
        print("Write to DataBase - Failed")

