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
import sqlite3
import sensor_modules.pimoroni_bh1745 as pimoroni_bh1745
import sensor_modules.pimoroni_BME680 as pimoroni_BME680
import sensor_modules.pimoroni_enviro as pimoroni_enviro
import sensor_modules.pimoroni_LSM303D as pimoroni_LSM303D
import sensor_modules.RP_system as RP_system
import sensor_modules.RP_senseHAT as RP_senseHAT

sensorDB_Location = '/home/sensors/data/SensorIntervalDatabase.sqlite'


def create_or_check_db():
    """
    Connect to DB, and if necessary, create it and or its columns
    Each Column is tried individually to ensure they are ALL checked
    Any new columns will be automatically added to DataBase
    """
    try:
        db_connection = sqlite3.connect(sensorDB_Location)
        db_cursor = db_connection.cursor()
    except Exception as error:
        print("DB Connection Failed: " + str(error))

    try:
        db_cursor.execute('CREATE TABLE {tn} ({nf} {ft})'\
                          .format(tn='Sensor_Data', nf='Time', ft='TEXT'))
        print("Table 'Sensor_Data' - Created")
    except Exception as error:
        print("Table 'Sensor_Data' - " + str(error))

    try:
        db_cursor.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}"\
                          .format(tn='Sensor_Data', cn='hostName', ct='TEXT'))
        print("COLUMN hostName - Created")
    except Exception as error:
        print("COLUMN hostName - " + str(error))

    try:
        db_cursor.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}"\
                          .format(tn='Sensor_Data', cn='uptime', ct='TEXT'))
        print("COLUMN uptime - Created")
    except Exception as error:
        print("COLUMN uptime - " + str(error))

    try:
        db_cursor.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}"\
                          .format(tn='Sensor_Data', cn='ip', ct='TEXT'))
        print("COLUMN ip - Created")
    except Exception as error:
        print("COLUMN ip - " + str(error))

    try:
        db_cursor.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}"\
                          .format(tn='Sensor_Data', cn='cpuTemp', ct='TEXT'))
        print("COLUMN cpuTemp -  Created")
    except Exception as error:
        print("COLUMN cpuTemp - " + str(error))

    try:
        db_cursor.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}"\
                          .format(tn='Sensor_Data', cn='hatTemp', ct='TEXT'))
        print("COLUMN hatTemp - Created")
    except Exception as error:
        print("COLUMN hatTemp - " + str(error))

    try:
        db_cursor.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}"\
                          .format(tn='Sensor_Data', cn='pressure', ct='TEXT'))
        print("COLUMN pressure - Created")
    except Exception as error:
        print("COLUMN pressure - " + str(error))

    try:
        db_cursor.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}"\
                          .format(tn='Sensor_Data', cn='humidity', ct='TEXT'))
        print("COLUMN humidity - Created")
    except Exception as error:
        print("COLUMN humidity - " + str(error))

    try:
        db_cursor.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}"\
                          .format(tn='Sensor_Data', cn='lumen', ct='TEXT'))
        print("COLUMN lumen - Created")
    except Exception as error:
        print("COLUMN lumen - " + str(error))

    try:
        db_cursor.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}"\
                .format(tn='Sensor_Data', cn='red', ct='TEXT'))
        print("COLUMN red - Created")
    except:
        print("COLUMN red - OK")

    try:
        db_cursor.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}"\
                .format(tn='Sensor_Data', cn='green', ct='TEXT'))
        print("COLUMN green - Created")
    except:
        print("COLUMN green - OK")

    try:
        db_cursor.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}"\
                .format(tn='Sensor_Data', cn='blue', ct='TEXT'))
        print("COLUMN blue - Created")
    except:
        print("COLUMN blue - OK")

    try:
        db_cursor.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}"\
                .format(tn='Sensor_Data', cn='mg_X', ct='TEXT'))
        print("COLUMN mg_X - Created")
    except:
        print("COLUMN mg_X - OK")

    try:
        db_cursor.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}"\
                .format(tn='Sensor_Data', cn='mg_Y', ct='TEXT'))
        print("COLUMN mg_Y - Created")
    except:
        print("COLUMN mg_Y - OK")

    try:
        db_cursor.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}"\
                .format(tn='Sensor_Data', cn='mg_Z', ct='TEXT'))
        print("COLUMN mg_Z - Created")
    except:
        print("COLUMN mg_Z - OK")
    
    db_connection.commit()
    db_connection.close()


