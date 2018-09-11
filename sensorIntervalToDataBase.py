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


Supported Sensor list in Order of its "list" ** Updated: Sept 5th, 2018
    New Sensors are added to the bottom of the list
RP_system
RP_senseHAT
Pimoroni_bh1745
Pimoroni_BME680
Pimoroni_Enviro
Pimoroni_LSM303D
'''
import DB_Interval_Operations

sensor_ver_file = "/home/pi/config/sensor_type.txt"
sql_query_start = "INSERT OR IGNORE INTO Sensor_Data (Time, "
sql_query_values_start = ") VALUES ((CURRENT_TIMESTAMP), "
sql_query_values_end = ")"


def get_installed_sensors():
    # See top of file for sensor_list[] order
    try:
        sensor_list_file = open(sensor_ver_file, 'r')
        sensor_list = sensor_list_file.readlines()
        RP_system = sensor_list[1]
        RP_senseHAT = sensor_list[2]
        Pimoroni_bh1745 = sensor_list[3]
        Pimoroni_BME680 = sensor_list[4]
        Pimoroni_Enviro = sensor_list[5]
        Pimoroni_LSM303D = sensor_list[6]

        sensors_enabled = RP_system[:1], \
                          RP_senseHAT[:1], \
                          Pimoroni_bh1745[:1], \
                          Pimoroni_BME680[:1], \
                          Pimoroni_Enviro[:1], \
                          Pimoroni_LSM303D[:1]

        return sensors_enabled
    except:
        print("\nChecking Installed Sensors File Failed\nUnable to open: " + \
              sensor_ver_file)


def write_sensor_readings_to_database(installed_sensors):
    # See top of file for installed_sensors[] order
    DB_Interval_Operations.create_or_check_DB()
    sql_query_columns_final = ""
    sql_query_values_final = ""

    count = 0
    if int(installed_sensors[0]) == 1:
        print("\nRP_system Installed")
        sql_query_columns , sql_query_values = \
            DB_Interval_Operations.get_RP_system_readings()
        sql_query_columns_final = sql_query_columns_final + sql_query_columns
        sql_query_values_final = sql_query_values_final + sql_query_values
        count = count + 1

    if int(installed_sensors[1]) == 1:
        print("\nRP_senseHAT Installed")
        if count > 0:
            sql_query_columns_final = sql_query_columns_final + ", "
            sql_query_values_final = sql_query_values_final + ", "

        sql_query_columns , sql_query_values = DB_Interval_Operations.get_RP_senseHAT_readings()
        sql_query_columns_final = sql_query_columns_final + sql_query_columns
        sql_query_values_final = sql_query_values_final + sql_query_values
        count = count + 1

    if int(installed_sensors[2]) == 1:
        print("\nPimoroni_bh1745 Installed")
        if count > 0:
            sql_query_columns_final = sql_query_columns_final + ", "
            sql_query_values_final = sql_query_values_final + ", "

        sql_query_columns , sql_query_values = DB_Interval_Operations.get_pimoroni_bh1745_readings()
        sql_query_columns_final = sql_query_columns_final + sql_query_columns
        sql_query_values_final = sql_query_values_final + sql_query_values
        count = count + 1

    if int(installed_sensors[3]) == 1:
        print("\nPimoroni_BME680 Installed")
        if count > 0:
            sql_query_columns_final = sql_query_columns_final + ", "
            sql_query_values_final = sql_query_values_final + ", "

        sql_query_columns , sql_query_values = DB_Interval_Operations.get_pimoroni_BME680_readings()
        sql_query_columns_final = sql_query_columns_final + sql_query_columns
        sql_query_values_final = sql_query_values_final + sql_query_values
        count = count + 1

    if int(installed_sensors[4]) == 1:
        print("\nPimoroni_Enviro Installed")
        if count > 0:
            sql_query_columns_final = sql_query_columns_final + ", "
            sql_query_values_final = sql_query_values_final + ", "

        sql_query_columns , sql_query_values = DB_Interval_Operations.get_pimoroni_Enviro_readings()
        sql_query_columns_final = sql_query_columns_final + sql_query_columns
        sql_query_values_final = sql_query_values_final + sql_query_values
        count = count + 1

    if int(installed_sensors[5]) == 1:
        print("\nPimoroni_LSM303D Installed")
        if count > 0:
            sql_query_columns_final = sql_query_columns_final + ", "
            sql_query_values_final = sql_query_values_final + ", "

        sql_query_columns , sql_query_values = DB_Interval_Operations.get_pimoroni_LSM303D_readings()
        sql_query_columns_final = sql_query_columns_final + sql_query_columns
        sql_query_values_final = sql_query_values_final + sql_query_values
        count = count + 1

    sql_command = sql_query_start + sql_query_columns_final + \
                       sql_query_values_start + sql_query_values_final + \
                       sql_query_values_end

    DB_Interval_Operations.write_to_sql_database(sql_command)


'''
Start of Program.  Check Sensor Type from file
Then get readings from Said Sensor and write to DB
'''

installed_sensors = get_installed_sensors()
write_sensor_readings_to_database(installed_sensors)