def get_rp_system_readings():
    sql_database_columns = "hostName, ip, uptime, cpuTemp"
    sql_database_values = "'" + str(RP_system.get_hostname()) + \
                       "', '" + str(RP_system.get_ip()) + \
                       "', '" + str(RP_system.get_uptime()) + \
                       "', '" + str(RP_system.cpu_temperature()) + "'"

    return sql_database_columns, sql_database_values


def get_RP_senseHAT_readings():
    sql_database_columns = "hatTemp, pressure, humidity, mg_X, mg_Y, mg_Z"

    mg_XYZ = RP_senseHAT.magnetometer_xyz()
    sql_database_values = "'" + str(RP_senseHAT.temperature()) + \
                       "', '" + str(RP_senseHAT.pressure()) + \
                       "', '" + str(RP_senseHAT.humidity()) + \
                       "', '" + str(mg_XYZ[0]) + \
                       "', '" + str(mg_XYZ[1]) + \
                       "', '" + str(mg_XYZ[2]) + "'"

    return sql_database_columns, sql_database_values


def get_pimoroni_bh1745_readings():
    sql_database_columns = "lumen, red, green, blue"

    colour_RGB = pimoroni_bh1745.rgb()
    sql_database_values = "'" + str(pimoroni_bh1745.lumen()) + \
                       "', '" + str(colour_RGB[0]) + \
                       "', '" + str(colour_RGB[1]) + \
                       "', '" + str(colour_RGB[2]) + "'"

    return sql_database_columns, sql_database_values


def get_pimoroni_bme680_readings():
    sql_database_columns = "hatTemp, pressure, humidity"
    sql_database_values = "'" + str(pimoroni_BME680.temperature()) + \
                       "', '" + str(pimoroni_BME680.pressure()) + \
                       "', '" + str(pimoroni_BME680.humidity()) + "'"

    return sql_database_columns, sql_database_values


def get_pimoroni_enviro_readings():
    sql_database_columns = "hatTemp, pressure, lumen, red, green, blue, " + \
                        "mg_X, mg_Y, mg_Z"

    colour_rgb = pimoroni_enviro.rgb()
    mg_xyz = pimoroni_enviro.magnetometer_xyz()
    sql_database_values = "'" + str(pimoroni_enviro.temperature()) + \
                          "', '" + str(pimoroni_enviro.pressure()) + \
                          "', '" + str(pimoroni_enviro.lumen()) + \
                          "', '" + str(colour_rgb[0]) + \
                          "', '" + str(colour_rgb[1]) + \
                          "', '" + str(colour_rgb[2]) + \
                          "', '" + str(mg_xyz[0]) + \
                          "', '" + str(mg_xyz[1]) + \
                          "', '" + str(mg_xyz[2]) + "'"

    return sql_database_columns, sql_database_values


def get_pimoroni_lsm303d_readings():
    sql_database_columns = "mg_X, mg_Y, mg_Z"

    mg_xyz = pimoroni_LSM303D.magnetometer_xyz()
    sql_database_values = "'" + str(mg_xyz[0]) + "', '" + str(mg_xyz[1]) + "', '" + str(mg_xyz[2]) + "'"

    return sql_database_columns, sql_database_values


def write_to_sql_database(sql_command):
    print("\nSQL String to execute\n'''\n" + str(sql_command) + "\n'''\n")
    try:
        db_connection = sqlite3.connect(sensorDB_Location)
        db_cursor = db_connection.cursor()
        db_cursor.execute(sql_command)
        db_connection.commit()
        print("Write to DataBase - OK")
        db_connection.close()
    except:
        print("Write to DataBase - Failed")

